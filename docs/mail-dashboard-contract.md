# Mail Dashboard Contract

Status: CP0 agreed; CP1, CP2, and CP3 implemented
Schema version: 1

## Purpose and scope

This contract defines the mail snapshot that Mail Platform will send to AD Automation and the dashboard metrics AD Automation will calculate from the snapshots it has stored.

The dashboard snapshot is separate from workflow jobs and from `mail_request_audits`. It represents mail records persisted by Mail Platform, including records whose mailbox domain does not create a workflow request.

The contract and metric definitions below are agreed in CP0. Implementation status for CP1 through CP3 is recorded at the end of this document. The dashboard UI is not implemented yet.

## Mail snapshot payload

Mail Platform sends one current snapshot per mail record when the record is first persisted and when its processing state changes. Delivery is service-to-service and will use the existing integration-token mechanism. AD Automation upserts the snapshot; retrying delivery must not create another mail.

```json
{
  "schema_version": 1,
  "source_system": "mail-platform",
  "mailbox": "shared-mailbox@example.com",
  "source_mail_id": "<opaque-stable-message-id>",
  "subject": "Example subject",
  "received_at": "2026-10-22T14:30:00Z",
  "processing_state": "RETRY_PENDING",
  "state_changed_at": "2026-10-22T14:31:12Z"
}
```

| Field | Contract |
|---|---|
| `schema_version` | Integer contract version. Initial value is `1`. |
| `source_system` | Stable source identifier; `mail-platform` for this integration. |
| `mailbox` | Shared mailbox address, normalized to lowercase for identity and filtering. |
| `source_mail_id` | Stable opaque identifier mapped from `MailRecord.message_id`. Treat as an identifier, not as display text. |
| `subject` | Subject for the dashboard row. Render as plain text; never treat as HTML. |
| `received_at` | Original mail receive time in UTC RFC 3339 format. May be `null` if unavailable; such a record is excluded from the 24-hour count but remains in the total count. |
| `processing_state` | Current state, using the exact values listed below. |
| `state_changed_at` | UTC RFC 3339 time when the current processing state was entered. Set on initial persistence and update only when the state changes. |

The idempotency key is the tuple `(source_system, mailbox, source_mail_id)`. A repeated snapshot with the same key updates the stored record. The payload does not contain the email body, recipients, credentials, request payload, or detailed processing trace.

## Processing states

The initial contract recognizes these states:

- `PENDING`
- `PROCESSING`
- `RETRY_PENDING`
- `SUCCESS`
- `BUSINESS_REJECTED`
- `INVALID_REQUEST`
- `UNSUPPORTED_REQUEST`
- `RETRY_EXHAUSTED`

An unrecognized state or unsupported schema version is rejected rather than silently mapped to another state. Adding states or changing their meaning requires a contract revision.

## Metric definitions

AD Automation calculates all dashboard counts from the latest stored snapshot per idempotency key. It does not add counts received from Mail Platform.

### Total mail

Count all distinct mail snapshots stored in AD Automation for the configured Mail Platform mailboxes, regardless of processing state or receive date.

### Mail received in the last 24 hours

Count distinct snapshots whose `received_at` is within the rolling interval `[current UTC time - 24 hours, current UTC time]`. This uses original receive time, not persistence time, poll time, or state-change time. A missing or invalid receive time is not included in this metric.

### Successful mail

Count snapshots whose current `processing_state` is `SUCCESS`.

### Failed mail

Count snapshots whose current `processing_state` is one of:

- `RETRY_PENDING`
- `BUSINESS_REJECTED`
- `INVALID_REQUEST`
- `UNSUPPORTED_REQUEST`
- `RETRY_EXHAUSTED`

`RETRY_PENDING` is included because the mail has failed an attempt and needs monitoring while awaiting retry. If a later retry changes the current state to `SUCCESS`, the mail is no longer counted as failed.

`PENDING` and `PROCESSING` are neither successful nor failed. Therefore, successful plus failed counts may be less than total mail.

### Five most recent failed mail

Return at most five distinct snapshots currently in a failed state, ordered by `state_changed_at` descending. Break timestamp ties by `received_at` descending and then by the idempotency key for deterministic ordering.

Each row displays only mailbox, receive time, subject, and current processing state. Detailed error investigation is outside this dashboard contract and remains deferred to the later audit/trace work.

## Consistency and delivery expectations

- A snapshot is sent only after the corresponding Mail Platform persistence or state update has committed.
- AD Automation is the dashboard's read model; Mail Platform remains the processing source of truth.
- Repeated delivery is safe because AD Automation upserts by the idempotency key.
- Mail Platform stores the latest pending snapshot per mail in a durable outbox and retries delivery failures independently from mail processing state.
- Successfully delivered outbox entries are deleted after 15 days. Pending or failed entries are retained until delivery succeeds.
- Initial dashboard population must synchronize existing Mail Platform records. Otherwise, totals represent only records delivered after rollout.
- Mail records that fail before Mail Platform creates a persistent mail record are outside these dashboard counts.

## CP1 implementation in AD Automation

CP1 implements the authenticated receive-and-store side of this contract:

- Endpoint: `POST /api/v1/service/mail-dashboard/snapshots`.
- Authentication and authorization: integration JWT via `require_integration_endpoint("mail_dashboard_snapshot")`. The `mail-platform` integration is granted this capability in the integration registry.
- Storage: the separate `mail_dashboard_snapshots` table, represented by `app/mail_dashboard/record.py`. The composite primary key is `(source_system, mailbox, source_mail_id)`.
- Validation: schema version, source system, state enum, timezone-aware timestamps, non-empty identifiers, and no undeclared payload fields.
- Idempotency and ordering: an identical snapshot returns `unchanged`; a newer state timestamp updates the record; an older snapshot returns `stale`; conflicting state transitions return HTTP 409.
- Refresh: `monitor_refresh` is published only after a committed create/update. Unchanged and stale snapshots do not publish a refresh.
- Table creation: the table is ensured at application startup and its model is registered with the existing database model metadata.

CP1 did not include the dashboard read/KPI API, Mail Platform delivery, synchronization of existing Mail Platform records, or dashboard UI. Mail Platform delivery was implemented separately in CP2; the read/KPI API was implemented in CP3. Initial synchronization and dashboard UI remain later CPs.

## CP2 implementation in Mail Platform

CP2 implements snapshot delivery from Mail Platform to the CP1 endpoint:

- New code is grouped under `dashboard_to_ad/`; existing modules remain in their original locations.
- `database/schema.py` creates the outbox table and adds/migrates `mail_records.state_changed_time`. Existing records initialize this field from `created_time`.
- `database/mail_record_repository.py` inserts or updates the mail record and its latest outbox snapshot in the same SQLite transaction. Repeated state updates do not create new snapshots when the state has not changed.
- `dashboard_to_ad/outbox_repository.py` stores one latest snapshot per mail, tracks delivery attempts and errors, applies bounded exponential retry delays, and deletes only delivered records older than 15 days.
- Retry starts at 30 seconds and doubles up to a one-hour cap; each flush processes up to 100 pending records.
- `dashboard_to_ad/snapshot_sender.py` and `builder/ad_automation_client.py` send snapshots to `POST /api/v1/service/mail-dashboard/snapshots` using the existing integration JWT flow.
- `dashboard_to_ad/sync_service.py` flushes pending snapshots and logs failures without changing the mail's business processing state.
- `resolver/mail_poller.py` flushes pending entries before and after a polling pass. This also retries snapshots for already-terminal mail records; Graph's rolling 24-hour retrieval and IMAP-specific `mark_seen()` behavior are unchanged.
- `main.py` initializes/migrates the database before starting polling schedulers.

The initial outbox is created for records persisted after CP2 is deployed. Historical Mail Platform records are not backfilled by CP2; initial synchronization remains a separate rollout step. CP2 does not implement the AD read/KPI API or dashboard UI.

## CP3 implementation in AD Automation

CP3 implements the authenticated dashboard read API:

- Endpoint: `GET /api/v1/service/mail-dashboard/summary`.
- Authentication and authorization: user JWT with membership in the `ad_login` group. The integration token/secret is not exposed to the browser.
- The endpoint returns `total_mail`, `mail_last_24h`, `failed_mail`, `successful_mail`, and up to five `recent_failed_mail` rows.
- All aggregate counts are calculated from the current Mail Platform snapshots in AD Automation. The 24-hour interval is inclusive at both ends and uses UTC `received_at`; missing receive times are excluded.
- Recent failures use the agreed failed-state set and sort by `state_changed_at` descending, then `received_at` descending, then the snapshot key for deterministic ties.
- Each recent-failure row contains only mailbox, receive time, subject, and current processing state. No body or request payload is returned.
- Raw JWT and decoded claim debug output was removed from the shared user-token dependency so credentials and claim data are not written to application logs.

CP3 does not backfill historical Mail Platform records. The dashboard calls this API with the user's JWT; internal AD monitor refresh continues to serve as the reload hint.

## CP4 implementation in AD Automation dashboard

CP4 adds the mail summary to the existing Monitor dashboard page:

- `Onboard_UI_React/src/pages/MonitorDashboard.jsx` loads the mail summary from `GET /api/v1/service/mail-dashboard/summary` with the existing authenticated `axiosClient`.
- The page displays the four agreed mail KPIs and up to five recent failures below the existing AD Runtime and Workflow Runtime sections. Mail subjects are rendered as text, with no body or request payload.
- Initial load and the existing `monitor_refresh` event both reload the AD Runtime, Workflow Runtime, and Mail Summary data. CP4 adds no mail-specific event stream, timer, or refresh mechanism.
- The mail section reuses existing Monitor card, panel, and failed-status styles in `Onboard_UI_React/src/pages/MonitorDashboard.css`.
- A Mail API load failure is shown within the mail section and does not prevent the AD Runtime or Workflow Runtime sections from loading.

CP4 does not change the backend API, monitor event bus, dashboard route, or Mail Platform delivery flow. Historical Mail Platform records are still not backfilled; counts reflect snapshots received and stored by AD Automation.
