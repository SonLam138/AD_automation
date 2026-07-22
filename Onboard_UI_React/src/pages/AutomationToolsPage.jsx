import "./AutomationToolsPage.css";
import { useNavigate } from "react-router-dom";

export default function AutomationToolsPage() {

    const navigate = useNavigate();

    const handleStartAssistant = () => {

        console.log(
            "START ASSISTANT"
        );

        // TODO:
        // Navigate sang giao diện chat
    };

    return (

        <div className="automation-page">

            <div className="assistant-card">

                {/* =====================================================
                   TODO:
                   Thay ảnh đại diện Ngáo tại đây
                ===================================================== */}

                <img
                    src="/ngao.png"
                    alt="AD Assistant"
                    className="assistant-avatar"
                />

                <h2>
                    AD Automation Assistant
                </h2>

                <p className="assistant-description">

                    Hỗ trợ thực hiện các tác vụ
                    tự động hóa trên Active Directory
                    và hạ tầng doanh nghiệp.

                </p>

                <div className="assistant-features">

                    <div className="feature-box">
                        👤 Disable User
                    </div>

                    <div className="feature-box">
                        ✅ Enable User
                    </div>

                    <div className="feature-box">
                        🔑 Reset Password
                    </div>

                    <div className="feature-box">
                        🔓 Unlock User
                    </div>

                    <div className="feature-box">
                        👥 Group Management
                    </div>

                </div>

            <button 
                className="assistant-button"
                onClick={() => navigate("/portal/assistant")}
            >
                Bắt đầu tương tác với trợ lý
            </button>

            </div>

        </div>

    );
}