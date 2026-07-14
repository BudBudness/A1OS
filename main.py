import uvicorn
from core.api import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3011)

@app.get("/admin")
async def get_admin():
    with open("web/admin/index.html", "r") as f:
        return f.read()
