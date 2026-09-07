import axiosClient from "../api/axiosClient";

export async function disableUser(payload) {

    const response = await axiosClient.post(
        "/api/ad/disable-user",
        payload
    );

    return response.data;
}

export async function enableUser(payload) {

    const response = await axiosClient.post(
        "/api/ad/enable-user",
        payload
    );

    return response.data;
}

export async function addGroup(payload) {

    const response = await axiosClient.post(
        "/api/ad/add-group",
        payload
    );

    return response.data;
}

export async function removeGroup(payload) {

    const response = await axiosClient.post(
        "/api/ad/remove-group",
        payload
    );

    return response.data;
}

export async function moveUser(payload) {

    const response = await axiosClient.post(
        "/api/ad/move-user",
        payload
    );

    return response.data;
}

export async function verifySecret(secret) {

    const response =
        await axiosClient.post(
            "/api/ad/verify-admin-secret",
            {
                secret
            }
        );

    return response.data;
}

export async function disableComputer(
    payload
) {

    const response =
        await axiosClient.post(
            "/api/ad/disable-computer",
            payload
        );

    return response.data;
}

export async function updateUserDisplayName(
    payload
) {
    const response =
        await axiosClient.post(
            "/api/ad/update-user-displayname",
            payload
        );

    return response.data;
}

export async function updateUserIpPhone(
    payload
) {
    const response =
        await axiosClient.post(
            "/api/ad/update-user-ip-phone",
            payload
        );

    return response.data;
}



export async function updateUserDepartment(
    payload
) {
    const response =
        await axiosClient.post(
            "/api/ad/update-user-department",
            payload
        );

    return response.data;
}

export async function updateUserDescription(
    payload
) {
    const response =
        await axiosClient.post(
            "/api/ad/update-user-description",
            payload
        );

    return response.data;
}

export async function createEmployeeOffboarding(
    payload
) {

    const response =
        await axiosClient.post(
            "/api/workflow/employee-offboarding",
            payload
        );

    return response.data;
}

export async function analyzeOffboardingFile(
    file
) {

    const formData =
        new FormData();

    formData.append(
        "file",
        file
    );

    const response =
        await axiosClient.post(
            "/api/workflow/ra_soat/analyze",
            formData,
            {
                headers: {
                    "Content-Type":
                        "multipart/form-data"
                }
            }
        );

    return response.data;
}



export async function getWorkflowJournalList(
    payload
) {

    const response =
        await axiosClient.get(
            "/api/workflow/custom-workflow/journal",
            payload
        );

    return response.data;
}

export async function getWorkflowJournalDetail(
    journalId
) {
    const response =
        await axiosClient.get(
            `/api/workflow/custom-workflow/journal/${journalId}`
        );

    return response.data;
}

export async function deleteWorkflowJournal(
    journalId
) {
    const response =
        await axiosClient.delete(
            `/api/workflow/custom-workflow/journal/${journalId}`
        );

    return response.data;
}

export async function executeTempAccess(
    payload
) {
    const response =
        await axiosClient.post(
            "/api/workflow/temp-access",
            payload
        );

    return response.data;
}

export async function tempResolveObject(
    objectType,
    keyword
) {
    const response =
        await axiosClient.post(
            "/api/workflow/temp-resolve-object",
            {
                object_type:
                    objectType,

                keyword:
                    keyword,
            }
        );

    return response.data;
}

export async function confirmOffboardingReview(
    sessionId
) {
    const response =
        await axiosClient.post(
            "/api/workflow/employee-offboarding/confirm",
            {
                session_id: sessionId
            }
        );

    return response.data;
}

