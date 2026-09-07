import "./OffboardingReviewPage.css";
import { useState } from "react";
import {analyzeOffboardingFile, confirmOffboardingReview} from "../services/adToolApi";

export default function OffboardingReviewPage() {

    const [selectedFile, setSelectedFile] =
        useState(null);
    const [reviewResult, setReviewResult] =
        useState(null);
    const [loading, setLoading] =
        useState(false);
    const [showConfirm, setShowConfirm] =
    useState(false);
    const [isCreatingRequests,
        setIsCreatingRequests] =
            useState(false);
    const canCreateRequests =
        reviewResult &&
        reviewResult.requestsReady > 0;
        
    const [
        isConfirmed,
        setIsConfirmed
    ] = useState(false);

    const [
        isConfirming,
        setIsConfirming
    ] = useState(false);

    const handleFileChange = (event) => {

        const file =
            event.target.files?.[0];

        if (!file) {
            return;
        }

        setSelectedFile(file);
    };

    const handleAnalyze =
        async () => {

            try {

                const result =
                    await analyzeOffboardingFile(
                        selectedFile
                    );

                setReviewResult(
                    result
                );

            } catch (error) {

                console.error(error);

                alert(
                    "Analyze failed"
                );
            }
        };

    const requestCandidates =
        reviewResult?.results?.filter(
            item =>
                item.found &&
                item.isDisabled === false &&
                item.email
        ) || [];

    const handleConfirm =
    async () => {

        try {

            setIsConfirming(
                true
            );

            await confirmOffboardingReview(
                reviewResult.session_id
            );

            setIsConfirmed(
                true
            );

        }
        catch (error) {

            console.error(
                error
            );

            alert(
                "Create requests failed."
            );

        }
        finally {

            setIsConfirming(
                false
            );
        }
    };

    

    return (

        <div className="workflow-page">

            <div className="workflow-card">

                <h2>
                    🔍 Offboarding Review
                </h2>

                <p className="workflow-description">

                    Rà soát tài khoản hệ thống liên quan
                    trước khi tạo yêu cầu Offboarding.

                </p>

                {/* ================================================= */}
                {/* Upload Card */}
                {/* ================================================= */}

                <div className="review-section">

                    <h3>
                        1. Upload HR Offboarding File
                    </h3>

                    <div className="review-card">

                        <input
                            type="file"
                            accept=".xlsx,.xls"
                            onChange={handleFileChange}
                        />
                        {
                            selectedFile && (
                                <div
                                    className="selected-file"
                                >
                                    📄 {selectedFile.name}
                                </div>
                            )
                        }

                        <button
                            className="workflow-button"
                            disabled={!selectedFile}
                            onClick={handleAnalyze}
                        >
                            Analyze
                        </button>

                    </div>

                </div>

                {/* ================================================= */}
                {/* Summary Card */}
                {/* ================================================= */}

                {
                    reviewResult && (

                        <div className="review-section">

                            <h3>
                                2. Review Summary
                            </h3>

                            <div className="review-card">

                                <div className="summary-item">
                                    <span>Tổng nhân sự rà soát</span>
                                    <strong>
                                        {reviewResult.totalUsers}
                                    </strong>
                                </div>

                                <div className="summary-item">
                                    <span>Các tài khoản liên quan được tìm thấy</span>
                                    <strong>
                                        {reviewResult.foundAccounts}
                                    </strong>
                                </div>

                                <div className="summary-item">
                                    <span>Các tài khoản liên quan đã bị disabled</span>
                                    <strong>
                                        {reviewResult.alreadyDisabled}
                                    </strong>
                                </div>

                                <div className="summary-item">
                                    <span>Các tài khoản liên quan thiếu trường email</span>
                                    <strong>
                                        {reviewResult.missingEmail}
                                    </strong>
                                </div>

                                <div className="summary-item">
                                    <span>Tổng tài khoản hệ thống thực tế đã xử lý</span>
                                    <strong>
                                        {reviewResult.totalSearchKeys}
                                    </strong>
                                </div>

                            </div>

                        </div>

                    )
                }
                
                {/* ================================================= */}
                {/* Discovery Result */}
                {/* ================================================= */}

                {
                    reviewResult?.results && (

                        <div className="review-section">

                            <h3>
                                3. Request Summary
                            </h3>

                            <div className="review-card">

                                <div className="summary-item">
                                    <span>Số lượng yêu thu hồi cầu cần khởi tạo</span>
                                    <strong>
                                        {reviewResult.requestsReady}
                                    </strong>
                                </div>

                                <div className="summary-item">
                                    <span>Các tài khoản đã được thu hồi đúng quy định</span>
                                    <strong>
                                        {reviewResult.alreadyDisabled}
                                    </strong>
                                </div>

                                <div className="summary-item">
                                    <span>Số lượng tài khoản liên quan không tìm thấy</span>
                                    <strong>
                                        {reviewResult.noRelatedAccounts}
                                    </strong>
                                </div>

                                <div className="summary-item">
                                    <span>Các tài khoản liên quan cần rà soát thủ công</span>
                                    <strong>
                                        {reviewResult.missingEmail}
                                    </strong>
                                </div>

                            </div>
                            <button
                                className="workflow-button"
                                disabled={!canCreateRequests}
                                onClick={() => {
                                    if (!canCreateRequests) {
                                        return;
                                    }

                                    setShowConfirm(true);
                                }}
                            >
                                Create
                                {" "}
                                {reviewResult?.requestsReady || 0}
                                {" "}
                                Offboarding Requests
                            </button>


                        </div>

                    )
                }

                {/* ================================================= */}
                {/* Confirm */}
                {/* ================================================= */}
                
                {
                    showConfirm && (
                        <div className="review-section">

                            <h3>
                                4. Confirm Request Creation
                            </h3>

                            <div className="review-card">

                                <p>

                                    The following

                                    <strong>
                                        {" "}
                                        {requestCandidates.length}
                                        {" "}
                                    </strong>

                                    active related accounts
                                    will have Offboarding Requests created.

                                </p>

                                {
                                    requestCandidates.map(
                                        (
                                            item,
                                            index
                                        ) => (
                                            <div
                                                key={index}
                                                className="request-candidate"
                                            >

                                                <div
                                                    className="request-account"
                                                >
                                                    ✅ {item.samAccountName}
                                                </div>

                                                <div
                                                    className="request-email"
                                                >
                                                    {item.email}
                                                </div>

                                            </div>
                                        )
                                    )
                                }

                                <hr />

                                <p>
                                    Total Requests:
                                    <strong>
                                        {" "}
                                        {
                                            requestCandidates.length
                                        }
                                    </strong>
                                </p>

                                <button
                                    className="workflow-button"
                                    disabled={
                                        isConfirming
                                        || isConfirmed
                                    }
                                    onClick={handleConfirm}
                                >
                                    {
                                        isConfirming
                                            ? "Creating Requests..."
                                            : isConfirmed
                                                ? "Requests Created"
                                                : "Confirm Create Requests"
                                    }
                                </button>

                            </div>

                        </div>
                    )
                }
                {
                    isConfirmed && (

                        <div className="review-card confirm-success">

                            <h4>
                                ✅ Offboarding Requests Created
                            </h4>

                            <p>

                                Related account requests
                                have been submitted to
                                Workflow Engine successfully.

                            </p>

                            <p>

                                Please open the
                                <strong>
                                    {" "}
                                    Monitor Dashboard
                                </strong>
                                {" "}
                                to track execution progress.

                            </p>

                        </div>

                    )
                }
                

            </div>

        </div>

    );
}