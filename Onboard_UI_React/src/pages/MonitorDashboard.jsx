import { useEffect, useState } from "react";
import axiosClient from "../api/axiosClient";
import "./MonitorDashboard.css";


export default function MonitorDashboard() {
    console.log("MONITOR DASHBOARD RENDER");
    const [dashboard, setDashboard] = useState(null);
    const [objectType, setObjectType] =
    useState("ALL");

    const [actionUser, setActionUser] =
        useState("");
    const [searchResults, setSearchResults] =
    useState([]);
    const [objectName, setObjectName] =
        useState("");

    const [fromDate, setFromDate] =
        useState("");

    const [toDate, setToDate] =
        useState("");

    const loadDashboard = async () => {
        const response = await axiosClient.get(
            "/api/ad/monitor/dashboard"
        );

        setDashboard(
            response.data
        );
    };

    const resetSearch = () => {

        setObjectType(
            "ALL"
        );

        setActionUser(
            ""
        );

        setObjectName(
            ""
        );

        setFromDate(
            ""
        );

        setToDate(
            ""
        );

        setSearchResults(
            []
        );
    };
    const searchMonitor = async () => {

        const response =
            await axiosClient.get(
                "/api/ad/monitor/search",
                {
                    params: {
                        object_type:
                            objectType,

                        action_user:
                            actionUser,

                        object_name:
                            objectName,

                        from_date:
                            fromDate,

                        to_date:
                            toDate
                    }
                }
            );

        console.log(
            "SEARCH RESULT",
            response.data
        );

        setSearchResults(
            response.data
        );
    };


    useEffect(() => {
        loadDashboard();
    }, []);


    useEffect(() => {

        const eventSource =
            new EventSource(
                "http://localhost:8000/api/ad/monitor/stream"
            );

        eventSource.addEventListener(
            "monitor_refresh",
            () => {
                console.log(
                    "MONITOR REFRESH RECEIVED"
                    );
                loadDashboard();
            }
        );

        return () => {
            eventSource.close();
        };

    }, []);

    if (!dashboard) {
    return (
        <div>
            Loading...
        </div>
    );
}

return (
    <div>

        <h2>
            Runtime Monitor
        </h2>

        <div className="monitor-dashboard">

            <div className="monitor-header">

                <div>

                    <div className="monitor-title">
                        AD Automation Monitor
                    </div>

                    <div className="monitor-date">
                        {
                            dashboard?.date
                                ? new Date(
                                    dashboard.date
                                ).toLocaleDateString(
                                    "vi-VN"
                                )
                                : ""
                        }
                    </div>

                </div>

                <div className="monitor-live">
                    🟢 LIVE
                </div>

            </div>

            <div className="monitor-cards">

                <div className="monitor-card card-requests">
                    <div className="monitor-card-title">
                        Total Requests
                    </div>
                    <div className="monitor-card-value">
                        {dashboard.total_requests}
                    </div>
                </div>

                <div className="monitor-card card-success">
                    <div className="monitor-card-title">
                        Success
                    </div>
                    <div className="monitor-card-value">
                        {dashboard.success_count}
                    </div>
                </div>

                <div className="monitor-card card-failed">
                    <div className="monitor-card-title">
                        Failed
                    </div>
                    <div className="monitor-card-value">
                        {dashboard.failed_count}
                    </div>
                </div>

            </div>

            <div className="monitor-search-panel">

                <div className="monitor-search-title">
                    Search Monitor
                </div>

                <div className="monitor-filter-grid">

                    <div>
                        <label>
                            Object Type
                        </label>

                        <select
                            value={objectType}
                            onChange={(e) =>
                                setObjectType(
                                    e.target.value
                                )
                            }
                        >
                            <option value="ALL">
                                All Objects
                            </option>

                            <option value="USER">
                                USER
                            </option>

                            <option value="COMPUTER">
                                COMPUTER
                            </option>

                            <option value="GROUP">
                                GROUP
                            </option>

                            <option value="OU">
                                OU
                            </option>
                        </select>

                    </div>

                    <div>

                        <label>
                            Action User
                        </label>

                        <input
                            value={actionUser}
                            onChange={(e) =>
                                setActionUser(
                                    e.target.value
                                )
                            }
                            placeholder="sonnm"
                        />

                    </div>

                </div>

                <div className="monitor-text-filter">

                    <label>
                        Object Name
                    </label>

                    <input
                        value={objectName}
                        onChange={(e) =>
                            setObjectName(
                                e.target.value
                            )
                        }
                        placeholder="ad.auto2"
                    />

                </div>

                <div className="monitor-filter-grid">

                    <div>

                        <label>
                            From Date
                        </label>

                        <input
                            type="date"
                            value={fromDate}
                            onChange={(e) =>
                                setFromDate(
                                    e.target.value
                                )
                            }
                        />

                    </div>

                    <div>

                        <label>
                            To Date
                        </label>

                        <input
                            type="date"
                            value={toDate}
                            onChange={(e) =>
                                setToDate(
                                    e.target.value
                                )
                            }
                        />

                    </div>

                </div>

                <div className="monitor-search-actions">

                    <button
                        onClick={searchMonitor}
                    >
                        Search
                    </button>

                    <button
                        onClick={resetSearch}
                    >
                        Reset
                    </button>

                </div>

            </div>

            <div className="monitor-search-results">

                <div className="monitor-search-title">
                    Search Results
                </div>

                {
                    searchResults.map(
                        (item) => (
                            <div
                                key={item.search_id}
                                className="search-result-card"
                            >
                                <div>
                                    <strong>
                                        {item.action}
                                    </strong>
                                </div>

                                <div>
                                    Target Object:
                                    {" "}
                                    {item.object_name}
                                </div>

                                <div>
                                    Type:
                                    {" "}
                                    {item.object_type}
                                </div>

                                <div>
                                    Action by:
                                    {" "}
                                    {item.username}
                                </div>

                                <div>
                                    Time:
                                    {" "}
                                    {
                                        new Date(
                                            item.time
                                        ).toLocaleString(
                                            "vi-VN"
                                        )
                                    }
                                </div>

                            </div>
                        )
                    )
                }

            </div>

        </div>

    </div>
);
}
