import axiosClient from "../api/axiosClient";
const API_URL = "http://localhost:8000";

export async function sendMessage(
    message
) {

    const response =
        await axiosClient.post(
            "/api/chat/message",
            {
                message
            }
        );

    console.log(
    "API RESPONSE =",
    response.data
    );

    return response.data;
}