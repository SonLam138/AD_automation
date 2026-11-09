const ACCESS_TOKEN_KEY = "access_token";

export function getAccessTokenState() {
    const token = localStorage.getItem(ACCESS_TOKEN_KEY);
    if (!token) {
        return "missing";
    }

    try {
        const payloadPart = token.split(".")[1];
        if (!payloadPart) {
            return "invalid";
        }

        const normalizedPayload = payloadPart
            .replace(/-/g, "+")
            .replace(/_/g, "/");
        const paddedPayload = normalizedPayload.padEnd(
            Math.ceil(normalizedPayload.length / 4) * 4,
            "="
        );
        const payload = JSON.parse(atob(paddedPayload));

        if (
            typeof payload.exp !== "number"
            || payload.exp * 1000 <= Date.now()
        ) {
            return "expired";
        }

        return "valid";
    } catch {
        return "invalid";
    }
}

export function getAccessTokenExpiry() {
    const token = localStorage.getItem(ACCESS_TOKEN_KEY);
    if (!token) {
        return null;
    }

    try {
        const payloadPart = token.split(".")[1];
        if (!payloadPart) {
            return null;
        }

        const normalizedPayload = payloadPart
            .replace(/-/g, "+")
            .replace(/_/g, "/");
        const paddedPayload = normalizedPayload.padEnd(
            Math.ceil(normalizedPayload.length / 4) * 4,
            "="
        );
        const payload = JSON.parse(atob(paddedPayload));

        return typeof payload.exp === "number"
            ? payload.exp * 1000
            : null;
    } catch {
        return null;
    }
}

export function clearAuthSession() {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem("landing_page");
}

export function notifySessionInvalid() {
    window.dispatchEvent(
        new CustomEvent("auth:session-invalid")
    );
}
