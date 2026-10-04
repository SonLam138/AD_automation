import axiosClient from "../api/axiosClient";

export const getPendingRequests = async () => {

    const response = await axiosClient.get(
        "onboarding/requests/pending"
    );

    return response.data;
};
