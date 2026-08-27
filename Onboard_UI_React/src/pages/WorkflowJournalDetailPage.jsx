import {
    useEffect,
    useMemo,
    useState
} from "react";

import {
    useNavigate,
    useParams
} from "react-router-dom";

import {getWorkflowJournalDetail} from "../services/adToolApi";

import "./WorkflowJournalDetailPage.css";


export default function WorkflowJournalDetailPage() {

    const navigate = useNavigate();

    const {
        journalId
    } = useParams();

    const [
        journal,
        setJournal
    ] = useState(null);

    const [
        loading,
        setLoading
    ] = useState(true);

    const [
        error,
        setError
    ] = useState("");


    useEffect(() => {

        const loadJournalDetail = async () => {

            try {

                setLoading(true);

                setError("");

                const data =
                    await getWorkflowJournalDetail(
                        journalId
                    );

                setJournal(
                    data?.item ?? null
                );

            }
            catch (err) {

                console.error(
                    "Load workflow journal detail failed:",
                    err
                );

                setError(
                    err?.response?.data?.detail
                    || "Không thể tải thông tin workflow."
                );

            }
            finally {

                setLoading(false);

            }

        };

        loadJournalDetail();

    }, [journalId]);


    const snapshot =
        journal?.snapshot ?? {};

    const workflowInfo =
        snapshot?.workflowInfo ?? {};

    const objects =
        Array.isArray(snapshot?.objects)
            ? snapshot.objects
            : [];

    const steps =
        Array.isArray(snapshot?.steps)
            ? snapshot.steps
            : [];


    const objectMap = useMemo(() => {

        return objects.reduce(
            (
                result,
                object
            ) => {

                if (object?.alias) {

                    result[object.alias] =
                        object;

                }

                return result;

            },
            {}
        );

    }, [objects]);


    const formatDateTime = (
        dateValue
    ) => {

        if (!dateValue) {

            return "Không đặt lịch";

        }

        const date =
            new Date(dateValue);

        if (
            Number.isNaN(
                date.getTime()
            )
        ) {

            return dateValue;

        }

        return (
            date.toLocaleDateString(
                "vi-VN"
            )
            + " "
            + date.toLocaleTimeString(
                "vi-VN",
                {
                    hour: "2-digit",
                    minute: "2-digit"
                }
            )
        );

    };


    const getObjectTarget = (
        object
    ) => {

        if (!object) {

            return "-";

        }

        switch (
            object.objectType
        ) {

            case "USER":

                return (
                    object.username
                    || object.email
                    || "-"
                );

            case "COMPUTER":

                return (
                    object.computer_name
                    || "-"
                );

            case "GROUP":

                return (
                    object.group_name
                    || "-"
                );

            default:

                return (
                    object.username
                    || object.computer_name
                    || object.group_name
                    || object.email
                    || "-"
                );

        }

    };


    const getStepObjectLabel = (
        objectRef
    ) => {

        const object =
            objectMap[objectRef];

        const target =
            getObjectTarget(
                object
            );

        if (
            !object
            || target === "-"
        ) {

            return objectRef || "-";

        }

        return `${objectRef} (${target})`;

    };


    if (loading) {

        return (
            <div className="workflow-detail-page">

                <div className="workflow-detail-state">
                    Đang tải workflow...
                </div>

            </div>
        );

    }


    if (error) {

        return (
            <div className="workflow-detail-page">

                <div className="workflow-detail-error">

                    <h3>
                        Không tải được workflow
                    </h3>

                    <p>
                        {error}
                    </p>

                    <button
                        className="detail-back-btn"
                        onClick={() =>
                            navigate(
                                "/portal/workflow/custom/designer/workflow-journal"
                            )
                        }
                    >
                        ← Back to Journal
                    </button>

                </div>

            </div>
        );

    }


    if (!journal) {

        return (
            <div className="workflow-detail-page">

                <div className="workflow-detail-state">
                    Không tìm thấy workflow.
                </div>

            </div>
        );

    }


    return (
        <div className="workflow-detail-page">

            <div className="workflow-detail-header">

                <div>

                    <div className="workflow-detail-eyebrow">
                        WORKFLOW JOURNAL
                    </div>

                    <h2 className="workflow-detail-title">
                        Workflow Detail
                    </h2>

                </div>

                <button
                    className="detail-back-btn"
                    onClick={() =>
                        navigate(
                            "/portal/workflow/custom/designer/workflow-journal"
                        )
                    }
                >
                    ← Back to Journal
                </button>

            </div>


            <section className="workflow-detail-card workflow-info-card">

                <div className="detail-section-header">

                    <div>

                        <h3>
                            Workflow Information
                        </h3>

                        <span>
                            {journal.journal_id}
                        </span>

                    </div>

                    <span
                        className={
                            `detail-status-badge ${
                                journal.status || "saved"
                            }`
                        }
                    >
                        {journal.status || "saved"}
                    </span>

                </div>


                <div className="workflow-info-grid">

                    <div className="workflow-info-item">

                        <span className="workflow-info-label">
                            Workflow Name
                        </span>

                        <strong className="workflow-info-value">
                            {workflowInfo.workflowName || "-"}
                        </strong>

                    </div>


                    <div className="workflow-info-item">

                        <span className="workflow-info-label">
                            Workflow ID
                        </span>

                        <strong className="workflow-info-value workflow-code">
                            {workflowInfo.workflowId || "-"}
                        </strong>

                    </div>


                    <div className="workflow-info-item">

                        <span className="workflow-info-label">
                            Description
                        </span>

                        <strong className="workflow-info-value">
                            {workflowInfo.description || "-"}
                        </strong>

                    </div>


                    <div className="workflow-info-item">

                        <span className="workflow-info-label">
                            Context
                        </span>

                        <strong className="workflow-info-value workflow-code">
                            {workflowInfo.context || "-"}
                        </strong>

                    </div>

                </div>

            </section>


            <div className="workflow-detail-lower-grid">

                <section className="workflow-detail-card object-card">

                    <div className="detail-section-header">

                        <div>

                            <h3>
                                Objects
                            </h3>

                            <span>
                                {objects.length} object(s)
                            </span>

                        </div>

                    </div>


                    <div className="detail-table-wrapper">

                        <table className="detail-table object-table">

                            <thead>

                                <tr>
                                    <th>Alias</th>
                                    <th>Type</th>
                                    <th>Target</th>
                                </tr>

                            </thead>

                            <tbody>

                                {objects.length === 0 ? (

                                    <tr>

                                        <td
                                            colSpan="3"
                                            className="detail-empty-cell"
                                        >
                                            Không có object.
                                        </td>

                                    </tr>

                                ) : (

                                    objects.map(
                                        (
                                            object,
                                            index
                                        ) => (

                                            <tr
                                                key={
                                                    object.alias
                                                    || index
                                                }
                                            >

                                                <td className="object-alias">
                                                    {object.alias || "-"}
                                                </td>

                                                <td>

                                                    <span className="object-type-badge">
                                                        {object.objectType || "-"}
                                                    </span>

                                                </td>

                                                <td className="object-target">
                                                    {getObjectTarget(object)}
                                                </td>

                                            </tr>

                                        )
                                    )

                                )}

                            </tbody>

                        </table>

                    </div>

                </section>


                <section className="workflow-detail-card step-card">

                    <div className="detail-section-header">

                        <div>

                            <h3>
                                Workflow Steps
                            </h3>

                            <span>
                                {steps.length} step(s)
                            </span>

                        </div>

                    </div>


                    <div className="detail-table-wrapper">

                        <table className="detail-table step-table">

                            <thead>

                                <tr>
                                    <th>#</th>
                                    <th>Object</th>
                                    <th>Action</th>
                                    <th>Execute Time</th>
                                </tr>

                            </thead>

                            <tbody>

                                {steps.length === 0 ? (

                                    <tr>

                                        <td
                                            colSpan="4"
                                            className="detail-empty-cell"
                                        >
                                            Không có workflow step.
                                        </td>

                                    </tr>

                                ) : (

                                    steps.map(
                                        (
                                            step,
                                            index
                                        ) => (

                                            <tr
                                                key={`${step.objectRef}-${step.action}-${index}`}
                                            >

                                                <td className="step-number">
                                                    {index + 1}
                                                </td>

                                                <td className="step-object">
                                                    {
                                                        getStepObjectLabel(
                                                            step.objectRef
                                                        )
                                                    }
                                                </td>

                                                <td>

                                                    <span className="action-badge">
                                                        {step.action || "-"}
                                                    </span>

                                                </td>

                                                <td>
                                                    {
                                                        formatDateTime(
                                                            step.executeTime
                                                        )
                                                    }
                                                </td>

                                            </tr>

                                        )
                                    )

                                )}

                            </tbody>

                        </table>

                    </div>

                </section>

            </div>

        </div>
    );

}