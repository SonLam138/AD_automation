import { useEffect, useState } from "react";
import {
    Outlet,
    useNavigate,
    useLocation,
    Navigate,
} from "react-router-dom";
import {
    clearAuthSession,
    getAccessTokenExpiry,
    getAccessTokenState,
} from "../components/authSession";

import "./PortalLayout.css";

export default function PortalLayout() {

    const navigate = useNavigate();
    const location = useLocation();
    const [sessionValid, setSessionValid] = useState(
        () => getAccessTokenState() === "valid"
    );

    useEffect(() => {
        let expiryTimer;

        const checkSession = () => {
            const tokenState = getAccessTokenState();
            if (tokenState !== "valid") {
                clearAuthSession();
                setSessionValid(false);
                return;
            }

            setSessionValid(true);

            const expiry = getAccessTokenExpiry();
            if (expiry !== null) {
                expiryTimer = window.setTimeout(
                    checkSession,
                    Math.max(0, expiry - Date.now())
                );
            }
        };

        const handleInvalidSession = () => {
            clearAuthSession();
            setSessionValid(false);
            navigate("/login", {
                replace: true,
                state: { sessionExpired: true },
            });
        };

        const handleStorageChange = (event) => {
            if (event.key === "access_token") {
                checkSession();
            }
        };

        checkSession();
        window.addEventListener(
            "auth:session-invalid",
            handleInvalidSession
        );
        window.addEventListener("storage", handleStorageChange);
        window.addEventListener("focus", checkSession);
        document.addEventListener(
            "visibilitychange",
            checkSession
        );

        return () => {
            window.clearTimeout(expiryTimer);
            window.removeEventListener(
                "auth:session-invalid",
                handleInvalidSession
            );
            window.removeEventListener(
                "storage",
                handleStorageChange
            );
            window.removeEventListener("focus", checkSession);
            document.removeEventListener(
                "visibilitychange",
                checkSession
            );
        };
    }, [navigate]);

    const menuItems = [

        {
            key: "monitor",
            label: "Monitor Dashboard",
            path: "/portal/monitor"
        },
        {
            key: "workflow",
            label: "Workflow Engine",
            path: "/portal/workflow"
        },
        {
            key: "automation-tools",
            label: "Automation Tools",
            path: "/portal/automation-tools"
        },
        {
            key: "reporting",
            label: "Reporting & Auditing",
            path: "/portal/reporting"
        },
        {
            key: "ai-lab",
            label: "Trải nghiệm ngáo",
            path: "/portal/ai-lab"
        }
    ];

    const handleLogout = () => {

        clearAuthSession();

        navigate("/login");
    };

    if (!sessionValid) {
        return (
            <Navigate
                to="/login"
                replace
                state={{ sessionExpired: true }}
            />
        );
    }

    return (

        <div className="portal-layout">

            {/* Header */}
            <header className="portal-header">

                <div className="portal-title">
                    AD Automation Portal
                </div>

                <div className="portal-user">

                    <span>
                        Xin chào
                    </span>

                    <button
                        className="logout-btn"
                        onClick={handleLogout}
                    >
                        Logout
                    </button>

                </div>

            </header>

            {/* Body */}
            <div className="portal-body">

                {/* Sidebar */}
                <aside className="portal-sidebar">

                    <div className="sidebar-group-title">

                        AD AUTOMATION
                        <br />
                        FRAMEWORK

                    </div>

                    <div className="sidebar-menu">

                        {menuItems.map((item) => {

                            const active =
                                location.pathname === item.path;

                            return (
                                <button
                                    key={item.key}
                                    className={
                                        active
                                            ? "menu-item active"
                                            : "menu-item"
                                    }
                                    onClick={() =>
                                        navigate(
                                            item.path
                                        )
                                    }
                                >
                                    {item.label}
                                </button>
                            );
                        })}

                    </div>

                </aside>

                {/* Content */}

                <main className="portal-content">

                    <Outlet />

                </main>

            </div>

        </div>

    );
}