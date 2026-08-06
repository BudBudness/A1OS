import { getRoute, navigate, routeTitle, startRouter } from "./router.js";
import { api } from "./education-api.js";
import { login, logout, verifySession, isAuthenticated, can, user, getToken } from "./auth.js?v=1785434576";
import { renderDashboard } from "../pages/dashboard.js";
import { renderStudents } from "../pages/students.js";
import { renderAdmissions } from "../pages/admissions.js";
import { renderFees } from "../pages/fees.js";
import { renderAttendance } from "../pages/attendance.js";
import { renderOperations } from "../pages/operations.js";

import { renderStaffPage } from "../pages/staff.js";
import { renderDirectorSuite } from "../pages/director/index.js";
import { renderWebsitePage, wireWebsitePage } from "../pages/website.js";
import {
    renderPublicShell,
    renderPublicPage,
    parentPortalPage,
    isPublicRoute,
    publicTitle
} from "../pages/public.js";
import { loadSiteContent } from "./site-content.js";
const app = document.querySelector("#app");

const navItems = [
    ["dashboard", "Dashboard"],
    ["students", "Students"],
    ["admissions", "Admissions"],
    ["fees", "Fees & Payments"],
    ["attendance", "Attendance"],
    ["operations", "School Operations"],
    ["website", "Website"],
    ["password", "Change Password"]
];

function wireLoginForm() {
    const form = document.querySelector("#login-form");
    if (!form) return;

    form.addEventListener("submit", async event => {
        event.preventDefault();

        const email = document.querySelector("#login-email").value.trim();
        const password = document.querySelector("#login-password").value;
        const error = document.querySelector("#login-error");
        const button = document.querySelector(".auth-submit");

        error.textContent = "";
        button.disabled = true;
        button.textContent = "Signing in...";

        try {
            await login(email, password);
            await render();
        } catch (e) {
            error.textContent = e.message;
            button.disabled = false;
            button.textContent = "Sign in";
        }
    });
}

function wireContactForm() {
    const form = document.querySelector("#contact-form");
    if (!form) return;

    form.addEventListener("submit", event => {
        event.preventDefault();
        const note = document.querySelector("#contact-note");
        if (note) {
            note.hidden = false;
            note.textContent = "Thank you! Your message has been received. We will be in touch within one working day.";
        }
        form.reset();
    });
}

function renderPublicApp(route) {
    const appRoot = document.querySelector("#app");

    if (!isPublicRoute(route)) {
        location.hash = "/home";
        route = "home";
    }

    const content = route === "parent-portal" ? parentPortalPage() : renderPublicPage(route);
    appRoot.innerHTML = renderPublicShell(content, route);
    document.title = `${publicTitle(route)} — Little Oaks Montessori Kindergarten & Daycare`;

    if (route === "parent-portal") wireLoginForm();
    if (route === "contact") wireContactForm();
}



function renderChangePassword() {
    return `
        <div class="auth-shell">
            <div class="auth-card">
                <div class="auth-brand">
                    <strong>Little Oaks</strong>
                    <span>Account</span>
                </div>

                <h1>Change Password</h1>

                <div id="password-error" class="auth-error"></div>
                <div id="password-success" style="color:#15803d;margin-bottom:12px"></div>

                <form id="password-form">
                    <div class="form-group">
                        <label>Current password</label>
                        <input id="current-password" type="password" required />
                    </div>

                    <div class="form-group">
                        <label>New password (min 8 characters)</label>
                        <input id="new-password" type="password" required />
                    </div>

                    <div class="form-group">
                        <label>Confirm new password</label>
                        <input id="confirm-password" type="password" required />
                    </div>

                    <button class="btn btn-primary auth-submit" type="submit">
                        Update password
                    </button>
                </form>
            </div>
        </div>
    `;
}

function wireChangePasswordForm() {
    const passwordForm = document.querySelector("#password-form");
    if (!passwordForm) return;

    passwordForm.addEventListener("submit", async event => {
        event.preventDefault();

        const error = document.querySelector("#password-error");
        const success = document.querySelector("#password-success");
        const button = passwordForm.querySelector("button");
        const current = document.querySelector("#current-password").value;
        const next = document.querySelector("#new-password").value;
        const confirm = document.querySelector("#confirm-password").value;

        error.textContent = "";
        success.textContent = "";

        if (next !== confirm) {
            error.textContent = "New passwords do not match";
            return;
        }

        button.disabled = true;
        button.textContent = "Updating...";

        try {
            const token = getToken();
            const response = await fetch("/api/auth/change-password", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    ...(token ? { Authorization: `Bearer ${token}` } : {})
                },
                body: JSON.stringify({
                    current_password: current,
                    new_password: next
                })
            });

            const data = await response.json().catch(() => null);

            if (!response.ok) {
                throw new Error(data?.detail || "Failed to update password");
            }

            success.textContent = "Password updated. Other sessions were signed out.";
            passwordForm.reset();
        } catch (e) {
            error.textContent = e.message;
        } finally {
            button.disabled = false;
            button.textContent = "Update password";
        }
    });
}



async function render() {
    console.log("APP RENDER ENTER");
    const route = getRoute();
    console.log("ROUTE =", route);
    console.log("RENDER ROUTE:", route);

    const appRoot = document.querySelector("#app");

    if (!appRoot) {
        console.error("Missing #app root");
        return;
    }

    try {
        if (!isAuthenticated()) {
            renderPublicApp(route);
            return;
        }

        document.title = "Little Oaks Education OS";

        appRoot.innerHTML = `
            <div class="app-shell">
                <nav class="sidebar">
                    <h2>Little Oaks</h2>
                    ${navItems.filter(([r]) => r !== "website" || can("website"))
                        .map(([r,t]) =>
                        `<a href="#/${r}">${t}</a>`
                    ).join("")}
                    <a href="#" id="logout-link" style="margin-top:24px;opacity:.7">Logout</a>
                </nav>
                <main id="content" class="content">
                    <div class="loading">Loading ${route}...</div>
                </main>
            </div>
        `;

        const content = document.querySelector("#content");

        if (!content) {
            throw new Error("Content container missing");
        }

        switch(route) {
            case "dashboard":
                content.innerHTML = await renderDashboard();
                break;

            case "students":
                content.innerHTML = await renderStudents();
                break;

            case "admissions":
                content.innerHTML = await renderAdmissions();
                break;

            case "fees":
                content.innerHTML = await renderFees();
                break;

            case "attendance":
                content.innerHTML = await renderAttendance();
                break;

            case "operations":
                content.innerHTML = await renderOperations();
                break;

            case "staff":
                content.innerHTML = await renderStaffPage();
                break;

            case "website":
                content.innerHTML = can("website")
                    ? await renderWebsitePage()
                    : `<div class="error">You do not have permission to manage website content.</div>`;
                break;

            case "password":
                content.innerHTML = renderChangePassword();
                break;

            default:
                content.innerHTML = await renderDashboard();
        }

        console.log("RENDER COMPLETE", route);

        document.querySelector("#logout-link")?.addEventListener("click", event => {
            event.preventDefault();
            logout();
        });

        wireChangePasswordForm();
        wireWebsitePage();

    } catch (error) {
        console.error("RENDER FAILURE:", error);

        appRoot.innerHTML = `
            <div style="padding:40px;color:#991b1b;font-family:system-ui">
                <h1>Little Oaks Education OS</h1>
                <h2>Frontend Render Error</h2>
                <pre>${error.stack || error}</pre>
            </div>
        `;
    }
}

window.addEventListener("error", event => {
    console.error("GLOBAL ERROR:", event.message, event.error);
    const app = document.querySelector("#app");
    if (app) {
        app.innerHTML = `
            <div style="padding:40px;font-family:system-ui;color:#b91c1c">
                <h1>Little Oaks Frontend Error</h1>
                <pre style="white-space:pre-wrap">${event.error?.stack || event.message}</pre>
            </div>
        `;
    }
    console.error("Little Oaks runtime error:", event.error || event.message);
});

window.addEventListener("unhandledrejection", event => {
    console.error("PROMISE ERROR:", event.reason);
    const app = document.querySelector("#app");
    if (app) {
        app.innerHTML = `
            <div style="padding:40px;font-family:system-ui;color:#b91c1c">
                <h1>Little Oaks Frontend Error</h1>
                <pre style="white-space:pre-wrap">${event.reason?.stack || event.reason}</pre>
            </div>
        `;
    }
    console.error("Little Oaks unhandled rejection:", event.reason);
});




async function boot() {
    const app = document.querySelector("#app");

    try {
        console.log("[BOOT] starting");

        await verifySession();

        console.log("[BOOT] session verified");

        await loadSiteContent();

        console.log("[BOOT] site content loaded");

        await render();

        console.log("[BOOT] render completed");

        startRouter(render);

    } catch (error) {
        console.error("[BOOT ERROR]", error);

        if (app) {
            app.innerHTML = `
            <div style="padding:40px;font-family:system-ui;color:#991b1b">
                <h1>Little Oaks Education OS</h1>
                <h2>Frontend startup failed</h2>
                <pre>${error?.stack || error}</pre>
            </div>`;
        }
    }
}

boot();
