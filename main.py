from anthropic import APIError, APITimeoutError, AuthenticationError, NotFoundError
from fastapi import FastAPI, HTTPException

from claude_client import call_claude
from models import PipelineRequest, PipelineResponse

app = FastAPI(title="Claude Pipeline", version="0.1.0")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/pipeline", response_model=PipelineResponse)
def pipeline(req: PipelineRequest):
    try:
        result = call_claude(req.prompt)
        return PipelineResponse(result=result, model=call_claude.model_name)
    except AuthenticationError:
        raise HTTPException(status_code=401, detail="Claude API 认证失败，请检查 API Key")
    except NotFoundError:
        raise HTTPException(status_code=503, detail="请求的模型不可用")
    except APITimeoutError:
        raise HTTPException(status_code=504, detail="Claude API 请求超时")
    except APIError as e:
        raise HTTPException(status_code=502, detail=f"Claude API 错误: {e.message}")
