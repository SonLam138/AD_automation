export function getCurrentUserName() {

    const token =
        localStorage.getItem(
            "access_token"
        );

    if (!token) {
        return "";
    }

    try {

        const payload = JSON.parse(
            atob(
                token.split(".")[1]
            )
        );

        return payload.name || "";

    } catch {

        return "";

    }

}