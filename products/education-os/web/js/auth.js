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
    const response = await fetch("/api/auth/login", {
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
    const token = getToken();

    if (!token) return null;

    const response = await fetch("/api/auth/me", {
        headers: {
            Authorization: `Bearer ${token}`
        }
    });

    if (!response.ok) {
        clearAuth();
        return null;
    }

    const data = await response.json();

    const current = getAuth();
    setAuth({
        ...current,
        user: data.user
    });

    return data;
}

export function logout() {
    clearAuth();
    location.reload();
}
