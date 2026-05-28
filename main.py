from anthropic import APIError, APITimeoutError, AuthenticationError, NotFoundError
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse

from claude_client import call_claude, check_health, stream_claude
from models import PipelineRequest, PipelineResponse

app = FastAPI(title="Claude Pipeline", version="0.1.0")


@app.get("/health")
async def health():
    result = check_health()
    status_code = 200 if result["status"] == "healthy" else 503
    return JSONResponse(content=result, status_code=status_code)


@app.post("/pipeline", response_model=PipelineResponse)
def pipeline(req: PipelineRequest):
    try:
        result = call_claude(req.prompt, req.max_tokens)
        return PipelineResponse(result=result, model=call_claude.model_name)
    except AuthenticationError:
        raise HTTPException(status_code=401, detail="Claude API 认证失败，请检查 API Key")
    except NotFoundError:
        raise HTTPException(status_code=503, detail="请求的模型不可用")
    except APITimeoutError:
        raise HTTPException(status_code=504, detail="Claude API 请求超时")
    except APIError as e:
        raise HTTPException(status_code=502, detail=f"Claude API 错误: {e.message}")


@app.post("/pipeline/stream")
def pipeline_stream(req: PipelineRequest):
    def _generate():
        try:
            for token in stream_claude(req.prompt, req.max_tokens):
                yield f"data: {token}\n\n"
            yield "data: [DONE]\n\n"
        except AuthenticationError:
            yield "event: error\ndata: Claude API 认证失败，请检查 API Key\n\n"
        except NotFoundError:
            yield "event: error\ndata: 请求的模型不可用\n\n"
        except APITimeoutError:
            yield "event: error\ndata: Claude API 请求超时\n\n"
        except APIError as e:
            yield f"event: error\ndata: Claude API 错误: {e.message}\n\n"

    return StreamingResponse(
        _generate(),
        media_type="text/event-stream",
        headers={"X-Model": stream_claude.model_name},
    )
