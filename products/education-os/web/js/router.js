const routes = {
    dashboard: "Dashboard",
    students: "Students",
    admissions: "Admissions",
    fees: "Fees & Payments",
    attendance: "Attendance",
    operations: "School Operations"
};

export function getRoute() {
    return location.hash.replace("#/", "") || "dashboard";
}

export function navigate(route) {
    location.hash = `/${route}`;
}

export function routeTitle(route) {
    return routes[route] || "Dashboard";
}

export function startRouter(callback) {
    window.addEventListener("hashchange", callback);
}
