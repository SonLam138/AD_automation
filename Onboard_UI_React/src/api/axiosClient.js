import axios from "axios";
import {
    clearAuthSession,
    getAccessTokenState,
    notifySessionInvalid,
} from "../components/authSession";

const axiosClient = axios.create({
    baseURL: "http://localhost:8000",
    headers: {
        "Content-Type": "application/json"
    }
});

axiosClient.interceptors.request.use(
    (config) => {

        const token =
            localStorage.getItem(
                "access_token"
            );

        if (token && getAccessTokenState() === "valid") {

            config.headers.Authorization =
                `Bearer ${token}`;
        } else if (token) {
            clearAuthSession();
            notifySessionInvalid();
        }

        return config;
    }
);

axiosClient.interceptors.response.use(
    (response) => response,
    (error) => {
        const requestUrl = error.config?.url || "";
        const isLoginRequest = requestUrl.includes(
            "/onboard_auth/login"
        );

        if (error.response?.status === 401 && !isLoginRequest) {
            clearAuthSession();
            notifySessionInvalid();
        }

        return Promise.reject(error);
    }
);

export default axiosClient;
