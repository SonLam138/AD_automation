import axiosClient from "../api/axiosClient";

export const createUser = async (
    createUserRequest
) => {

    const response =
        await axiosClient.post(
            "/onboarding/new",
            createUserRequest
        );

    return response.data;
};

export const rejectRequest = async (
    requestId
) => {

    return await axiosClient.post(
        `/onboarding/requests/${requestId}/reject`
    );

};