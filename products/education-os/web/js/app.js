import { getRoute, navigate, routeTitle, startRouter } from "./router.js";
import { api } from "./education-api.js";
import { login, logout, verifySession, isAuthenticated, can, user } from "./auth.js?v=1785434576";
import { renderDashboard } from "../pages/dashboard.js";
import { renderStudents } from "../pages/students.js";
import { renderAdmissions } from "../pages/admissions.js";
import { renderFees } from "../pages/fees.js";
import { renderAttendance } from "../pages/attendance.js";
import { renderOperations } from "../pages/operations.js";

import { renderStaffPage } from "../pages/staff.js";
import { renderDirectorSuite } from "../pages/director/index.js";
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
        await render();
        } catch (e) {
            error.textContent = e.message;
            button.disabled = false;
            button.textContent = "Sign in";
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
            renderLogin();
            return;
        }

        appRoot.innerHTML = `
            <div class="app-shell">
                <nav class="sidebar">
                    <h2>Little Oaks</h2>
                    ${navItems.map(([r,t]) =>
                        `<a href="#/${r}">${t}</a>`
                    ).join("")}
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

            default:
                content.innerHTML = await renderDashboard();
        }

        console.log("RENDER COMPLETE", route);

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
