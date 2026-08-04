import "./AutomationToolsPage.css";
import { useNavigate } from "react-router-dom";
import { useState } from "react";

export default function AutomationToolsPage() {

    const navigate = useNavigate();
    const [showHints, setShowHints] =
    useState(false);

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
                        👤 Disable/Enable Users
                    </div>

                    <div className="feature-box">
                        ↔️ Group membership
                    </div>

                    <div className="feature-box">
                        📁 Move User to OU
                    </div>

                    <div className="feature-box">
                        🪪 Modify basic attributes
                    </div>

                    <div
                        className="feature-box"
                        onClick={() =>
                            setShowHints(true)
                        }
                    >
                        📖 Fast lane hints (click to see)
                    </div>

                </div>

            <button 
                className="assistant-button"
                onClick={() => navigate("/portal/assistant")}
            >
                Bắt đầu tương tác với trợ lý
            </button>

            </div>
            {
                showHints && (

                    <div className="modal-overlay">

                        <div className="fastlane-modal">

                            <div className="fastlane-header">
                                ⚡ Fast Lane Cheatsheet
                            </div>

                            <div className="fastlane-content">

                                <div className="hint-item">
                                    Tôi cần disable user/Tôi cần khóa user [USER]
                                </div>

                                <div className="hint-item">
                                    Tôi cần disable computer/Tôi cần khóa máy tính [COMPUTER]
                                </div>

                                <div className="hint-item">
                                    Tôi cần add group member/tôi cần thêm thành viên nhóm [USER] [GROUP]
                                </div>

                                <div className="hint-item">
                                    Tôi cần xóa group member/Tôi cần xóa thành viên nhóm [USER] [GROUP]
                                </div>

                                <div className="hint-item">
                                    Tôi cần move OU/Tôi cần chuyển OU [USER] [OU]
                                </div>

                                <div className="hint-item">
                                    Tôi cần đổi department/Tôi cần đổi tên phòng [USER] [NEW_DEPARTMENT]
                                </div>

                                <div className="hint-item">
                                    Tôi cần đổi displayname/Tôi cần đổi tên hiển thị [USER] [NEW_DISPLAYNAME]
                                </div>

                                <div className="hint-item">
                                    Tôi cần đổi description/Tôi cần đổi mô tả [USER] [NEW_DESCRIPTION]
                                </div>

                            </div>

                            <button
                                className="close-btn"
                                onClick={() =>
                                    setShowHints(false)
                                }
                            >
                                Close
                            </button>

                        </div>

                    </div>

                )
            }
        </div>

    );
}