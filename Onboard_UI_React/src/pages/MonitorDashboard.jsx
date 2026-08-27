import { useEffect, useState } from "react";
import axiosClient from "../api/axiosClient";
import "./MonitorDashboard.css";


export default function MonitorDashboard() {
    console.log("MONITOR DASHBOARD RENDER");
    const [dashboard, setDashboard] = useState(null);
    const [jobDashboard,setJobDashboard] = useState(null);
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

    const loadJobDashboard = async () => {

        const response =
            await axiosClient.get(
                "/api/ad/monitor/job-dashboard"
            );

        console.log(
            "JOB DASHBOARD",
            response.data
        );

        setJobDashboard(
            response.data
        );
    };

    const loadRuntimeDashboard = async () => {

        await Promise.all([
            loadDashboard(),
            loadJobDashboard()
        ]);
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

        loadRuntimeDashboard();

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

                loadRuntimeDashboard();
            }
        );

        return () => {
            eventSource.close();
        };

    }, []);

    if (
        !dashboard
        ||
        !jobDashboard
    ) {

        return (
            <div>
                Loading...
            </div>
        );
    }

    console.log(
        "AD DASHBOARD DATA",
        dashboard
    );

    console.log(
        "JOB DASHBOARD DATA",
        jobDashboard
    );

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

           <div className="monitor-section-title">
                AD Runtime Overview
            </div>  

            <div className="monitor-cards monitor-cards">

                <div className="monitor-card card-requests">
                    <div className="monitor-card-title">
                        Total Requests
                    </div>
                    <div className="monitor-card-value">
                        {dashboard.total_requests}
                    </div>
                </div>

                <div className="monitor-card build-failed">
                    <div className="monitor-card-title">
                        Build Failed
                    </div>
                    <div className="monitor-card-value">
                        {dashboard.action_build_failed}
                    </div>
                </div>

                <div className="monitor-card card-success">
                    <div className="monitor-card-title">
                        Execute Success
                    </div>
                    <div className="monitor-card-value">
                        {dashboard.execute_action_success}
                    </div>
                </div>

                <div className="monitor-card card-failed">
                    <div className="monitor-card-title">
                        Execute Failed
                    </div>
                    <div className="monitor-card-value">
                        {dashboard.execute_action_failed}
                    </div>
                </div>

            </div>

           <div className="monitor-section-title">
                Workflow Runtime Overview
            </div>                 
            <div className="monitor-cards monitor-cards-job">
                <div className="monitor-card card-requests">

                    <div className="monitor-card-title">
                        Total Jobs
                    </div>

                    <div className="monitor-card-value">
                        {jobDashboard.total_jobs_created}
                    </div>
                </div>

                <div className="monitor-card card-failed">

                    <div className="monitor-card-title">
                        Failed Jobs
                    </div>

                    <div className="monitor-card-value">
                        {jobDashboard.failed_jobs_count}
                    </div>

                </div>

                <div className="monitor-card">

                    <div className="monitor-card-title">
                        Queue Jobs
                    </div>

                    <div className="monitor-card-value">
                        {
                            jobDashboard.next_jobs
                                ?.length || 0
                        }
                    </div>

                </div>

                <div className="monitor-card">

                    <div className="monitor-card-title">
                        Last Executed
                    </div>

                    <div className="runtime-job-name">
                        {
                            jobDashboard
                                ?.last_executed_job
                                ?.display_name
                            || "-"
                        }
                    </div>

                    <div className="runtime-job-meta">
                        {
                            jobDashboard
                                ?.last_executed_job
                                ?.object_name
                            || "-"
                        }
                    </div>

                    <div className="runtime-job-target">
                        {
                            jobDashboard
                                ?.last_executed_job
                                ?.target
                            || "-"
                        }
                    </div>

                    <div className="runtime-job-meta">
                        {
                            jobDashboard
                                ?.last_executed_job
                                ?.execute_at
                            || "-"
                        }
                    </div>

                    <div
                        className={
                            jobDashboard
                                ?.last_executed_job
                                ?.error_message
                                ? "runtime-job-status-failed"
                                : "runtime-job-status-success"
                        }
                    >
                        {
                            jobDashboard
                                ?.last_executed_job
                                ?.error_message
                                ? "FAILED"
                                : "SUCCESS"
                        }
                    </div>

                </div>

            </div>




        <div className="runtime-monitor-panels">    

            <div className="runtime-panel">

                <div className="runtime-panel-title">
                    Next Jobs
                </div>

                {
                    jobDashboard?.next_jobs?.length
                        ? (
                            jobDashboard.next_jobs.map(
                                (job) => (
                                    <div
                                        key={job.job_id}
                                        className="runtime-job-item"
                                    >
                                        <div className="runtime-job-name">
                                                {job.display_name}
                                            </div>

                                            <div className="runtime-job-meta">
                                                {job.object_name || "-"}
                                            </div>

                                            <div className="runtime-job-meta">
                                                {job.target || "-"}
                                            </div>

                                            <div className="runtime-job-meta">
                                                {job.execute_at || job.timestamp}
                                            </div>
                                    </div>
                                )
                            )
                        )
                        : (
                            <div>
                                No queued jobs
                            </div>
                        )
                }
            </div>
            <div className="runtime-panel">
                <div className="runtime-panel-title">
                    Recent Failed Jobs
                </div>

                {
                    jobDashboard?.recent_failed_jobs?.length
                        ? (
                            jobDashboard.recent_failed_jobs.map(
                                (job) => (
                                    <div
                                        key={job.job_id}
                                        className="runtime-job-item"
                                    >
                                        

                                            <div className="runtime-job-name">
                                                {job.display_name}
                                            </div>

                                            <div className="runtime-job-meta">
                                                {job.object_name || "-"}
                                            </div>

                                            <div className="runtime-job-error">
                                                {job.error_message || "-"}
                                            </div>

                                            <div className="runtime-job-meta">
                                                {job.execute_at || job.timestamp}
                                            </div>

                                        
                                    </div>
                                )
                            )
                        )
                        : (
                            <div>
                                No failed jobs
                            </div>
                        )
                }
                

            </div>

        </div>
    </div>            
    </div>
);
}
