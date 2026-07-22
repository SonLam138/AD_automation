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
        "/api/move-user",
        payload
    );

    return response.data;
}