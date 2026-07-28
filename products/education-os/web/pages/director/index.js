import { api } from "../../js/education-api.js";
import { user, can } from "../../js/auth.js";

export async function renderDirectorSuite() {
    const current = user();

    if (!can("director")) {
        return `
        <div class="error">
            <h2>Access denied</h2>
            <p>Director permissions required.</p>
        </div>`;
    }

    return `
    <div class="director-suite">
        <h2>Director Editing Suite</h2>
        <p>Welcome ${current?.full_name || "Director"}</p>

        <div class="director-grid">
            <button>School Profile</button>
            <button>Staff Management</button>
            <button>Students</button>
            <button>Admissions</button>
            <button>Announcements</button>
            <button>Montessori Records</button>
        </div>
    </div>`;
}
