import {
    Routes,
    Route,
    Navigate
} from "react-router-dom";

import LoginPage from "./pages/LoginPage";

import PortalLayout from "./layouts/PortalLayout";

import WorkflowPage from "./pages/WorkflowPage";
import EmployeeOffboardingPage from "./pages/EmployeeOffboardingPage";
import AutomationToolsPage from "./pages/AutomationToolsPage";
import ReportingPage from "./pages/ReportingPage";
import AiLabPage from "./pages/AiLabPage";
import ChatPage from "./pages/ChatPage";
import MonitorDashboard from "./pages/MonitorDashboard";
import BulkOffboardingPage from "./pages/BulkOffboardingPage";

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

                {/* WorkFlow Engine */}
                <Route
                    path="workflow"
                    element={<WorkflowPage />}
                />
                <Route
                    path="workflow/offboarding"
                    element={
                        <EmployeeOffboardingPage />
                    }
                />
                <Route
                    path="workflow/bulk-offboarding"
                    element={
                        <BulkOffboardingPage />
                    }
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
                <Route
                    path="monitor"
                    element={<MonitorDashboard />}
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