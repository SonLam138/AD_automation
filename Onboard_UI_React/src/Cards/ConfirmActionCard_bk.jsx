import { useState } from "react";
import "./ConfirmActionCard.css";
import {
    executeAction
}
from "../services/actionExecutor";
import { verifySecret } from "../services/adToolApi";
import { getRandomVerifySecretMessage } from "../components/verifySecretMsg";

function ConfirmActionCard({ 
                data, 
                onFinished ,
                onCancel,
                onVerifyMessage
            }){
    const [showSecretInput, setShowSecretInput] = useState(false);
    const [secret, setSecret] = useState("");
    const [executing, setExecuting] = useState(false);
    const [completed, setCompleted] = useState(false);
    const [cancelled, setCancelled] = useState(false);
    const action = data?.action;
    const approvalPolicy = data?.approval_policy;
    const payload = data?.proposed_action_payload || {};
    const samAccountName = payload?.sam_account_name;
    const groupName = payload?.group_name;

    const handleConfirm = () => {
        if (approvalPolicy === "admin_secret") {
            setShowSecretInput(true);
            return;
        }

        if (approvalPolicy === "normal") {
            handleExecute();
            return;
        }

        console.warn("Unknown approval_policy:", approvalPolicy);
    };

    const handleExecute = async () => {

        try {

            setExecuting(true);

            // ========================
            // VERIFY SECRET
            // ========================

            if (
                approvalPolicy === "admin_secret"
            ) {

                if (onVerifyMessage) {
                    onVerifyMessage(
                    getRandomVerifySecretMessage()
                    );
                }

                const verifyResult =
                    await verifySecret(
                        secret
                    );

                if (
                    !verifyResult.success
                ) {

                    alert(
                        "Admin Secret không hợp lệ"
                    );

                    return;
                }
            }

            // ========================
            // EXECUTE ACTION
            // ========================

            const result =
                await executeAction(
                    action,
                    payload
                );
                setCompleted(true);
                if (onFinished) {
                    onFinished(result);
                }

            console.log(
                "EXECUTE RESULT",
                result
            );




        } catch (error) {

            console.error(
                "EXECUTE ERROR",
                error
            );

            alert(
                "Có lỗi khi thực hiện thao tác"
            );

        } finally {

            setExecuting(false);

        }
    };

    const handleCancel = () => {

        setCancelled(true);

        if (onCancel) {
            onCancel();
        }

    };

    return (
        <div className="confirm-card">

            <div className="confirm-card-header">
                <div>
                    <div className="confirm-card-title">
                        Xác nhận hành động
                    </div>

                    <div className="confirm-card-subtitle">
                        Ngáo em đã phân tích xong và cần anh/chị xác nhận trước khi thực hiện.
                    </div>
                </div>
            </div>

            <div className="confirm-card-body">

                <div className="confirm-row">
                    <span className="confirm-label">Action</span>
                    <span className="confirm-value">{action}</span>
                </div>

                <div className="confirm-row">
                    <span className="confirm-label">User</span>
                    <span className="confirm-value">{samAccountName}</span>
                </div>
                {groupName && (
                <div className="confirm-row">
                    <span className="confirm-label">
                        Group
                    </span>

                    <span className="confirm-value">
                        {groupName}
                    </span>
                </div>
                )}
                <div className="confirm-row">
                    <span className="confirm-label">Policy</span>
                    <span className={`policy-badge ${approvalPolicy}`}>
                        {approvalPolicy}
                    </span>
                </div>

            </div>

            {showSecretInput && (
                <div className="secret-box">
                    <label className="secret-label">
                        Admin Secret
                    </label>

                    <input
                        type="password"
                        value={secret}
                        className="secret-input"
                        placeholder="Nhập admin secret..."
                        onChange={(e) => setSecret(e.target.value)}
                    />
                </div>
            )}

            {completed && (

                <div className="action-completed">
                    ✅ Đã thực hiện
                </div>

            )}
            {cancelled && (

                <div className="action-cancelled">
                    🚫 Yêu cầu đã bị hủy
                </div>

            )}
            {!completed && !cancelled && (
            <div className="confirm-card-actions">

                {!showSecretInput && (
                    <button
                        className="confirm-btn"
                        onClick={handleConfirm}
                        disabled={executing || completed}
                    >
                        {executing ? "Đang xử lý..." : "Xác nhận"}
                    </button>
                )}

                {showSecretInput && (
                    <button
                        className="confirm-btn"
                        onClick={handleExecute}
                        disabled={executing || completed || !secret.trim()}
                    >
                        {executing ? "Đang xử lý..." : "Thực hiện"}
                    </button>
                )}

                <button
                    className="cancel-btn"
                    onClick={handleCancel}
                    disabled={executing || completed}
                >
                    Hủy
                </button>

            </div>
            )}

        </div>
    );
}

// export default ConfirmActionCard;