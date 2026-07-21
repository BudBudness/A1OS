from fastapi import FastAPI

app=FastAPI(title="A1OS")

@app.get("/")
async def root():
    return {"platform":"A1OS"}
