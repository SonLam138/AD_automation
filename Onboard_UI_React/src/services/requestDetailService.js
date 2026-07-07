import axiosClient from "../api/axiosClient";

export const getRequestDetail = async (
    requestId
) => {

    const response =
        await axiosClient.get(
            `/onboarding/requests/${requestId}`
        );

    return response.data;
};