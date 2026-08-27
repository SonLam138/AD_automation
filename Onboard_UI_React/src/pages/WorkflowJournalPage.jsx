import { useEffect, useState } from "react";
import { getWorkflowJournalList } from "../services/adToolApi";
import "./WorkflowJournalPage.css";
import { useNavigate } from "react-router-dom";
import {deleteWorkflowJournal} from "../services/adToolApi";

export default function WorkflowJournalPage() {
    const [entries, setEntries] = useState([]);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();
    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            setLoading(true);

            const data =
                await getWorkflowJournalList();
                console.log("Journal Data:", data);

            setEntries(data.items || []);
        }
        catch (error) {
            console.error(error);
        }
        finally {
            setLoading(false);
        }
    };

    const handleDelete = async (
        journalId
    ) => {

        const confirmed =
            window.confirm(
                "Delete this workflow?"
            );

        if (!confirmed) {
            return;
        }

        try {

            await deleteWorkflowJournal(
                journalId
            );

            await loadData();

        }
        catch (error) {

            alert(
                error?.response?.data?.detail
                || "Delete workflow failed."
            );

        }

    };

    function formatDateTime(dateString) {
        const date = new Date(dateString);

        return (
            date.toLocaleDateString("vi-VN") +
            " " +
            date.toLocaleTimeString(
                "vi-VN",
                {
                    hour: "2-digit",
                    minute: "2-digit"
                }
            )
        );
    }


    return (
        <div className="workflow-journal-page">

            <div className="workflow-journal-header">

                <button
                    className="back-btn"
                    onClick={() =>
                        navigate("/portal/workflow/custom")
                    }
                >
                    ← Back
                </button>

                <h2 className="workflow-journal-title">
                    Workflow Journal
                </h2>

            </div>


            <h2 className="workflow-journal-title">
                Workflow Journal
            </h2>

            <div className="workflow-journal-card">

                <table className="workflow-table">

                    <thead>
                        <tr>
                            <th>Workflow Name</th>
                            <th>Saved At</th>
                            <th>Objects</th>
                            <th>Steps</th>
                            <th>Status</th>
                            <th>Action</th>
                        </tr>
                    </thead>

                    <tbody>

                        {entries.map((item) => (

                            <tr key={item.journal_id}>

                                <td>
                                    {item.workflow_name}
                                </td>

                                <td>
                                    {new Date(item.saved_at)
                                        .toLocaleDateString("vi-VN")}
                                    {" "}
                                    {new Date(item.saved_at)
                                        .toLocaleTimeString(
                                            "vi-VN",
                                            {
                                                hour: "2-digit",
                                                minute: "2-digit"
                                            }
                                        )}
                                </td>

                                <td>
                                    {item.object_count}
                                </td>

                                <td>
                                    {item.step_count}
                                </td>

                                <td>

                                    <span
                                        className={`status-badge ${item.status}`}
                                    >
                                        {item.status}
                                    </span>

                                </td>

                                <td>

                                    <button
                                        className="view-btn"
                                        onClick={() =>
                                            navigate(
                                                `/portal/workflow/custom/designer/workflow-journal/${item.journal_id}`
                                            )
                                        }
                                    >
                                        View
                                    </button>

                                    {item.status == "saved" && (

                                        <button
                                            className="delete-btn"
                                            onClick={() =>
                                                handleDelete(
                                                    item.journal_id
                                                )
                                            }
                                        >
                                            Delete
                                        </button>

                                    )}

                                </td>

                            </tr>

                        ))}

                    </tbody>

                </table>

            </div>

        </div>
    );
}