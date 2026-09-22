import "./QuayXePage.css";
import {
    enableUser,
    getAccessSnapshot,
    moveUser,
    restoreGroups
} from "../services/adToolApi";
import React, {
    useState
} from "react";

export default function QuayXePage() {
    const [samAccountName, setSamAccountName] =
        useState("");

    const [snapshotData, setSnapshotData] =
        useState(null);

    const [loading, setLoading] =
        useState(false);

    const [restoringOu, setRestoringOu] =
        useState(false);

    const [restoringUser, setRestoringUser] =
        useState(false);

    const [restoringGroups, setRestoringGroups] =
        useState(false);

    const [restoreLocked, setRestoreLocked] =
        useState(false);

    const [restoreResult, setRestoreResult] =
        useState({});

    const handleLoadSnapshot = async () => {
        try {
            setLoading(true);
            setRestoreLocked(true);
            setRestoreResult({});

            const response = await getAccessSnapshot(
                samAccountName
            );

            setSnapshotData(response);
            setRestoreLocked(false);
        } catch (error) {
            console.error(error);
            alert("Không tìm thấy snapshot.");
        } finally {
            setLoading(false);
        }
    };

    const handleRestoreOu = async () => {
        if (!snapshotData?.ou_dn) {
            return;
        }

        try {
            setRestoringOu(true);

            const response = await moveUser({
                sam_account_name:
                    snapshotData.sam_account_name,
                target_ou_dn: snapshotData.ou_dn
            });
            const succeeded = response?.success === true;

            setRestoreResult((current) => ({
                ...current,
                ou: {
                    success: succeeded,
                    message: succeeded
                        ? "Khôi phục OU thành công."
                        : "Khôi phục OU thất bại."
                }
            }));
            setRestoringOu(false);
        } catch (error) {
            console.error(error);
            setRestoreResult((current) => ({
                ...current,
                ou: {
                    success: false,
                    message: "Khôi phục OU thất bại."
                }
            }));
            setRestoringOu(false);
        } finally {
            setRestoreLocked(true);
        }
    };

    const handleEnableUser = async () => {
        if (!snapshotData?.sam_account_name) {
            return;
        }

        try {
            setRestoringUser(true);

            const response = await enableUser({
                sam_account_name:
                    snapshotData.sam_account_name
            });
            const succeeded = response?.success === true;

            if (succeeded) {
                setSnapshotData((current) => ({
                    ...current,
                    user_status: "enabled"
                }));
            }

            setRestoreResult((current) => ({
                ...current,
                user: {
                    success: succeeded,
                    message: succeeded
                        ? "Enable user thành công."
                        : "Enable user thất bại."
                }
            }));
            setRestoringUser(false);
        } catch (error) {
            console.error(error);
            setRestoreResult((current) => ({
                ...current,
                user: {
                    success: false,
                    message: "Enable user thất bại."
                }
            }));
            setRestoringUser(false);
        } finally {
            setRestoreLocked(true);
        }
    };

    const handleRestoreGroups = async () => {
        const groupDns = snapshotData?.groups || [];

        if (groupDns.length === 0) {
            return;
        }

        try {
            setRestoringGroups(true);

            const response = await restoreGroups({
                sam_account_name:
                    snapshotData.sam_account_name,
                group_dns: groupDns
            });

            const failedCount =
                response.failed_groups?.length || 0;
            const restoredCount =
                response.restored_groups?.length || 0;

            setRestoreResult((current) => ({
                ...current,
                groups: {
                    success: failedCount === 0,
                    message: failedCount === 0
                        ? `Đã khôi phục ${groupDns.length} group.`
                        : `Đã khôi phục ${
                            restoredCount
                        }/${groupDns.length} group; ${
                            failedCount
                        } group lỗi.`
                }
            }));
        } catch (error) {
            console.error(error);
            setRestoreResult((current) => ({
                ...current,
                groups: {
                    success: false,
                    message: "Khôi phục group thất bại."
                }
            }));
        } finally {
            setRestoringGroups(false);
            setRestoreLocked(true);
        }
    };

    return (
        <div className="quayxe-page">
            <div className="quayxe-card">
                <h2>Quay Xe User Access</h2>
                <p className="quayxe-description">
                    Khôi phục quyền truy cập từ Access Snapshot đã được
                    lưu trước khi Offboarding.
                </p>

                <div className="quayxe-search-section">
                    <label>Sam Account Name</label>
                    <input
                        type="text"
                        value={samAccountName}
                        onChange={(event) =>
                            setSamAccountName(event.target.value)
                        }
                        placeholder="ad.auto2"
                    />
                    <button
                        onClick={handleLoadSnapshot}
                        disabled={loading}
                    >
                        {loading ? "Loading..." : "Load Snapshot"}
                    </button>
                </div>

                <div className="quayxe-result">
                    <div className="quayxe-result-title">
                        Kết quả quay xe
                    </div>

                    {snapshotData && (
                        <div className="snapshot-container">
                            <div className="snapshot-card">
                                <div className="snapshot-card-header">
                                    Request Information
                                </div>
                                <div className="snapshot-item">
                                    <label>Request ID</label>
                                    <span>{snapshotData.request_id}</span>
                                </div>
                                <div className="snapshot-item">
                                    <label>Context</label>
                                    <span>{snapshotData.request_context}</span>
                                </div>
                                <div className="snapshot-item">
                                    <label>Employee ID</label>
                                    <span>{snapshotData.employee_id}</span>
                                </div>
                                <div className="snapshot-item">
                                    <label>Sam Account</label>
                                    <span>{snapshotData.sam_account_name}</span>
                                </div>
                                <div className="snapshot-item">
                                    <label>Captured At</label>
                                    <span>{snapshotData.captured_at}</span>
                                </div>
                            </div>

                            <div className="snapshot-card">
                                <div className="snapshot-card-header-row">
                                    <div className="snapshot-card-header">
                                        User Status
                                    </div>
                                    <button
                                        className="quayxe-restore-button"
                                        onClick={handleEnableUser}
                                        disabled={
                                            restoringUser ||
                                            restoreLocked ||
                                            snapshotData.user_status !==
                                                "disabled"
                                        }
                                    >
                                        {restoringUser
                                            ? "Đang enable..."
                                            : restoreResult.user
                                                ? "Đã xử lý"
                                                : "Enable"}
                                    </button>
                                </div>
                                <div className="snapshot-dn">
                                    {snapshotData.user_status === "disabled"
                                        ? "Disabled"
                                        : "Enabled"}
                                </div>
                                {restoreResult.user && (
                                    <div
                                        className={`restore-status ${
                                            restoreResult.user.success
                                                ? "restore-status-success"
                                                : "restore-status-failed"
                                        }`}
                                    >
                                        {restoreResult.user.message}
                                    </div>
                                )}
                            </div>

                            <div className="snapshot-card">
                                <div className="snapshot-card-header-row">
                                    <div className="snapshot-card-header">
                                        Original OU
                                    </div>
                                    <button
                                        className="quayxe-restore-button"
                                        onClick={handleRestoreOu}
                                        disabled={
                                            restoringOu ||
                                            restoreLocked ||
                                            !snapshotData.ou_dn
                                        }
                                    >
                                        {restoringOu
                                            ? "Đang khôi phục..."
                                            : restoreResult.ou
                                                ? "Đã xử lý"
                                                : "Khôi phục"}
                                    </button>
                                </div>
                                <div className="snapshot-dn">
                                    {snapshotData.ou_dn || "No OU found"}
                                </div>
                                {restoreResult.ou && (
                                    <div
                                        className={`restore-status ${
                                            restoreResult.ou.success
                                                ? "restore-status-success"
                                                : "restore-status-failed"
                                        }`}
                                    >
                                        {restoreResult.ou.message}
                                    </div>
                                )}
                            </div>

                            <div className="snapshot-card">
                                <div className="snapshot-card-header-row">
                                    <div className="snapshot-card-header">
                                        Group Membership
                                    </div>
                                    <button
                                        className="quayxe-restore-button"
                                        onClick={handleRestoreGroups}
                                        disabled={
                                            restoringGroups ||
                                            restoreLocked ||
                                            !snapshotData.groups?.length
                                        }
                                    >
                                        {restoringGroups
                                            ? "Đang khôi phục..."
                                            : "Khôi phục"}
                                    </button>
                                </div>
                                {snapshotData.groups &&
                                snapshotData.groups.length > 0 ? (
                                    snapshotData.groups.map(
                                        (groupDn, index) => (
                                            <div
                                                key={`${groupDn}-${index}`}
                                                className="group-card"
                                            >
                                                {groupDn}
                                            </div>
                                        )
                                    )
                                ) : (
                                    <div className="empty-message">
                                        No groups found
                                    </div>
                                )}
                                {restoreResult.groups && (
                                    <div
                                        className={`restore-status ${
                                            restoreResult.groups.success
                                                ? "restore-status-success"
                                                : "restore-status-failed"
                                        }`}
                                    >
                                        {restoreResult.groups.message}
                                    </div>
                                )}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
