import time
import traceback

from anthropic import APIError, APITimeoutError, AuthenticationError, NotFoundError
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse

from claude_client import call_claude, stream_claude
from logger import get_logger, setup_logging
from models import PipelineRequest, PipelineResponse

setup_logging()
logger = get_logger(__name__)

app = FastAPI(title="Claude Pipeline", version="0.1.0")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start) * 1000
    logger.info(
        "%s %s | status=%d | duration=%.2fms",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/pipeline", response_model=PipelineResponse)
def pipeline(req: PipelineRequest):
    try:
        result = call_claude(req.prompt)
        return PipelineResponse(result=result, model=call_claude.model_name)
    except AuthenticationError:
        logger.error("auth failed\n%s", traceback.format_exc())
        raise HTTPException(status_code=401, detail="Claude API 认证失败，请检查 API Key")
    except NotFoundError:
        logger.error("model not found\n%s", traceback.format_exc())
        raise HTTPException(status_code=503, detail="请求的模型不可用")
    except APITimeoutError:
        logger.error("request timeout\n%s", traceback.format_exc())
        raise HTTPException(status_code=504, detail="Claude API 请求超时")
    except APIError as e:
        logger.error("api error: %s\n%s", e.message, traceback.format_exc())
        raise HTTPException(status_code=502, detail=f"Claude API 错误: {e.message}")


@app.post("/pipeline/stream")
def pipeline_stream(req: PipelineRequest):
    def _generate():
        try:
            for token in stream_claude(req.prompt):
                yield f"data: {token}\n\n"
            yield "data: [DONE]\n\n"
        except AuthenticationError:
            logger.error("stream auth failed\n%s", traceback.format_exc())
            yield "event: error\ndata: Claude API 认证失败，请检查 API Key\n\n"
        except NotFoundError:
            logger.error("stream model not found\n%s", traceback.format_exc())
            yield "event: error\ndata: 请求的模型不可用\n\n"
        except APITimeoutError:
            logger.error("stream request timeout\n%s", traceback.format_exc())
            yield "event: error\ndata: Claude API 请求超时\n\n"
        except APIError as e:
            logger.error("stream api error: %s\n%s", e.message, traceback.format_exc())
            yield f"event: error\ndata: Claude API 错误: {e.message}\n\n"

    return StreamingResponse(
        _generate(),
        media_type="text/event-stream",
        headers={"X-Model": stream_claude.model_name},
    )
