import { getSiteContent } from "../js/site-content.js";

export const PUBLIC_ROUTES = {
    home: { title: "Home" },
    about: { title: "About Us" },
    programmes: { title: "Programmes" },
    "day-care": { title: "Day Care" },
    kindergarten: { title: "Kindergarten" },
    skills: { title: "Talents, Sports & Skills" },
    "admissions-info": { title: "Admissions" },
    gallery: { title: "Gallery" },
    news: { title: "News & Events" },
    location: { title: "Location" },
    contact: { title: "Contact" },
    "parent-portal": { title: "Parent Portal" }
};

const INTERNAL_ROUTES = [
    "dashboard",
    "students",
    "admissions",
    "fees",
    "attendance",
    "operations",
    "staff",
    "password",
    "website"
];

export function isPublicRoute(route) {
    return route in PUBLIC_ROUTES;
}

export function isInternalRoute(route) {
    return INTERNAL_ROUTES.includes(route);
}

export function publicTitle(route) {
    return PUBLIC_ROUTES[route]?.title || "Home";
}

function esc(value) {
    return String(value ?? "").replace(/[&<>"']/g, ch => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    }[ch]));
}

function intlNumber(raw) {
    let digits = String(raw || "").replace(/\D/g, "");
    if (digits.startsWith("0")) digits = "256" + digits.slice(1);
    if (!digits.startsWith("256")) digits = "256" + digits;
    return digits;
}

function telLink(phone) {
    return `tel:+${intlNumber(phone)}`;
}

function waLink(phone) {
    return `https://wa.me/${intlNumber(phone)}`;
}

function navLink(route, label, activeRoute) {
    const active = activeRoute === route ? " active" : "";
    return `<a class="public-nav-link${active}" href="#/${route}">${label}</a>`;
}

function listItems(items) {
    return items.map(item => `<li>${esc(item)}</li>`).join("");
}

function pageHeading(eyebrow, title, subtitle) {
    return `
        <header class="public-page-head">
            <span class="eyebrow">${esc(eyebrow)}</span>
            <h1>${title}</h1>
            ${subtitle ? `<p class="public-lead">${esc(subtitle)}</p>` : ""}
        </header>
    `;
}

export function renderPublicShell(content, activeRoute) {
    const programmesActive =
        activeRoute === "programmes" ||
        activeRoute === "day-care" ||
        activeRoute === "kindergarten";

    return `
        <div class="public-shell">
            <header class="public-nav">
                <a class="public-brand" href="#/home">
                    <strong>Little Oaks</strong>
                    <span>Montessori Kindergarten &amp; Daycare</span>
                </a>
                <nav class="public-nav-links">
                    ${navLink("home", "Home", activeRoute)}
                    ${navLink("about", "About Us", activeRoute)}
                    <div class="public-dropdown${programmesActive ? " active" : ""}">
                        <a class="public-nav-link" href="#/programmes">Programmes</a>
                        <div class="public-dropdown-menu">
                            <a href="#/day-care">Day Care</a>
                            <a href="#/kindergarten">Kindergarten</a>
                        </div>
                    </div>
                    ${navLink("skills", "Talents, Sports &amp; Skills", activeRoute)}
                    ${navLink("admissions-info", "Admissions", activeRoute)}
                    ${navLink("gallery", "Gallery", activeRoute)}
                    ${navLink("news", "News &amp; Events", activeRoute)}
                    ${navLink("location", "Location", activeRoute)}
                    ${navLink("contact", "Contact", activeRoute)}
                    <a class="public-nav-cta" href="#/parent-portal">Parent Portal</a>
                </nav>
            </header>

            <main class="public-main" id="public-content">${content}</main>

            <footer class="public-footer">
                <div class="public-footer-inner">
                    <div class="public-footer-col">
                        <a class="public-brand" href="#/home">
                            <strong>Little Oaks</strong>
                            <span>Montessori Kindergarten &amp; Daycare</span>
                        </a>
                        <p>
                            A loving, safe and stimulating environment where children
                            grow in knowledge, confidence, character and creativity.
                        </p>
                    </div>
                    <div class="public-footer-col">
                        <h4>Explore</h4>
                        <a href="#/about">About Us</a>
                        <a href="#/programmes">Programmes</a>
                        <a href="#/skills">Talents, Sports &amp; Skills</a>
                        <a href="#/admissions-info">Admissions</a>
                        <a href="#/gallery">Gallery</a>
                        <a href="#/news">News &amp; Events</a>
                    </div>
                    <div class="public-footer-col">
                        <h4>Visit us</h4>
                        <a href="#/location">Location</a>
                        <a href="#/contact">Contact</a>
                        <a href="#/parent-portal" class="public-nav-cta">Parent Portal</a>
                    </div>
                    <div class="public-footer-col">
                        <h4>Reach us</h4>
                        <span class="public-footer-addr">Nsikye, Nyamitanga, Mbarara City</span>
                        <a href="mailto:info@littleoaks.ug">info@littleoaks.ug</a>
                        <span class="public-footer-phones">0705 074279 &middot; 0762 023393</span>
                    </div>
                </div>
                <div class="public-footer-legal">
                    &copy; ${new Date().getFullYear()} Little Oaks Montessori Kindergarten &amp; Daycare. All rights reserved.
                </div>
            </footer>
        </div>
    `;
}

function announcementBand(section) {
    if (!section?.enabled) return "";
    return `
        <section class="public-announcement">
            <span class="eyebrow">${esc(section.title || "Notice")}</span>
            <p>${esc(section.body)}</p>
        </section>
    `;
}

function homePage() {
    const c = getSiteContent();
    const prog = c.programmes;
    return `
        <section class="public-hero">
            <div class="public-hero-inner">
                <p class="eyebrow">Nurture &bull; Explore &bull; Grow</p>
                <h1>Little Oaks Montessori<br>Kindergarten &amp; Daycare</h1>
                <p class="public-hero-sub">
                    ${esc(c.about.intro)}
                </p>
                <div class="public-hero-actions">
                    <a class="btn btn-primary" href="#/admissions-info">Begin Admissions</a>
                    <a class="btn btn-secondary" href="#/programmes">Explore Programmes</a>
                </div>
            </div>
        </section>

        ${announcementBand(c.homepage_announcement)}

        <section class="public-section public-section-tint">
            <div class="public-page-head">
                <span class="eyebrow">Our Programmes</span>
                <h2>Learning for every age</h2>
            </div>
            <div class="public-grid-2">
                <a class="card public-programme" href="#/day-care">
                    <span class="eyebrow">${esc(prog.day_care.ages)}</span>
                    <h3>${esc(prog.day_care.title)}</h3>
                    <p>${esc(prog.day_care.description)}</p>
                    <span class="public-link-more">Learn more</span>
                </a>
                <a class="card public-programme" href="#/kindergarten">
                    <span class="eyebrow">${esc(prog.kindergarten.ages)}</span>
                    <h3>${esc(prog.kindergarten.title)}</h3>
                    <p>${esc(prog.kindergarten.description)}</p>
                    <span class="public-link-more">Learn more</span>
                </a>
            </div>
            <div class="public-inline-cta">
                <p>Plus <strong>Talents, Sports &amp; Skills</strong> &mdash; sports, brain games, life skills and enrichment.</p>
                <a class="btn btn-secondary" href="#/skills">Explore activities</a>
            </div>
        </section>

        <section class="public-section">
            <div class="public-approach">
                <span class="eyebrow">${esc(c.approach.title)}</span>
                <blockquote>${esc(c.approach.body)}</blockquote>
            </div>
        </section>

        <section class="public-section">
            <div class="public-cta-band">
                <div>
                    <h2>Ready to join the Little Oaks family?</h2>
                    <p>Parents are warmly invited to register early to secure a place.</p>
                </div>
                <a class="btn btn-primary" href="#/admissions-info">Begin Admissions</a>
            </div>
        </section>
    `;
}

function aboutPage() {
    const c = getSiteContent();
    return `
        <section class="public-section public-section-narrow">
            ${pageHeading("About Little Oaks", "About Us", c.about.intro)}
            <div class="public-grid-2">
                <div class="card public-feature">
                    <h3>Our Mission</h3>
                    <p>${esc(c.about.mission)}</p>
                </div>
                <div class="card public-feature">
                    <h3>Montessori Philosophy</h3>
                    <p>${esc(c.about.philosophy)}</p>
                </div>
            </div>
        </section>
        <section class="public-section public-section-tint">
            <div class="public-page-head">
                <span class="eyebrow">What makes us special</span>
                <h2>The Little Oaks experience</h2>
            </div>
            <div class="public-grid-3">
                ${c.about.highlights.map(h => `
                    <div class="card public-feature">
                        <p>${esc(h)}</p>
                    </div>
                `).join("")}
            </div>
        </section>
        <section class="public-section">
            <div class="public-approach">
                <span class="eyebrow">${esc(c.approach.title)}</span>
                <blockquote>${esc(c.approach.body)}</blockquote>
            </div>
        </section>
    `;
}

function programmeOverviews() {
    const c = getSiteContent();
    const prog = c.programmes;
    return `
        <section class="public-section public-section-narrow">
            ${pageHeading("Our Programmes", "Programmes", "Two complementary programmes cover the earliest years &mdash; from Day Care for our youngest children to a full Montessori Kindergarten.")}
            <div class="public-grid-2">
                <a class="card public-programme" href="#/day-care">
                    <span class="eyebrow">${esc(prog.day_care.ages)}</span>
                    <h3>${esc(prog.day_care.title)}</h3>
                    <p>${esc(prog.day_care.description)}</p>
                    <span class="public-link-more">Learn more</span>
                </a>
                <a class="card public-programme" href="#/kindergarten">
                    <span class="eyebrow">${esc(prog.kindergarten.ages)}</span>
                    <h3>${esc(prog.kindergarten.title)}</h3>
                    <p>${esc(prog.kindergarten.description)}</p>
                    <span class="public-link-more">Learn more</span>
                </a>
            </div>
            <div class="public-inline-cta">
                <p>Beyond the classroom, children enjoy <strong>Talents, Sports &amp; Skills</strong>.</p>
                <a class="btn btn-secondary" href="#/skills">Explore activities</a>
            </div>
        </section>
    `;
}

function programmeDetail(key) {
    const c = getSiteContent();
    const prog = c.programmes[key];
    return `
        <section class="public-section public-section-narrow">
            ${pageHeading("Programmes", `${esc(prog.title)} &mdash; Ages ${esc(prog.ages)}`, prog.description)}
            <div class="card public-programme-detail">
                <h3>What your child experiences</h3>
                <ul class="public-list public-list-2col">
                    ${listItems(prog.items)}
                </ul>
            </div>
            <div class="public-cta-band">
                <p>Places are limited. Register early to secure your child's place.</p>
                <a class="btn btn-primary" href="#/admissions-info">Begin Admissions</a>
            </div>
        </section>
    `;
}

function skillsPage() {
    const c = getSiteContent();
    const s = c.sports_skills;
    return `
        <section class="public-section public-section-narrow">
            ${pageHeading("Beyond the classroom", "Talents, Sports &amp; Skills", "Children grow healthy bodies and bright minds through sports, brain games, life skills and enrichment activities.")}
            <div class="public-grid-4">
                <div class="card public-feature">
                    <h3>Sports</h3>
                    <ul class="public-list">
                        ${listItems(s.sports)}
                    </ul>
                </div>
                <div class="card public-feature">
                    <h3>Brain Games</h3>
                    <ul class="public-list">
                        ${listItems(s.brain_games)}
                    </ul>
                </div>
                <div class="card public-feature">
                    <h3>Life Skills</h3>
                    <ul class="public-list">
                        ${listItems(s.life_skills)}
                    </ul>
                </div>
                <div class="card public-feature">
                    <h3>Enrichment</h3>
                    <ul class="public-list">
                        ${listItems(s.enrichment)}
                    </ul>
                </div>
            </div>
        </section>
    `;
}

function admissionsPage() {
    const c = getSiteContent();
    return `
        <section class="public-section public-section-narrow">
            ${pageHeading("Admissions", "Admissions", "We welcome new families at every level. Admissions are simple and we are happy to guide you through each step.")}
            ${announcementBand(c.admissions_notice)}
            <div class="public-grid-2">
                <div class="card">
                    <h3>How it works</h3>
                    <ol class="public-list public-list-num">
                        <li><strong>Visit.</strong> Book a tour and see our classrooms and grounds.</li>
                        <li><strong>Apply.</strong> Complete the application form and share your child's details.</li>
                        <li><strong>Meet.</strong> We meet your child and family to understand their needs.</li>
                        <li><strong>Enrol.</strong> Confirm your place, arrange fees and settle in.</li>
                    </ol>
                </div>
                <div class="card">
                    <h3>What you need</h3>
                    <ul class="public-list">
                        <li>Completed application form</li>
                        <li>Copy of the child's birth certificate</li>
                        <li>Child's immunisation / health records</li>
                        <li>Two passport photos</li>
                        <li>Term fee payment on confirmation</li>
                    </ul>
                </div>
            </div>
            <div class="public-cta-band">
                <p>Questions first? Call 0705 074279 or 0762 023393, or send us a message.</p>
                <a class="btn btn-primary" href="#/contact">Contact us</a>
            </div>
        </section>
    `;
}

function galleryPage() {
    const c = getSiteContent();
    const items = c.gallery.items || [];
    return `
        <section class="public-section public-section-narrow">
            ${pageHeading("Gallery", "Gallery", "A glimpse of daily life at Little Oaks &mdash; classrooms, grounds, activities and celebrations.")}
            <div class="public-gallery">
                ${items.map((item, i) => {
                    const url = String(item.url || "").trim();
                    const label = esc(item.label || `Photo ${i + 1}`);
                    if (url) {
                        return `<figure class="public-gallery-tile photo">
                            <img src="${esc(url)}" alt="${label}" loading="lazy" />
                            <figcaption>${label}</figcaption>
                        </figure>`;
                    }
                    return `<div class="public-gallery-tile placeholder">
                        <span>${label}</span>
                    </div>`;
                }).join("")}
            </div>
        </section>
    `;
}

const NEWS_ITEMS = [
    ["05 Jan 2026", "Welcome to the new school year", "We are delighted to welcome new families to Little Oaks. Classrooms are refreshed and our teachers are ready for a wonderful year of discovery."],
    ["01 Dec 2025", "Admissions open for next year", "Applications for Day Care and Kindergarten places for the coming year are now open. Book a tour to secure your child's place."],
    ["30 Nov 2025", "Annual sports day", "A fun-filled sports day of races, games and team activities. Every child took part and showed great team spirit."],
    ["12 Oct 2025", "Parent teacher conferences", "Thank you to every family who joined our termly conferences. Partnership between home and school makes all the difference."]
];

function newsPage() {
    return `
        <section class="public-section public-section-narrow">
            ${pageHeading("News &amp; Events", "News &amp; Events", "Updates from the Little Oaks community &mdash; announcements, events and highlights from school life.")}
            <div class="public-news">
                ${NEWS_ITEMS.map(([date, title, body]) => `
                    <article class="card public-news-item">
                        <span class="public-news-date">${date}</span>
                        <h3>${title}</h3>
                        <p>${body}</p>
                    </article>
                `).join("")}
            </div>
        </section>
    `;
}

function locationPage() {
    const c = getSiteContent();
    const loc = c.location;
    return `
        <section class="public-section public-section-narrow">
            ${pageHeading("Find us", "Location", "Visit us in Nsikye, Nyamitanga in Mbarara City &mdash; we would love to show you around.")}
            <div class="card public-location-card">
                <h3>${esc(loc.place)}</h3>
                <ul class="public-list">
                    ${listItems(loc.details)}
                </ul>
                <a class="btn btn-primary" href="${esc(loc.maps_url)}" target="_blank" rel="noopener">Open in Google Maps</a>
            </div>
        </section>
    `;
}

function contactPage() {
    const c = getSiteContent();
    const con = c.contact;
    return `
        <section class="public-section public-section-narrow">
            ${pageHeading("Contact", "Contact", "We would love to hear from you. Reach out for admissions, tours or any question about Little Oaks.")}
            <div class="public-grid-2">
                <div class="card">
                    <h3>Reach us</h3>
                    <ul class="public-list public-list-contact">
                        <li>
                            <strong>Call</strong>
                            <span class="public-contact-actions">
                                ${con.phones.map(p => `<a class="btn btn-secondary btn-sm" href="${telLink(p)}">Call ${esc(p)}</a>`).join("")}
                            </span>
                        </li>
                        <li>
                            <strong>WhatsApp</strong>
                            <span><a class="btn btn-secondary btn-sm" href="${waLink(con.whatsapp)}" target="_blank" rel="noopener">WhatsApp us</a></span>
                        </li>
                        <li><strong>Email</strong><span><a href="mailto:${esc(con.email)}">${esc(con.email)}</a></span></li>
                        <li><strong>Address</strong><span>${esc(con.address)}</span></li>
                        <li><strong>Hours</strong><span>${esc(con.hours)}</span></li>
                    </ul>
                </div>
                <div class="card">
                    <h3>Send a message</h3>
                    <form id="contact-form" class="public-contact-form">
                        <div class="form-group">
                            <label>Your name</label>
                            <input id="contact-name" type="text" required />
                        </div>
                        <div class="form-group">
                            <label>Phone or email</label>
                            <input id="contact-email" type="text" required />
                        </div>
                        <div class="form-group">
                            <label>Message</label>
                            <textarea id="contact-message" rows="5" required></textarea>
                        </div>
                        <div id="contact-note" class="public-contact-note" hidden></div>
                        <button class="btn btn-primary" type="submit">Send message</button>
                    </form>
                </div>
            </div>
        </section>
    `;
}

export function parentPortalPage() {
    return `
        <section class="public-section public-section-narrow">
            <div class="public-portal-wrap">
                <div class="auth-card">
                    <div class="auth-brand">
                        <strong>Little Oaks</strong>
                        <span>Parent Portal</span>
                    </div>
                    <h1>Sign in</h1>
                    <p class="auth-subtitle">
                        Access the Little Oaks portal for parents and staff.
                    </p>
                    <form id="login-form">
                        <div class="form-group">
                            <label>Email</label>
                            <input
                                id="login-email"
                                type="email"
                                placeholder="you@littleoaks.ug"
                                required
                            />
                        </div>
                        <div class="form-group">
                            <label>Password</label>
                            <input
                                id="login-password"
                                type="password"
                                placeholder="Enter your password"
                                required
                            />
                        </div>
                        <div id="login-error" class="auth-error"></div>
                        <button class="btn btn-primary auth-submit" type="submit">
                            Sign in
                        </button>
                    </form>
                    <p class="public-back-site">
                        <a href="#/home">&larr; Back to website</a>
                    </p>
                </div>
            </div>
        </section>
    `;
}

export function renderPublicPage(route) {
    switch (route) {
        case "home": return homePage();
        case "about": return aboutPage();
        case "programmes": return programmeOverviews();
        case "day-care": return programmeDetail("day_care");
        case "kindergarten": return programmeDetail("kindergarten");
        case "skills": return skillsPage();
        case "admissions-info": return admissionsPage();
        case "gallery": return galleryPage();
        case "news": return newsPage();
        case "location": return locationPage();
        case "contact": return contactPage();
        case "parent-portal": return parentPortalPage();
        default: return homePage();
    }
}
