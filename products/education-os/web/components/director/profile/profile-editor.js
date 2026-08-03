import { api } from "../../../js/education-api.js";

export async function renderProfileEditor() {

    const profile = await api.directorProfile.get();

    return `
    <div class="profile-editor">
        <h2>School Profile Editor</h2>

        <label>
            School Name
            <input id="school_name" value="${profile.school_name || ""}">
        </label>

        <label>
            Slogan
            <input id="slogan" value="${profile.slogan || ""}">
        </label>

        <label>
            Location
            <input id="location" value="${profile.location || ""}">
        </label>

        <label>
            Description
            <textarea id="description">${profile.description || ""}</textarea>
        </label>

        <button id="save-profile">
            Save Changes
        </button>
    </div>
    `;
}
