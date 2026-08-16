import { useState } from "react";
import { createEmployeeOffboarding } from "../services/adToolApi";

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

        <div>

            <h2>
                Employee Offboarding
            </h2>

            <input
                name="employee_id"
                placeholder="Employee ID"
                value={
                    formData.employee_id
                }
                onChange={
                    handleChange
                }
            />

            <br /><br />

            <input
                name="email"
                placeholder="Email"
                value={
                    formData.email
                }
                onChange={
                    handleChange
                }
            />

            <br /><br />

            <input
                name="reason"
                placeholder="Reason"
                value={
                    formData.reason
                }
                onChange={
                    handleChange
                }
            />

            <br /><br />

            <input
                type="datetime-local"
                name="effective_time"
                value={
                    formData.effective_time
                }
                onChange={
                    handleChange
                }
            />

            <button
                onClick={
                    handleSubmit
                }
            >
                Submit
            </button>
            {
                submitResult&& (

                    <div className="success-card">

                        <h3>
                            ✅ Request Created Successfully
                        </h3>

                        <p>
                            Request ID:
                            <strong>
                                {submitResult.request_id}
                            </strong>
                        </p>

                        <p>
                            Workflow:
                            Employee Offboarding
                        </p>

                        <p>
                            Execute At:
                            {
                                submitResult.execute_at
                            }
                        </p>

                        <p>
                            Status:
                            Waiting For Execution
                        </p>

                    </div>

                )
            }
            {
                error && (

                    <div
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

    );
}



