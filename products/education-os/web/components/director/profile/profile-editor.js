export function renderProfileEditor(org = {}) {
    return `
    <div class="director-profile-editor">
        <h2>School Profile</h2>

        <label>
            School Name
            <input id="school-name" value="${org.name || ""}">
        </label>

        <label>
            Motto
            <input id="school-motto" value="${org.motto || ""}">
        </label>

        <label>
            Address
            <input id="school-address" value="${org.address || ""}">
        </label>

        <button id="save-profile">
            Save Changes
        </button>
    </div>
    `;
}
