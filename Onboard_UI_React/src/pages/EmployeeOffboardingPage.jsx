import { useState } from "react";
import { createEmployeeOffboarding } from "../services/adToolApi";
import "./EmployeeOffboardingPage.css";
export default function EmployeeOffboardingPage() {

    const [formData, setFormData] =
        useState({
            employee_id: "",
            email: "",
            reason: "",
            effective_time: ""
        });
    const [submitResult, setSubmitResult] =
        useState(null);

    const [error, setError] =
        useState("");

    const handleChange = (e) => {

        setFormData({
            ...formData,
            [e.target.name]:
                e.target.value
        });

    };

    const handleSubmit = async () => {

        try {

            setError("");
            setSubmitResult(null);

            const result =
                await createEmployeeOffboarding(
                    formData
                );

            setSubmitResult(
                result
            );

            console.log(
                "SUCCESS",
                result
            );

        } catch (error) {

            setError(
                error.response?.data?.detail
                || error.message
            );

            console.error(
                "FAILED",
                error
            );

        }

    };

    return (
        
        <div className="offboarding-page">
            <div className="offboarding-card">

                <h2>
                    Employee Offboarding
                </h2>

                <p className="offboarding-subtitle">
                    Submit employee offboarding requests
                    for Active Directory automation.
                </p>
                <div className="offboarding-form">
                    <div className="form-group">

                        <label className="offboarding-label">
                            Employee ID
                        </label>

                        <input
                            name="employee_id"
                            placeholder="Enter Employee ID"
                            value={formData.employee_id}
                            onChange={handleChange}
                        />

                    </div>

                    <div className="form-group">

                        <label className="offboarding-label">
                            Email
                        </label>

                        <input
                            name="email"
                            placeholder="Enter Email"
                            value={formData.email}
                            onChange={handleChange}
                        />

                    </div>

                    <div className="form-group">

                        <label className="offboarding-label">
                            Offboarding Reason
                        </label>

                        <input
                            name="reason"
                            placeholder="Enter Reason"
                            value={formData.reason}
                            onChange={handleChange}
                        />

                    </div>

                    <div className="form-group">

                        <label className="offboarding-label">
                            Effective Time
                        </label>

                        <input
                            type="datetime-local"
                            name="effective_time"
                            value={formData.effective_time}
                            onChange={handleChange}
                        />

                    </div>
                
                    <button
                        className="submit-request-btn"
                        onClick={
                            handleSubmit
                        }
                    >
                        Submit
                    </button>
                </div>
                {
                    submitResult&& (

                        <div className="success-card">

                            <h3>
                                ✅ Request Created Successfully
                            </h3>

                            <div className="success-row">

                                <span className="success-label">
                                    Request ID
                                </span>

                                <span className="success-value">
                                    {submitResult.request_id}
                                </span>

                            </div>

                            <div className="success-row">

                                <span className="success-label">
                                    Workflow
                                </span>

                                <span className="success-value">
                                    Employee Offboarding
                                </span>

                            </div>

                            <div className="success-row">

                                <span className="success-label">
                                    Execute At
                                </span>

                                <span className="success-value">
                                    {submitResult.execute_at}
                                </span>

                            </div>

                            <div className="success-row">

                                <span className="success-label">
                                    Status
                                </span>

                                <span className="success-value">
                                    Waiting For Execution
                                </span>

                            </div>

                        </div>

                    )
                }
                {
                    error && (

                        <div className="error-card"
                            style={{
                                marginTop: "20px",
                                padding: "15px",
                                background: "#fef2f2",
                                border: "1px solid #dc2626",
                                borderRadius: "8px"
                            }}
                        >

                            ❌ {error}

                        </div>

                    )
                }

      
            </div>
        </div>
    );
}



