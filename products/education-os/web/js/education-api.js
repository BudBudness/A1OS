import { getToken, clearAuth } from "./auth.js?v=1785434576";

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
  students: {
    create: async (payload) => request("/students", {
      method:"POST",
      body: JSON.stringify(payload)
    })
  },
  admissions: {
    create: async (payload) => request("/admissions", {
      method:"POST",
      body: JSON.stringify(payload)
    })
  },
  fees: {
    create: async (payload) => request("/fees", {
      method:"POST",
      body: JSON.stringify(payload)
    })
  },
  payments: {
    create: async (payload) => request("/payments", {
      method:"POST",
      body: JSON.stringify(payload)
    })
  },
  attendance: {
    createSession: async (payload) => request("/attendance/sessions", {
      method:"POST",
      body: JSON.stringify(payload)
    })
  },
  operations: {
    create: async (payload) => request("/operations", {
      method:"POST",
      body: JSON.stringify(payload)
    })
  },

    health: () => request("/health"),

    organization: {
        get: () => request("/organization")
    },

    students: {
        list: async () => {
            const data = await request("/students");
            return Array.isArray(data) ? data : (data.students || []);
        },
        get: id => request(`/students/${id}`),
        create: data =>
            request("/students", {
                method: "POST",
                body: JSON.stringify(data)
            })
    },

    admissions: {
        list: async () => {
            const data = await request("/admissions");
            return Array.isArray(data) ? data : (data.admissions || []);
        },
        get: id => request(`/admissions/${id}`),
        create: data =>
            request("/admissions", {
                method: "POST",
                body: JSON.stringify(data)
            })
    },

    fees: {
        list: async () => {
            const data = await request("/fees");
            return Array.isArray(data) ? data : (data.fees || []);
        }
    },

    attendance: {
        list: () => request("/attendance/sessions"),
        get: id => request(`/attendance/sessions/${id}`),
        createSession: data =>
            request("/attendance/sessions", {
                method: "POST",
                body: JSON.stringify(data)
            }),
        record: (sessionId, data) =>
            request(`/attendance/sessions/${sessionId}/records`, {
                method: "POST",
                body: JSON.stringify(data)
            })
    },

    operations: {
        list: async () => {
            const data = await request("/operations");
            return Array.isArray(data) ? data : (data.operations || []);
        }
    }
};


api.intelligence = {
  summary: () => request("/intelligence/summary"),
  staff: async () => {
    const data = await request("/staff");
    return Array.isArray(data) ? data : (data.staff || []);
  }
};
