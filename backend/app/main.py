"""FastAPI application entrypoint for the AI Virtual Assistant backend."""
import logging

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings, get_settings
from app.llm_client import LLMClientError, generate_reply
from app.schemas import ChatRequest, ChatResponse, HealthResponse

settings = get_settings()
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Backend API for the LLM-powered virtual assistant (AI Systems Engineering project).",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse, tags=["ops"])
def health(cfg: Settings = Depends(get_settings)) -> HealthResponse:
    """Liveness/readiness probe used by Docker/Kubernetes."""
    return HealthResponse(status="ok", model=cfg.hf_model_id)


@app.post(f"{settings.api_prefix}/chat", response_model=ChatResponse, tags=["assistant"])
def chat(req: ChatRequest, cfg: Settings = Depends(get_settings)) -> ChatResponse:
    """Send a user message (plus optional prior turns) and get the assistant's reply."""
    try:
        reply = generate_reply(req.message, req.history, cfg)
    except LLMClientError as exc:
        logger.error("LLM call failed: %s", exc)
        raise HTTPException(status_code=502, detail="The language model backend is unavailable.") from exc
    return ChatResponse(reply=reply, model=cfg.hf_model_id)


@app.get("/", tags=["ops"])
def root() -> dict:
    return {"service": settings.app_name, "docs": "/docs", "health": "/health"}
