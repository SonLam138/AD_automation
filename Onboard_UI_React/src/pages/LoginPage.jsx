import { useState } from "react";
import axiosClient from "../api/axiosClient";
import { useNavigate } from "react-router-dom";
import "./LoginPage.css";
function LoginPage() {
    const navigate = useNavigate();
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    // const [loginSuccess, setLoginSuccess]
    // = useState(false);
    const [loginFailed, setLoginFailed]
    = useState(false);
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
        localStorage.setItem(
            "access_token",
            token
        );

        navigate(
            "/portal/automation-tools"
        );

    } catch (error) {
        setLoginFailed(true);
        console.log("ERROR");
        console.log(error);

    }
};

    return (

        <div className="login-page">

            <div className="login-card">

                <div className="login-header">

                    <h1>
                        AD Automation Platform
                    </h1>

                    <p>
                        Active Directory Automation Assistant
                    </p>

                </div>

                <form
                    className="login-form"
                    onSubmit={(e) => {
                        e.preventDefault();
                        handleLogin();
                    }}
                >

                    <label>
                        Username
                    </label>

                    <input
                        type="text"
                        value={username}
                        onChange={(e) =>
                            setUsername(
                                e.target.value
                            )
                        }
                    />

                    <label>
                        Password
                    </label>

                    <input
                        type="password"
                        value={password}
                        onChange={(e) =>
                            setPassword(
                                e.target.value
                            )
                        }
                    />

                    {loginFailed && (

                        <div className="login-error">
                            Đăng nhập thất bại
                        </div>

                    )}

                    <button type="submit">
                        Sign In
                    </button>

                </form>

                <div className="login-footer">
                    Enterprise Team Pharaoh Edition • Internal Use Only
                </div>

            </div>

        </div>

    );
}

export default LoginPage;