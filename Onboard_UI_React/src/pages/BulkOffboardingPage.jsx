import {
    useState
} from "react";
import axiosClient from "../api/axiosClient";

import "./BulkOffboardingPage.css"

export default function BulkOffboardingPage() {

    const [selectedFile,
        setSelectedFile] =
        useState(null);

    const [previewResult,
    setPreviewResult] =
    useState(null);

    const [confirmResult,
    setConfirmResult] =
    useState(null);

    const [confirmSuccess,
    setConfirmSuccess] =
    useState(false);

    const [confirmLoading,
    setConfirmLoading] =
    useState(false);



    // ==================================================
    // STATUS DISPLAY
    // ==================================================

    const getStatusLabel = (
        status
    ) => {

        const statusLabels = {

            VALID:
                "✅ Hợp lệ",

            MISSING_IDENTITY:
                "❌ Thiếu thông tin định danh",

            MISSING_REASON:
                "❌ Thiếu lý do",

            MISSING_EFFECTIVE_TIME:
                "❌ Thiếu thời điểm hiệu lực",

            NOT_FOUND:
                "❌ Không tìm thấy tài khoản",

            MULTIPLE_MATCH:
                "❌ Tìm thấy nhiều tài khoản",

            ALREADY_DISABLED:
                "⚠️ Tài khoản đã bị disable",

            LOOKUP_FAILED:
                "❌ Không thể tra cứu AD"
        };

        return (
            statusLabels[status]
            || status
            || "Không xác định"
        );
    };


    const getStatusClassName = (
        status
    ) => {

        if (
            status === "VALID"
        ) {
            return "review-status valid";
        }

        if (
            status === "ALREADY_DISABLED"
        ) {
            return "review-status warning";
        }

        return "review-status invalid";
    };


    const handleConfirm =
    async () => {

        try {

            setConfirmLoading(
                true
            );

            await axiosClient.post(

                "api/workflow/employee-offboarding/confirm",

                {
                    session_id:
                        previewResult.session_id
                }
            );

            setConfirmSuccess(
                true
            );

        } catch (error) {

            console.error(
                error
            );

        } finally {

            setConfirmLoading(
                false
            );
        }

    };

    const handlePreview = async () => {

        if (!selectedFile) {
            return;
        }

        const formData =
            new FormData();

        formData.append(
            "file",
            selectedFile
        );

        try {

            const response =
                await axiosClient.post(
                    "api/workflow/employee-offboarding/preview",
                    formData,
                    {
                        headers: {
                            "Content-Type":
                                "multipart/form-data"
                        }
                    }
                );

            setPreviewResult(
                response.data
            );

        } catch (error) {

            console.error(
                error
            );

        }

    };

    const handleFileChange = (
        event
    ) => {

        const file =
            event.target.files?.[0];

        if (!file) {
            return;
        }

        setSelectedFile(
            file
        );
        setPreviewResult(null);
    };

    return (

        <div>
            <div className="pharaoh-card">
                <h2>
                    Bulk Offboarding Import
                </h2>

                <p>
                    Upload danh sách nhân sự nghỉ việc
                    từ file Excel.
                </p>

                <input
                    type="file"
                    accept=".xlsx,.xls"
                    onChange={
                        handleFileChange
                    }
                />
                <button
                    onClick={
                        handlePreview
                    }
                >
                    Preview File
                </button>

                {
                    selectedFile && (
                        <div>

                            <p>
                                File:
                                {" "}
                                {
                                    selectedFile.name
                                }
                            </p>

                            <p>
                                Size:
                                {" "}
                                {
                                    selectedFile.size
                                }
                                {" "}
                                bytes
                            </p>

                        </div>
                    )}
            </div>
            {
                previewResult && (

                    <div className="pharaoh-card review-container">

                        {/* ======================================
                            REVIEW HEADER
                        ====================================== */}

                        <div
                            className={
                                previewResult.can_confirm
                                    ? "review-hero success"
                                    : "review-hero warning"
                            }
                        >

                            <h2>

                                {
                                    previewResult.can_confirm
                                        ? "✅ READY TO EXECUTE"
                                        : "⚠ REVIEW REQUIRED"
                                }

                            </h2>

                            <p>

                                {
                                    previewResult.can_confirm

                                    ? "All users passed validation and are ready for workflow creation."

                                    : `Found ${previewResult.invalid_rows} record(s) requiring attention.`
                                }

                            </p>

                        </div>


                        {/* ======================================
                            SUMMARY
                        ====================================== */}

                        <div className="summary-cards">

                            <div className="summary-card">

                                <span>Total</span>

                                <strong>
                                    {previewResult.total_rows}
                                </strong>

                            </div>

                            <div className="summary-card">

                                <span>Valid</span>

                                <strong>
                                    {previewResult.valid_rows}
                                </strong>

                            </div>

                            <div className="summary-card">

                                <span>Invalid</span>

                                <strong>
                                    {previewResult.invalid_rows}
                                </strong>

                            </div>

                        </div>


                        {/* ======================================
                            GLOBAL REVIEW MESSAGE
                        ====================================== */}

                        {
                            previewResult.can_confirm
                                ? (
                                    
                                    <div className="review-message success">

                                        <h4>
                                            ✅ Dữ liệu hợp lệ
                                        </h4>

                                        <p>
                                            Tất cả các dòng trong file
                                            đã được kiểm tra trên Active Directory.
                                        </p>

                                        <p>
                                            Có thể tiếp tục tạo
                                            Offboarding Requests.
                                        </p>

                                    </div>

                                )
                                : (

                                    <div className="review-message warning">

                                        <h4>
                                            ⚠️ Không thể tạo Requests
                                        </h4>

                                        <p>
                                            Phát hiện
                                            {" "}
                                            <strong>
                                                {
                                                    previewResult
                                                        .invalid_rows
                                                }
                                            </strong>
                                            {" "}
                                            dòng dữ liệu không hợp lệ.
                                        </p>

                                        <p>
                                            Vui lòng kiểm tra chi tiết
                                            bên dưới, sửa file Excel và
                                            thực hiện Preview lại.
                                        </p>

                                        <p>
                                            Không có tài khoản nào được
                                            thay đổi trong bước Review này.
                                        </p>

                                    </div>

                                )
                        }


                        {/* ======================================
                            REVIEW TABLE
                        ====================================== */}

                        {
                            previewResult.rows.some(
                                row =>
                                    row.status !== "VALID"
                            ) && (
                            <div>
                                <h3>
                                    Records Requiring Attention
                                </h3>
                                <div className="review-table-wrapper">

                                    <table className="review-table">

                                        <thead>

                                            <tr>

                                                <th>
                                                    Dòng
                                                </th>

                                                <th>
                                                    Employee ID
                                                </th>

                                                <th>
                                                    Email
                                                </th>

                                                <th>
                                                    Tài khoản AD
                                                </th>

                                                <th>
                                                    Display Name
                                                </th>

                                                <th>
                                                    Effective Time
                                                </th>

                                                <th>
                                                    Trạng thái
                                                </th>

                                                <th>
                                                    Chi tiết
                                                </th>

                                            </tr>

                                        </thead>

                                        <tbody>

                                        {
                                        previewResult.rows
                                            .filter(
                                                row =>
                                                    row.status !== "VALID"
                                            )
                                            .map(
                                                row => (

                                                <tr
                                                    key={
                                                        row.row_number
                                                    }
                                                >

                                                    <td>
                                                        {
                                                            row.row_number
                                                        }
                                                    </td>

                                                    <td>
                                                        {
                                                            row.employee_id
                                                            || "-"
                                                        }
                                                    </td>

                                                    <td>
                                                        {
                                                            row.email
                                                            || "-"
                                                        }
                                                    </td>

                                                    <td>
                                                        {
                                                            row
                                                                .sam_account_name
                                                            || "-"
                                                        }
                                                    </td>

                                                    <td>
                                                        {
                                                            row.display_name
                                                            || "-"
                                                        }
                                                    </td>

                                                    <td>
                                                        {
                                                            row.effective_time
                                                            || "-"
                                                        }
                                                    </td>

                                                    <td>

                                                        <span
                                                            className={
                                                                getStatusClassName(
                                                                    row.status
                                                                )
                                                            }
                                                        >
                                                            {
                                                                getStatusLabel(
                                                                    row.status
                                                                )
                                                            }
                                                        </span>

                                                    </td>

                                                    <td>
                                                        {
                                                            row.message
                                                            || "-"
                                                        }
                                                    </td>

                                                </tr>

                                                )
                                            )
                                        }

                                        </tbody>

                                    </table>
                                </div>
                            </div>
                            )
                        }


                        {/* ======================================
                            CONFIRM AREA
                        ====================================== */}

                        <div className="pharaoh-sub-card review-actions">

                            <button className="execute-button"
                                type="button"

                                disabled={
                                    confirmLoading
                                    ||
                                    confirmSuccess
                                    ||
                                    !previewResult?.can_confirm
                                }

                                onClick={
                                    handleConfirm
                                }
                            >
                                {
                                    confirmLoading
                                        ? "Creating Requests..."

                                        : confirmSuccess

                                            ? "✅ Requests Created"

                                            : `Create ${previewResult.valid_rows} Offboarding Requests`
                                }
                            </button>

                            {
                                confirmSuccess && (

                                    <div
                                        className="review-message success"
                                    >

                                        <h4>
                                            ✅ Offboarding Requests Created Successfully
                                        </h4>

                                        <p>
                                            Hệ thống đã tiếp nhận thành công file yêu cầu của bạn.
                                            Workflow Engine đã bắt đầu hoạt động.
                                        </p>

                                        <p>
                                            Để tạo thêm yêu cầu vui lòng upload thêm file mới.
                                        </p>

                                    </div>

                                )
                            }

                        </div>

                    </div>

                )
            }

        </div>

    );
}
