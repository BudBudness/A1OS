import { getRoute, navigate, routeTitle, startRouter } from "./router.js";
import { api } from "./education-api.js";
import { login, logout, verifySession, isAuthenticated, user } from "./auth.js";
import { renderDashboard } from "../pages/dashboard.js";
import { renderStudents } from "../pages/students.js";
import { renderAdmissions } from "../pages/admissions.js";
import { renderFees } from "../pages/fees.js";
import { renderAttendance } from "../pages/attendance.js";
import { renderOperations } from "../pages/operations.js";

import { renderStaffPage } from "../pages/staff.js";
const app = document.querySelector("#app");

const navItems = [
    ["dashboard", "Dashboard"],
    ["students", "Students"],
    ["admissions", "Admissions"],
    ["fees", "Fees & Payments"],
    ["attendance", "Attendance"],
    ["operations", "School Operations"]
];

function renderLogin() {
    app.innerHTML = `
        <div class="auth-shell">
            <div class="auth-card">
                <div class="auth-brand">
                    <strong>Little Oaks</strong>
                    <span>Education OS</span>
                </div>

                <h1>Sign in</h1>
                <p class="auth-subtitle">
                    Little Oaks Montessori Nursery & Kindergarten
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
            </div>
        </div>
    `;

    document.querySelector("#login-form").addEventListener("submit", async event => {
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
            if (bootApp) {
            const status = document.querySelector("#boot-status");
            if (status) status.textContent = "Application modules loaded. Verifying session...";
        }
        await render();
        } catch (e) {
            error.textContent = e.message;
            button.disabled = false;
            button.textContent = "Sign in";
        }
    });
}

async function render() {
    if (!isAuthenticated()) {
        renderLogin();
        return;
    }

    const route = getRoute();
    const currentUser = user();

    app.innerHTML = `
        <div class="app-shell">
            <aside class="sidebar">
                <div class="brand">
                    Little Oaks
                    <small>Education OS</small>
                </div>

                <nav class="nav">
                    ${navItems
                        .map(
                            ([key, label]) => `
                                <button
                                    data-route="${key}"
                                    class="${route === key ? "active" : ""}"
                                >
                                    ${label}
                                </button>
                            `
                        )
                        .join("")}
                </nav>

                <div class="sidebar-user">
                    <strong>${currentUser?.full_name || "User"}</strong>
                    <small>${currentUser?.role || ""}</small>
                    <button id="logout-button" class="logout-button">
                        Sign out
                    </button>
                </div>
            </aside>

            <main class="main">
                <header class="topbar">
                    <h1>${routeTitle(route)}</h1>
                    <span>Little Oaks Montessori</span>
                </header>

                <section class="content" id="page-content">
                    <div class="loading">Loading...</div>
                </section>
            </main>
        </div>
    `;

    document.querySelectorAll("[data-route]").forEach(button => {
        button.addEventListener("click", () => navigate(button.dataset.route));
    });

    document.querySelector("#logout-button").addEventListener("click", logout);

    const content = document.querySelector("#page-content");

    try {
        if (route === "dashboard") {
            content.innerHTML = await renderDashboard();
        } else if (route === "students") {
            content.innerHTML = await renderStudents();
        } else if (route === "admissions") {
            content.innerHTML = await renderAdmissions();
        } else if (route === "fees") {
            content.innerHTML = await renderFees();
        } else if (route === "attendance") {
            content.innerHTML = await renderAttendance();
        } else if (route === "operations") {
            content.innerHTML = await renderOperations();
        } else {
            navigate("dashboard");
        }
    } catch (e) {
        content.innerHTML = `
            <div class="error">
                <strong>Frontend integration error</strong>
                <p>${e.message}</p>
            </div>
        `;
    }
}

window.addEventListener("error", event => {
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
    const bootApp = document.querySelector("#app");
    if (bootApp) {
        bootApp.innerHTML = `
            <div style="padding:40px;font-family:system-ui;background:#f8fafc;min-height:100vh">
                <h1 style="color:#14532d">Little Oaks Education OS</h1>
                <p id="boot-status">Loading application modules...</p>
            </div>`;
    }
    const app = document.querySelector("#app");

    try {
        app.innerHTML = `
            <div style="padding:40px;font-family:system-ui">
                <h1>Little Oaks Education OS</h1>
                <p>Initializing application...</p>
            </div>
        `;

        if (bootApp) {
            const status = document.querySelector("#boot-status");
            if (status) status.textContent = "Application modules loaded. Verifying session...";
        }
        await render();
        startRouter(render);

    } catch (error) {
        console.error("BOOT ERROR:", error);

        app.innerHTML = `
            <div style="padding:40px;font-family:system-ui;color:#b91c1c">
                <h1>Little Oaks Frontend Error</h1>
                <pre style="white-space:pre-wrap">${error.stack || error.message}</pre>
            </div>
        `;
    }
}

boot();
