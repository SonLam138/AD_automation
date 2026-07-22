import {
    Routes,
    Route,
    Navigate
} from "react-router-dom";

import LoginPage from "./pages/LoginPage";

import PortalLayout from "./layouts/PortalLayout";

import OnboardingPage from "./pages/OnboardingPage";
import AutomationToolsPage from "./pages/AutomationToolsPage";
import ReportingPage from "./pages/ReportingPage";
import AiLabPage from "./pages/AiLabPage";
import ChatPage from "./pages/ChatPage";

function App() {

    return (

        <Routes>

            {/* Default Route */}
            <Route
                path="/"
                element={
                    <Navigate to="/login" />
                }
            />

            {/* Login */}
            <Route
                path="/login"
                element={<LoginPage />}
            />

            {/* Portal */}
            <Route
                path="/portal"
                element={<PortalLayout />}
            >

                {/* Default Portal Page */}
                <Route
                    index
                    element={
                        <Navigate
                            to="automation-tools"
                        />
                    }
                />

                {/* New Onboarding */}
                <Route
                    path="onboarding"
                    element={<OnboardingPage />}
                />

                {/* Automation Tools */}
                <Route
                    path="automation-tools"
                    element={
                        <AutomationToolsPage />
                    }
                />

                {/* Reporting */}
                <Route
                    path="reporting"
                    element={<ReportingPage />}
                />

                {/* Ngao */}
                <Route
                    path="ai-lab"
                    element={<AiLabPage />}
                />

                <Route
                    path="assistant"
                    element={<ChatPage />}
                />

            </Route>

        </Routes>

    );
}

export default App;