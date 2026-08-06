import { api } from "../js/education-api.js";
import { DEFAULT_CONTENT, mergeSiteContent, refreshSiteContent } from "../js/site-content.js";

function esc(value) {
    return String(value ?? "").replace(/[&<>"']/g, ch => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    })[ch]);
}

function checkbox(value) {
    return value ? " checked" : "";
}

function textField(field, value, label, options = {}) {
    return `
        <div class="form-group">
            <label>${label}</label>
            <input
                data-field="${field}"
                type="${options.password ? "password" : "text"}"
                value="${esc(value)}"
                ${options.required ? "required" : ""}
            />
        </div>
    `;
}

function textArea(field, value, label, rows = 3) {
    return `
        <div class="form-group">
            <label>${label}</label>
            <textarea data-field="${field}" rows="${rows}">${esc(value)}</textarea>
        </div>
    `;
}

function enabledField(field, value, label) {
    return `
        <label class="cms-check">
            <input type="checkbox" data-field="${field}"${checkbox(value)} /> ${label}
        </label>
    `;
}

function stringList(listKey, items) {
    return `
        <div class="cms-list" data-list="${listKey}">
            ${items.map(item => `
                <div class="cms-list-row" data-row>
                    <input data-item value="${esc(item)}" placeholder="Item" />
                    <button type="button" class="btn btn-secondary btn-sm cms-remove" data-remove>Remove</button>
                </div>
            `).join("")}
        </div>
        <button type="button" class="btn btn-secondary btn-sm cms-add" data-add="${listKey}">Add item</button>
    `;
}

function pairList(listKey, items) {
    return `
        <div class="cms-list" data-list="${listKey}" data-pair="true">
            ${items.map(item => `
                <div class="cms-list-row cms-pair" data-row>
                    <input data-item-label value="${esc(item.label)}" placeholder="Caption" />
                    <input data-item-url value="${esc(item.url || "")}" placeholder="Image path or URL (optional)" />
                    <button type="button" class="btn btn-secondary btn-sm cms-remove" data-remove>Remove</button>
                </div>
            `).join("")}
        </div>
        <button type="button" class="btn btn-secondary btn-sm cms-add" data-add="${listKey}" data-pair="true">Add photo</button>
    `;
}

function subBlock(name, label, block) {
    return `
        <div class="cms-sub" data-sub="${name}">
            <h4>${label}</h4>
            ${textField("title", block.title, "Title")}
            ${textField("ages", block.ages, "Ages")}
            ${textArea("description", block.description, "Description", 2)}
            <label class="cms-label">Focus areas</label>
            ${stringList(`prog-${name}-items`, block.items)}
        </div>
    `;
}

export async function renderWebsitePage() {
    try {
        const data = await api.siteContent.get();
        const c = mergeSiteContent(data?.sections);

        return `
            <div class="page-header">
                <div>
                    <span class="eyebrow">Public Website</span>
                    <h2>Website Content</h2>
                    <p class="page-subtitle">
                        Manage the public Little Oaks website. Changes appear on the
                        public pages immediately &mdash; no code changes required.
                    </p>
                </div>
                <button class="btn btn-primary" type="submit" form="website-form" id="cms-save-top">
                    Save changes
                </button>
            </div>

            <div id="cms-status" class="cms-status" hidden></div>

            <form id="website-form" class="cms-form">
                <section class="card cms-section" data-section="homepage_announcement">
                    <h3>Homepage Announcement</h3>
                    ${enabledField("enabled", c.homepage_announcement.enabled, "Show announcement on the homepage")}
                    ${textField("title", c.homepage_announcement.title, "Title")}
                    ${textArea("body", c.homepage_announcement.body, "Body", 2)}
                </section>

                <section class="card cms-section" data-section="about">
                    <h3>About Us</h3>
                    ${textArea("intro", c.about.intro, "Introduction", 4)}
                    ${textArea("mission", c.about.mission, "Mission", 3)}
                    ${textArea("philosophy", c.about.philosophy, "Montessori philosophy", 3)}
                    <label class="cms-label">Highlights</label>
                    ${stringList("about-highlights", c.about.highlights)}
                </section>

                <section class="card cms-section" data-section="approach">
                    <h3>Our Approach</h3>
                    ${textField("title", c.approach.title, "Title")}
                    ${textArea("body", c.approach.body, "Body", 3)}
                </section>

                <section class="card cms-section" data-section="programmes">
                    <h3>Programmes</h3>
                    ${subBlock("day_care", "Day Care", c.programmes.day_care)}
                    ${subBlock("kindergarten", "Kindergarten", c.programmes.kindergarten)}
                </section>

                <section class="card cms-section" data-section="sports_skills">
                    <h3>Talents, Sports &amp; Skills</h3>
                    <label class="cms-label">Sports</label>
                    ${stringList("sports-sports", c.sports_skills.sports)}
                    <label class="cms-label">Brain Games</label>
                    ${stringList("sports-brain", c.sports_skills.brain_games)}
                    <label class="cms-label">Life Skills</label>
                    ${stringList("sports-life", c.sports_skills.life_skills)}
                    <label class="cms-label">Enrichment</label>
                    ${stringList("sports-enrich", c.sports_skills.enrichment)}
                </section>

                <section class="card cms-section" data-section="admissions_notice">
                    <h3>Admissions Notice</h3>
                    ${enabledField("enabled", c.admissions_notice.enabled, "Show notice on the Admissions page")}
                    ${textField("title", c.admissions_notice.title, "Title")}
                    ${textArea("body", c.admissions_notice.body, "Body", 2)}
                </section>

                <section class="card cms-section" data-section="location">
                    <h3>Location</h3>
                    ${textField("place", c.location.place, "Place name")}
                    <label class="cms-label">Address lines</label>
                    ${stringList("location-details", c.location.details)}
                    ${textField("maps_url", c.location.maps_url, "Google Maps URL")}
                </section>

                <section class="card cms-section" data-section="contact">
                    <h3>Contact</h3>
                    <label class="cms-label">Phone numbers</label>
                    ${stringList("contact-phones", c.contact.phones)}
                    ${textField("whatsapp", c.contact.whatsapp, "WhatsApp number")}
                    ${textField("email", c.contact.email, "Email")}
                    ${textField("address", c.contact.address, "Address")}
                    ${textField("hours", c.contact.hours, "Opening hours")}
                </section>

                <section class="card cms-section" data-section="gallery">
                    <h3>Gallery</h3>
                    <p class="page-subtitle">
                        Add captions and an image path or URL for each photo. Leave the
                        URL empty to keep the placeholder tile.
                    </p>
                    ${pairList("gallery-items", c.gallery.items)}
                </section>

                <div class="cms-form-footer">
                    <button class="btn btn-primary" type="submit" id="cms-save-bottom">Save changes</button>
                </div>
            </form>
        `;
    } catch (err) {
        return `
            <div class="page-header">
                <div>
                    <span class="eyebrow">Public Website</span>
                    <h2>Website Content</h2>
                </div>
            </div>
            <div class="error">Could not load website content: ${esc(err.message)}</div>
        `;
    }
}

function readStringList(list) {
    return [...list.querySelectorAll("[data-item]")]
        .map(el => el.value.trim())
        .filter(Boolean);
}

function readPairList(list) {
    return [...list.querySelectorAll("[data-row]")]
        .map(row => {
            const label = row.querySelector("[data-item-label]")?.value.trim() || "";
            const url = row.querySelector("[data-item-url]")?.value.trim() || "";
            return label ? { label, url } : null;
        })
        .filter(Boolean);
}

function collectBlock(block) {
    const out = {};
    block.querySelectorAll("[data-field]").forEach(field => {
        out[field.dataset.field] =
            field.type === "checkbox" ? field.checked : field.value.trim();
    });
    block.querySelectorAll("[data-list]").forEach(list => {
        const key = list.dataset.list.split("-").pop();
        out[key] =
            list.dataset.pair === "true" ? readPairList(list) : readStringList(list);
    });
    return out;
}

function collectSections() {
    const sections = {};
    document.querySelectorAll(".cms-section").forEach(section => {
        const name = section.dataset.section;
        if (name === "programmes") {
            const programmes = {};
            section.querySelectorAll(".cms-sub").forEach(sub => {
                programmes[sub.dataset.sub] = collectBlock(sub);
            });
            sections[name] = programmes;
            return;
        }
        sections[name] = collectBlock(section);
    });
    return sections;
}

function addRow(button) {
    const block = button.closest(".cms-section, .cms-sub");
    const list = block.querySelector(`[data-list="${button.dataset.add}"]`);
    if (!list) return;

    const pair = button.dataset.pair === "true";
    const row = document.createElement("div");
    row.className = "cms-list-row" + (pair ? " cms-pair" : "");
    row.setAttribute("data-row", "");

    if (pair) {
        row.innerHTML = `
            <input data-item-label placeholder="Caption" />
            <input data-item-url placeholder="Image path or URL (optional)" />
            <button type="button" class="btn btn-secondary btn-sm cms-remove" data-remove>Remove</button>
        `;
    } else {
        row.innerHTML = `
            <input data-item placeholder="Item" />
            <button type="button" class="btn btn-secondary btn-sm cms-remove" data-remove>Remove</button>
        `;
    }

    list.appendChild(row);
    row.querySelector("input")?.focus();
}

export function wireWebsitePage() {
    const form = document.querySelector("#website-form");
    if (!form) return;

    form.addEventListener("submit", async event => {
        event.preventDefault();

        const status = document.querySelector("#cms-status");
        const buttons = form.querySelectorAll('button[type="submit"]');

        const setStatus = (kind, message) => {
            if (!status) return;
            status.hidden = false;
            status.className = `cms-status ${kind}`;
            status.textContent = message;
        };

        buttons.forEach(button => {
            button.disabled = true;
            button.textContent = "Saving...";
        });

        try {
            const saved = await api.siteContent.update(collectSections());
            await refreshSiteContent();
            setStatus("success", "Saved. The public website now shows your changes.");
        } catch (err) {
            setStatus("error", `Save failed: ${err.message}`);
        } finally {
            buttons.forEach(button => {
                button.disabled = false;
                button.textContent = "Save changes";
            });
        }
    });

    form.addEventListener("click", event => {
        const add = event.target.closest("[data-add]");
        if (add) {
            event.preventDefault();
            addRow(add);
            return;
        }
        const remove = event.target.closest("[data-remove]");
        if (remove) {
            event.preventDefault();
            remove.closest("[data-row]")?.remove();
        }
    });
}
