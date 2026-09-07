import "./WorkflowPage.css";
import { useNavigate } from "react-router-dom";

export default function WorkflowPage() {

    const navigate = useNavigate();

    return (

        <div className="workflow-page">

            <div className="workflow-card">

                <h2>
                    Workflow Automation Engine
                </h2>

                <p className="workflow-description">

                    Thực hiện các quy trình tự động hóa
                    nghiệp vụ doanh nghiệp trên
                    Active Directory và hạ tầng CNTT.

                </p>

                <div className="workflow-features">

                    <div
                        className="workflow-box"
                        onClick={() =>
                            navigate(
                                "/portal/workflow/offboarding"
                            )
                        }
                    >
                        👤 Employee Offboarding
                    </div>

                    <div
                        className="workflow-box"
                        onClick={() =>
                            navigate(
                                "/portal/workflow/bulk-offboarding"
                            )
                        }
                    >
                        📄 Bulk Offboarding Import
                    </div>
                    
                    <div
                        className="workflow-box workflow-box-custom"
                        onClick={() =>
                            navigate(
                                "/portal/workflow/custom"
                            )
                        }
                    >
                        ⚙️ Custom Workflow
                        <br />
                        <span>
                            Build your own workflow
                        </span>
                    </div>

                    <div
                        className="workflow-box workflow-box-review"
                        onClick={() =>
                            navigate(
                                "/portal/workflow/offboarding-review"
                            )
                        }
                    >
                        🔍 Offboarding Review
                        <br />
                        <span>
                            (AD/PAD Account Discovery)
                        </span>
                    </div>

                    <div
                        className="workflow-box workflow-box-temp"
                        onClick={() =>
                            navigate(
                                "/portal/workflow/temp-access"
                            )
                        }
                    >
                        ⏳ Temporary Access
                        <br />
                        <span>
                           (Grant permission to User & Computer)
                        </span>
                    </div>

                </div>

            </div>

        </div>

    );
}