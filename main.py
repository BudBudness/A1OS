from core.api import app


# Vercel/ASGI entrypoint.
# The full A1OS control-plane singleton is intentionally not imported at
# module load time: serverless instances must remain import-safe and should
# not start a persistent background worker during request initialization.

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=3011,
        log_level="info",
    )
