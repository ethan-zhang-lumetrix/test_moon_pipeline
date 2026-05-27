from fastapi import FastAPI

from claude_client import call_claude
from models import PipelineRequest, PipelineResponse

app = FastAPI(title="Claude Pipeline", version="0.1.0")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/pipeline", response_model=PipelineResponse)
def pipeline(req: PipelineRequest):
    result = call_claude(req.prompt)
    return PipelineResponse(result=result, model=call_claude.model_name)
