import { getRoute, navigate, routeTitle, startRouter } from "./router.js";
import { renderDashboard } from "../pages/dashboard.js";
import { renderStudents } from "../pages/students.js";
import { renderAdmissions } from "../pages/admissions.js";
import { renderFees } from "../pages/fees.js";
import { renderAttendance } from "../pages/attendance.js";
import { renderOperations } from "../pages/operations.js";

const app = document.querySelector("#app");

const navItems = [
    ["dashboard", "Dashboard"],
    ["students", "Students"],
    ["admissions", "Admissions"],
    ["fees", "Fees & Payments"],
    ["attendance", "Attendance"],
    ["operations", "School Operations"]
];

async function render() {
    const route = getRoute();

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

startRouter(render);
render();
