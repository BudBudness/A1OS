if (!window.__LITTLE_OAKS_BOOTED__) {
    window.__LITTLE_OAKS_BOOTED__ = true;

    const start = async () => {
        try {
            await import("./app.js?v=" + Date.now()).then(()=>console.log("APP MODULE LOADED")).catch(e=>console.error("APP LOAD FAILED",e));
            console.log("Little Oaks app loaded");
        } catch (error) {
            console.error("BOOT FAILURE", error);
            const app = document.querySelector("#app");
            if (app) {
                app.innerHTML = `
                <div style="padding:40px;color:#991b1b">
                    <h1>Little Oaks Education OS</h1>
                    <pre>${error.stack || error}</pre>
                </div>`;
            }
        }
    };

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", start);
    } else {
        start();
    }
}
