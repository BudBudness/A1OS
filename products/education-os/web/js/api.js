import { getToken, clearAuth } from "./auth.js";

const API_BASE = "/api";

async function request(path, options = {}) {
    const token = getToken();

    const response = await fetch(`${API_BASE}${path}`, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
            ...(options.headers || {})
        }
    });

    if (response.status === 401) {
        clearAuth();
        location.reload();
        throw new Error("Session expired");
    }

    let data = null;

    try {
        data = await response.json();
    } catch {
        data = null;
    }

    if (!response.ok) {
        const error = new Error(
            data?.detail || `API request failed: ${response.status}`
        );

        error.status = response.status;
        error.data = data;
        throw error;
    }

    return data;
}

export const api = {
    health: () => request("/health"),

    organization: {
        get: () => request("/organization")
    },

    students: {
        list: () => request("/students"),
        get: id => request(`/students/${id}`),
        create: data =>
            request("/students", {
                method: "POST",
                body: JSON.stringify(data)
            })
    },

    admissions: {
        list: () => request("/admissions"),
        get: id => request(`/admissions/${id}`),
        create: data =>
            request("/admissions", {
                method: "POST",
                body: JSON.stringify(data)
            })
    },

    fees: {
        list: () => request("/fees")
    },

    attendance: {
        list: () => request("/attendance")
    },

    operations: {
        list: () => request("/operations")
    }
};
