import axiosClient from "../api/axiosClient";

export async function disableUser(payload) {

    const response = await axiosClient.post(
        "/api/ad/disable-user",
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