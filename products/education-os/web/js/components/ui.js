export function loading(message = "Loading...") {
    return `<div class="loading">${message}</div>`;
}

export function error(message) {
    return `
        <div class="error">
            <strong>Unable to load data</strong>
            <p>${message}</p>
        </div>
    `;
}

export function empty(message) {
    return `<div class="empty">${message}</div>`;
}

export function metric(label, value) {
    return `
        <div class="card">
            <div class="metric-label">${label}</div>
            <div class="metric-value">${value}</div>
        </div>
    `;
}
