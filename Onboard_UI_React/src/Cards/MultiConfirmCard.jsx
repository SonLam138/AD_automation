import { useState } from "react";
import "./MultiConfirmCard.css";

import {
    executeAction
}
from "../services/actionExecutor";

import {
    verifySecret
}
from "../services/adToolApi";

import { getRandomVerifySecretMessage } from "../components/verifySecretMsg";


function MultiConfirmCard({
    data,
    onFinished,
    onCancel,
    onVerifyMessage
}) {
    const [
        showSecretInput,
        setShowSecretInput
    ] = useState(false);

    const [
        secret,
        setSecret
    ] = useState("");

    const [
        executing,
        setExecuting
    ] = useState(false);

    const [
        completed,
        setCompleted
    ] = useState(false);

    const [
        cancelled,
        setCancelled
    ] = useState(false);

    const action =
        data?.action;

    const approvalPolicy =
        data?.approval_policy;

    const resolvedObjects =
        data?.resolved_objects || {};

    const payload =
        data?.proposed_action_payload || {};


    const formatLabel = (key) => {
        return String(key)
            .replaceAll("_", " ")
            .replace(/\b\w/g, char =>
                char.toUpperCase()
            );
    };


    const getObjectDisplayValue = (objectType, objectData) => {
        if (!objectData) {
            return "";
        }

        if (objectData.displayName) {
            return objectData.displayName;
        }

        if (objectData.display_name) {
            return objectData.display_name;
        }

        if (objectData.sam_account_name) {
            return objectData.sam_account_name;
        }

        if (objectData.samaccountname) {
            return objectData.samaccountname;
        }

        if (objectData.name) {
            return objectData.name;
        }

        if (objectData.group_name) {
            return objectData.group_name;
        }

        if (objectData.distinguished_name) {
            return objectData.distinguished_name;
        }

        if (objectData.dn) {
            return objectData.dn;
        }

        return JSON.stringify(
            objectData
        );
    };


    const handleConfirm = () => {
        if (
            approvalPolicy === "admin_secret"
        ) {
            setShowSecretInput(true);
            return;
        }

        if (
            approvalPolicy === "normal"
        ) {
            handleExecute();
            return;
        }

        console.warn(
            "Unknown approval_policy:",
            approvalPolicy
        );
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
                "MULTI EXECUTE RESULT",
                result
            );

        } catch (error) {
            console.error(
                "MULTI EXECUTE ERROR",
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
        <div className="multi-confirm-card">

            <div className="multi-confirm-header">

                <div className="multi-confirm-title">
                    Xác nhận thực hiện {action}
                </div>

                {
                    approvalPolicy === "admin_secret" && (
                        <div className="multi-confirm-secret-warning">
                            🔒 Yêu cầu Admin Secret
                        </div>
                    )
                }

            </div>

            <div className="multi-confirm-body">

                <div className="multi-confirm-section">
                {
                    Object.entries(
                        resolvedObjects
                    ).map(([objectType, objectData]) => (

                        <div
                            key={objectType}
                            className="multi-object-card"
                        >

                            <div className="multi-confirm-label">
                                {objectType}
                            </div>

                            <div className="multi-object-value">
                                {
                                    getObjectDisplayValue(
                                        objectType,
                                        objectData
                                    )
                                }
                            </div>

                        </div>

                    ))
                }

            </div>


                <div className="multi-confirm-section">
                    {
                        Object.entries(
                            payload
                        ).map(([key, value]) => (
                            <div
                                key={key}
                                className="multi-confirm-row"
                            >
                                <span className="multi-confirm-label">
                                    {formatLabel(key)}
                                </span>

                                <span className="multi-confirm-value">
                                    {String(value)}
                                </span>
                            </div>
                        ))
                    }
                </div>

            </div>


            {showSecretInput && (
                <div className="multi-secret-box">
                    <label className="multi-secret-label">
                        Admin Secret
                    </label>

                    <input
                        type="password"
                        value={secret}
                        className="multi-secret-input"
                        placeholder="Nhập admin secret..."
                        onChange={(e) =>
                            setSecret(e.target.value)
                        }
                    />
                </div>
            )}


            {completed && (
                <div className="multi-action-completed">
                    ✅ Đã thực hiện
                </div>
            )}


            {cancelled && (
                <div className="multi-action-cancelled">
                    🚫 Yêu cầu đã bị hủy
                </div>
            )}


            {!completed && !cancelled && (
                <div className="multi-confirm-actions">

                    {!showSecretInput && (
                        <button
                            className="multi-confirm-btn"
                            onClick={handleConfirm}
                            disabled={executing || completed}
                        >
                            {
                                executing
                                    ? "Đang xử lý..."
                                    : "Xác nhận"
                            }
                        </button>
                    )}

                    {showSecretInput && (
                        <button
                            className="multi-confirm-btn"
                            onClick={handleExecute}
                            disabled={
                                executing ||
                                completed ||
                                !secret.trim()
                            }
                        >
                            {
                                executing
                                    ? "Đang xử lý..."
                                    : "Thực hiện"
                            }
                        </button>
                    )}

                    <button
                        className="multi-cancel-btn"
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

export default MultiConfirmCard;