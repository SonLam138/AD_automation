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


    if (
        selectedRequest &&
        requestDetail
    ) 
    {
        return (

                <div>

        <h2>Request Review</h2>

        <p>
            Request ID:
            {requestDetail.request_id}
        </p>

        <p>
            Status:
            {requestDetail.status}
        </p>

        <hr/>

        <h3>HR Information</h3>

        <table border="1">

            <tbody>

                <tr>
                    <td>Employee ID</td>
                    <td>
                        {requestDetail.hr_input?.employee_id}
                    </td>
                </tr>

                <tr>
                    <td>Full Name</td>
                    <td>
                        {requestDetail.hr_input?.full_name}
                    </td>
                </tr>

                <tr>
                    <td>Position</td>
                    <td>
                        {requestDetail.hr_input?.title}
                    </td>
                </tr>

                <tr>
                    <td>Department</td>
                    <td>
                        {requestDetail.hr_input?.department}
                    </td>
                </tr>

                <tr>
                    <td>Division</td>
                    <td>
                        {requestDetail.hr_input?.division}
                    </td>
                </tr>

            </tbody>

        </table>

        <br />

        <h3>Resolver Result</h3>

        <table border="1">

            <tbody>

                                <tr>
                    <td>
                        DISPLAYNAME
                    </td>
                    <td>
                        {
                            editingField
                            ===
                            "display_name"
                            ?
                            <>
                                <input
                                    value={
                                        editableData
                                        ?.display_name || ""
                                    }
                                    style={{
                                        width: "80%"
                                    }}
                                    onChange={(e) =>

                                        setEditableData({

                                            ...editableData,

                                            display_name:
                                                e.target.value
                                        })
                                    }
                                />
                                <button
                                    onClick={() =>

                                        setEditingField(null)
                                    }
                                >
                                    Save
                                </button>
                            </>
                            :
                            <>
                                {
                                    editableData
                                    ?.display_name
                                }
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
                            </>
                        }
                    </td>
                </tr>

                <tr>
                    <td>
                        USERNAME
                    </td>
                    <td>
                        {
                            editingField
                            ===
                            "sam_account_name"
                            ?
                            <>
                                <input
                                    value={
                                        editableData
                                        ?.sam_account_name || ""
                                    }
                                    style={{
                                        width: "80%"
                                    }}
                                    onChange={(e) =>

                                        setEditableData({

                                            ...editableData,

                                            sam_account_name:
                                                e.target.value
                                        })
                                    }
                                />
                                <button
                                    onClick={() =>

                                        setEditingField(null)
                                    }
                                >
                                    Save
                                </button>
                            </>
                            :
                            <>
                                {
                                    editableData
                                    ?.sam_account_name
                                }
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
                            </>
                        }
                    </td>
                </tr>
                <tr>
                    <td>
                        TARGET OU
                    </td>
                    <td>
                        {
                            editingField
                            ===
                            "target_ou_dn"
                            ?
                            <>
                                <input
                                    value={
                                        editableData
                                        ?.target_ou_dn || ""
                                    }
                                    style={{
                                        width: "80%"
                                    }}
                                    onChange={(e) =>

                                        setEditableData({

                                            ...editableData,

                                            target_ou_dn:
                                                e.target.value
                                        })
                                    }
                                />
                                <button
                                    onClick={() =>

                                        setEditingField(null)
                                    }
                                >
                                    Save
                                </button>
                            </>
                            :
                            <>
                                {
                                    editableData
                                    ?.target_ou_dn
                                }
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
                            </>
                        }
                    </td>
                </tr>
                <tr>
                    <td>
                        MEMBER OF
                    </td>
                    <td>
                        {
                            editingField
                            ===
                            "groups"
                            ?
                            <>
                                <input
                                    value={
                                        editableData
                                        ?.groups || ""
                                    }
                                    style={{
                                        width: "80%"
                                    }}
                                    onChange={(e) =>

                                        setEditableData({

                                            ...editableData,

                                            groups:
                                                e.target.value
                                        })
                                    }
                                />
                                <button
                                    onClick={() =>

                                        setEditingField(null)
                                    }
                                >
                                    Save
                                </button>
                            </>
                            :
                            <>
                                {
                                    editableData
                                    ?.groups
                                }
                                {" "}
                                <button
                                    onClick={() =>

                                        setEditingField(
                                            "groups"
                                        )
                                    }

                                >
                                    Edit
                                </button>
                            </>
                        }
                    </td>
                </tr>      
            </tbody>

        </table>

        <br />

        <button
            onClick={handleApprove}
        >
            Approve
        </button>

        <button
            onClick={handleReject}
        >
            Reject
        </button>

        <button
            onClick={() => {
                setSelectedRequest(null);
                setRequestDetail(null);
            }}
        >
            Back
        </button>

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
    <div>

        <h2>Pending Requests</h2>

        <table border="1">

        <thead>
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
            <tr key={request.request_id}>

                <td>{request.request_id}</td>
                <td>{request.hr_input?.full_name}</td>

                <td>{request.hr_input?.title}</td>

                <td>{request.hr_input?.department}</td>

                <td>{request.hr_input?.division}</td>

                <td>{request.status}</td>

                <td>
                <button
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