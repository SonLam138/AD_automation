import {
    Outlet,
    useNavigate,
    useLocation
} from "react-router-dom";

import "./PortalLayout.css";

export default function PortalLayout() {

    const navigate = useNavigate();
    const location = useLocation();

    const menuItems = [
        {
            key: "onboarding",
            label: "New Onboarding",
            path: "/portal/onboarding"
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

        localStorage.removeItem(
            "access_token"
        );

        localStorage.removeItem(
            "landing_page"
        );

        navigate("/login");
    };

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