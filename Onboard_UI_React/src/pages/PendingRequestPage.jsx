import { useEffect, useState }
    from "react";

import {
    getPendingRequests
}
from "../services/pendingRequestService";

import {
    getRequestDetail
}
from "../services/requestDetailService";

import {
    createUser,
    rejectRequest
}
from "../services/onboardingService";

function PendingRequestPage() {

    const [requests, setRequests]
        = useState([]);

    useEffect(() => {

        loadRequests();

    }, []);

        const [requestDetail,
            setRequestDetail]
            = useState(null);

    const handleReview = async (
        requestId
    ) => {

        try {

            const detail =
                await getRequestDetail(
                    requestId
                );

            console.log(detail);

            setRequestDetail(
                detail
            );

            setSelectedRequest(
                requestId
            );

        }
        catch(error){

            console.error(error);
        }
    };


const handleReject = async () => {

    try {

        await rejectRequest(

            requestDetail
            .request_id

        );

        alert(
            "Reject Success"
        );

        setSelectedRequest(
            null
        );

        setRequestDetail(
            null
        );

        loadPendingRequests();

    }
    catch(error){

        console.error(error);

        alert(
            "Reject Failed"
        );
    }
};

    const handleApprove = async () => {

        try {

        //    const edited_by_approver = editedByApprover;

            const hr =
                requestDetail.hr_input;

            const resolver =
                requestDetail.resolved_result;

            const editedByApprover =
            JSON.stringify(editableData)
            !==
            JSON.stringify({
                display_name:
                    resolver.display_name,

                sam_account_name:
                    resolver.sam_account_name,

                target_ou_dn:
                    resolver.target_ou_dn,

                groups:
                    resolver.groups
            });
            const nameParts =
                hr.full_name.trim().split(" ");

            const edited_by_approver = editedByApprover;

            const lastName =
                nameParts.pop();

            const firstName =
                nameParts.join(" ");

            const createUserRequest = {

                employee_id:
                    hr.employee_id,

                first_name:
                    firstName,

                last_name:
                    lastName,

                full_name:
                    hr.full_name,

                display_name:
                    editableData.display_name,

                sam_account_name:
                    editableData.sam_account_name,

                password:
                    "Welcome@123",

                target_ou_dn:
                    editableData.target_ou_dn,

                title:
                    hr.title,

                department:
                    resolver.department,

                description:
                    `Onboard ${hr.employee_id}`,

                dry_run: false,

                groups:
                Array.isArray(
                    editableData.groups
                )
                ?
                editableData.groups : [editableData.groups],
                edited_by_approver : edited_by_approver

            };

            console.log(
                "CREATE USER REQUEST"
            );

            console.log(
                createUserRequest
            );
            console.log(
                "GROUPS =",
                createUserRequest.groups
            );

            console.log(
                typeof createUserRequest.groups
            );
            const result =
            await createUser(
                createUserRequest
            );

            alert(
                "Approve Success"
            );

        }
        catch(error){

            console.error(error);

            alert(
                "Approve Failed"
            );
        }
    };

    // ------------------------------------------------
    const [selectedRequest,
       setSelectedRequest]
    = useState(null);
    
    const [editableData,
        setEditableData]
    = useState(null);
    const [editingField,
        setEditingField]
    = useState(null);

    useEffect(() => {

        if (!requestDetail)
            return;

        setEditableData({

            display_name:
                requestDetail
                .resolved_result
                ?.display_name,

            sam_account_name:
                requestDetail
                .resolved_result
                ?.sam_account_name,

            target_ou_dn:
                requestDetail
                .resolved_result
                ?.target_ou_dn,

            groups:
                requestDetail
                .resolved_result
                ?.groups || []
        });

    }, [requestDetail]);

//// Render ////
    if (selectedRequest && requestDetail)
    {
        const cardStyle = {
            background: "#FFFDF7",
            border: "1px solid #D4AF37",
            borderRadius: "14px",
            padding: "20px",
            color: "#222",
            textAlign: "left",
            flex: 1,
            boxShadow: "0 4px 12px rgba(0,0,0,0.08)"
        };

        const labelStyle = {
            fontSize: "12px",
            fontWeight: "700",
            color: "#B8860B",
            textTransform: "uppercase",
            marginBottom: "4px"
        };

        const valueStyle = {
            fontSize: "15px",
            color: "#222",
            marginBottom: "16px",
            wordBreak: "break-word"
        };

        const nameParts =
            requestDetail.hr_input?.full_name
                ?.trim()
                .split(" ") || [];

        const lastName =
            nameParts.length > 0
                ? nameParts[nameParts.length - 1]
                : "";

        const firstName =
            nameParts.length > 1
                ? nameParts.slice(0, -1).join(" ")
                : "";

        return (
            <div
                style={{
                    maxWidth: "1400px",
                    margin: "0 auto",
                    padding: "20px",
                    background: "#F8F6F0",
                    minHeight: "100vh"
                }}
            >
                {/* HEADER */}

                <div
                    style={{
                        background:
                            "linear-gradient(135deg,#F4D06F,#D4AF37)",
                        color: "#222",
                        padding: "24px",
                        borderRadius: "16px",
                        marginBottom: "24px",
                        boxShadow: "0 6px 16px rgba(0,0,0,0.15)"
                    }}
                >
                    <h2
                        style={{
                            margin: 0,
                            fontSize: "28px"
                        }}
                    >
                        {requestDetail.hr_input?.full_name}
                    </h2>

                    <div
                        style={{
                            marginTop: "10px"
                        }}
                    >
                        <strong>Employee ID:</strong>{" "}
                        {requestDetail.hr_input?.employee_id}
                    </div>

                    <div
                        style={{
                            marginTop: "4px"
                        }}
                    >
                        <strong>Status:</strong>{" "}
                        {requestDetail.status}
                    </div>
                </div>

                {/* 2 COLUMNS */}

                <div
                    style={{
                        display: "flex",
                        gap: "20px",
                        alignItems: "flex-start"
                    }}
                >
                    {/* HCM */}

                    <div style={cardStyle}>
                        <h3
                            style={{
                                color: "#B8860B",
                                marginTop: 0,
                                borderBottom:
                                    "2px solid #D4AF37",
                                paddingBottom: "10px"
                            }}
                        >
                            Thông tin nhân sự từ HCM
                        </h3>

                        <div style={labelStyle}>
                            Họ và tên
                        </div>
                        <div style={valueStyle}>
                            {requestDetail.hr_input?.full_name}
                        </div>

                        <div style={labelStyle}>
                            Mã nhân viên
                        </div>
                        <div style={valueStyle}>
                            {requestDetail.hr_input?.employee_id}
                        </div>

                        <div style={labelStyle}>
                            Chức danh
                        </div>
                        <div style={valueStyle}>
                            {requestDetail.hr_input?.title}
                        </div>

                        <div style={labelStyle}>
                            Phòng/Ban
                        </div>
                        <div style={valueStyle}>
                            {requestDetail.hr_input?.department}
                        </div>

                        <div style={labelStyle}>
                            Khối
                        </div>
                        <div style={valueStyle}>
                            {requestDetail.hr_input?.division}
                        </div>
                    </div>

                    {/* AD */}

                    <div style={cardStyle}>
                        <h3
                            style={{
                                color: "#B8860B",
                                marginTop: 0,
                                borderBottom:
                                    "2px solid #D4AF37",
                                paddingBottom: "10px"
                            }}
                        >
                            Thông tin tạo tài khoản
                        </h3>

                        <div style={labelStyle}>
                            firstName
                        </div>
                        <div style={valueStyle}>
                            {firstName}
                        </div>

                        <div style={labelStyle}>
                            lastName
                        </div>
                        <div style={valueStyle}>
                            {lastName}
                        </div>

                        {/* DISPLAY NAME */}

                        <div style={labelStyle}>
                            displayName
                        </div>

                        <div style={valueStyle}>
                            {editableData?.display_name}
                            {" "}
                            <button
                                onClick={() =>
                                    setEditingField(
                                        "display_name"
                                    )
                                }
                            >
                                Edit
                            </button>
                        </div>

                        {/* USERNAME */}

                        <div style={labelStyle}>
                            Username
                        </div>

                        <div style={valueStyle}>
                            {editableData?.sam_account_name}
                            {" "}
                            <button
                                onClick={() =>
                                    setEditingField(
                                        "sam_account_name"
                                    )
                                }
                            >
                                Edit
                            </button>
                        </div>

                        {/* TARGET OU */}

                        <div style={labelStyle}>
                            targetOU
                        </div>

                        <div style={valueStyle}>
                            {editableData?.target_ou_dn}
                            {" "}
                            <button
                                onClick={() =>
                                    setEditingField(
                                        "target_ou_dn"
                                    )
                                }
                            >
                                Edit
                            </button>
                        </div>

                        {/* GROUPS */}

                        <div style={labelStyle}>
                            memberOf
                        </div>

                        <div style={valueStyle}>
                            {Array.isArray(
                                editableData?.groups
                            )
                                ? editableData.groups.map(
                                    (group) => (
                                        <span
                                            key={group}
                                            style={{
                                                display:
                                                    "inline-block",
                                                background:
                                                    "#D4AF37",
                                                color:
                                                    "#222",
                                                borderRadius:
                                                    "20px",
                                                padding:
                                                    "6px 12px",
                                                margin:
                                                    "4px",
                                                fontSize:
                                                    "12px",
                                                fontWeight:
                                                    "600"
                                            }}
                                        >
                                            {group}
                                        </span>
                                    )
                                )
                                : editableData?.groups}
                        </div>
                    </div>
                </div>

                {/* BUTTONS */}

                <div
                    style={{
                        marginTop: "24px",
                        display: "flex",
                        gap: "10px"
                    }}
                >
                    <button
                        onClick={handleApprove}
                        style={{
                            background: "#D4AF37",
                            color: "#222",
                            border: "none",
                            padding: "12px 24px",
                            borderRadius: "8px",
                            cursor: "pointer",
                            fontWeight: "700"
                        }}
                    >
                        Approve
                    </button>

                    <button
                        onClick={handleReject}
                        style={{
                            background: "#B22222",
                            color: "white",
                            border: "none",
                            padding: "12px 24px",
                            borderRadius: "8px",
                            cursor: "pointer"
                        }}
                    >
                        Reject
                    </button>

                    <button
                        onClick={() => {
                            setSelectedRequest(null);
                            setRequestDetail(null);
                        }}
                        style={{
                            background: "#666",
                            color: "white",
                            border: "none",
                            padding: "12px 24px",
                            borderRadius: "8px",
                            cursor: "pointer"
                        }}
                    >
                        Back
                    </button>
                </div>
            </div>
        );
    }



    const loadRequests = async () => {

        try {

            const data =
                await getPendingRequests();

            console.log(data);

            setRequests(data);

        }
        catch(error){

            console.error(error);
        }
    }

    return (
    <div
        style={{
            maxWidth:"1400px",
            margin:"0 auto",
            padding:"20px",
            background:"#F8F6F0",
            minHeight:"100vh"
        }}
    >

        <div
            style={{
                background:
                    "linear-gradient(135deg,#F4D06F,#D4AF37)",
                color:"#222",
                padding:"20px",
                borderRadius:"16px",
                marginBottom:"20px",
                boxShadow:
                    "0 6px 16px rgba(0,0,0,0.15)"
            }}
        >
            <h2
                style={{
                    margin:0
                }}
            >
                📋 Pending Requests
            </h2>

            <div
                style={{
                    marginTop:"6px"
                }}
            >
                Total Requests :
                {requests.length}
            </div>
        </div>


        <table
        style={{
            width:"100%",
            borderCollapse:"collapse",
            background:"#FFFDF7",
            borderRadius:"12px",
            overflow:"hidden",
            boxShadow:
                "0 4px 12px rgba(0,0,0,0.08)"
        }}
    >

        <thead
        style={{
            background:"#D4AF37",
            color:"#222"
        }}
    >
            <tr>
            <th>Request ID</th>
            <th>Họ tên</th>
            <th>Chức danh</th>
            <th>Phòng ban</th>
            <th>Khối</th>
            <th>Status</th>
            <th>Action</th>
            </tr>
        </thead>

        <tbody>

            {requests.map((request) => (
                console.log(request),
            <tr
                key={request.request_id}
                style={{
                    borderBottom:
                        "1px solid #e5e5e5"
                }}
            >

                <td
                    style={{
                        padding:"12px"
                    }}
                >
                    {request.request_id}
                </td>
                <td
                    style={{
                        padding:"12px"
                    }}
                >
                    {request.hr_input?.full_name}
                </td>                
                <td
                    style={{
                        padding:"12px"
                    }}
                >
                    {request.hr_input?.title}
                </td>      
                <td
                    style={{
                        padding:"12px"
                    }}
                >
                    {request.hr_input?.department}
                </td>
                <td
                    style={{
                        padding:"12px"
                    }}
                >
                    {request.hr_input?.division}
                </td>
                    <td style={{padding:"12px"}}>
                    <span
                        style={{
                            background:"#0e0b02",
                            color:"#f8ca55",
                            padding:"5px 10px",
                            borderRadius:"999px",
                            fontSize:"12px",
                            fontWeight:"700"
                        }}
                    >
                        {request.status}
                    </span>
                </td>
                <td>
                <button
                    style={{
                        background:"#D4AF37",
                        color:"#222",
                        border:"none",
                        padding:"8px 16px",
                        borderRadius:"8px",
                        cursor:"pointer",
                        fontWeight:"600"
                    }}
                    onClick={() =>
                        handleReview(
                            request.request_id
                        )
                    }
                >
                    Review
                </button>
                </td>

            </tr>
            
            ))}
        
        </tbody>

        </table>

    </div>
    );
}
export default PendingRequestPage;