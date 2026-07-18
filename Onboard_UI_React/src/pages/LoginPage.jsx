import { useState } from "react";
import axiosClient from "../api/axiosClient";
import DashboardPage from "./PendingRequestPage";

function LoginPage() {

    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [loginSuccess, setLoginSuccess]
    = useState(false);
    const [loginFailed, setLoginFailed]
    = useState(false);
    if (loginSuccess) {

    return (
        <DashboardPage />
        );
    }
    const handleLogin = async () => {

    try {
        const response =
            await axiosClient.post(
                "/onboard_auth/login",
                {
                    username,
                    password
                }
            );
        
        const token = response.data.access_token;

        const landingPage =
            response.data.landing_page;

        localStorage.setItem(
            "access_token",
            token
        );

        localStorage.setItem(
            "landing_page",
            landingPage
        );

        setLoginSuccess(true);

        console.log("TOKEN SAVED");

        alert("LOGIN SUCCESS");

    } catch (error) {
        setLoginFailed(true);
        console.log("ERROR");
        console.log(error);

        alert("LOGIN FAILED");
    }
};

    return (
        <div style={{ padding: "20px" }}>
            <h2>Onboarding Approval Login</h2>

            <div>
                <label>Username</label>
                <br />
                <input
                    type="text"
                    value={username}
                    onChange={(e) =>
                        setUsername(e.target.value)
                    }
                />
            </div>

            <br />

            <div>
                <label>Password</label>
                <br />
                <input
                    type="password"
                    value={password}
                    onChange={(e) =>
                        setPassword(e.target.value)
                    }
                />
            </div>

            <br />

            <button onClick={handleLogin}>
                Login
                {
                    loginFailed &&
                    (
                        <p
                            style={{
                                color: "red"
                            }}
                        >
                            Login Failed
                        </p>
                    )
                }
            </button>
        </div>
    );
}

export default LoginPage;