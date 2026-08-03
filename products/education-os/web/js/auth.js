const AUTH_KEY = "little_oaks_auth";

export function getAuth() {
    try {
        return JSON.parse(localStorage.getItem(AUTH_KEY) || "null");
    } catch {
        return null;
    }
}

export function getToken() {
    return getAuth()?.token || null;
}

export function isAuthenticated() {
    return Boolean(getToken());
}

export function setAuth(data) {
    localStorage.setItem(AUTH_KEY, JSON.stringify(data));
    localStorage.setItem("little_oaks_access_token", data.token);
    localStorage.setItem("little_oaks_education_os_token", data.token);
    localStorage.setItem("a1os_access_token", data.token);
    localStorage.setItem("a1os_token", data.token);
    localStorage.setItem("access_token", data.token);
}

export function clearAuth() {
    localStorage.removeItem(AUTH_KEY);
}

export function user() {
    return getAuth()?.user || null;
}

export function hasPermission(permission) {
    const permissions = user()?.permissions || [];
    return permissions.includes("*") || permissions.includes(permission);
}

export async function login(email, password) {
    const response = await fetch("http://127.0.0.1:3011/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || "Authentication failed");
    }

    setAuth(data);
    return data;
}

export async function verifySession() {
    const auth = getAuth();
    return auth && auth.token ? auth : null;
}


export function logout() {
    clearAuth();
    location.reload();
}


export function can(permission) {
    const current = user();
    if (!current) return false;

    const role = String(current.role || "").toLowerCase();

    if (role === "director" || role === "director_ceo" || role === "director_ceo_teacher" || role === "ceo") {
        return true;
    }

    const permissions = {
        "head_mistress": [
            "academic",
            "headmistress",
            "curriculum.manage",
            "lesson.review",
            "operations",
            "staff.manage",
            "staff.view",
            "students",
            "admissions",
            "attendance",
            "staff",
            "reports"
        ],
        "staff": [
            "students",
            "attendance",
            "operations"
        ]
    };

    return (permissions[role] || []).some(
        item => permission === item || permission.startsWith(item + ".")
    );
}
