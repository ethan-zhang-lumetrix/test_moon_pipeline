from fastapi import FastAPI

app = FastAPI(title="Claude Pipeline", version="0.1.0")


@app.get("/")
async def hello():
    return {"message": "hello world"}


@app.get("/health")
async def health():
    return {"status": "ok"}
