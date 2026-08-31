"""
Centralized configuration for the backend service.

All values are read from environment variables so the same code runs
unchanged locally (.env via docker-compose), in Kubernetes (ConfigMap/Secret),
and on Hugging Face Spaces (Space "Repository secrets").
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- Hugging Face Inference ---
    # Any text-generation / conversational model hosted on the HF Hub, e.g.:
    #   "openai/gpt-oss-20b", "mistralai/Mistral-7B-Instruct-v0.2",
    #   "meta-llama/Llama-3.1-8B-Instruct" (gated, needs access) ...
    hf_model_id: str = "HuggingFaceH4/zephyr-7b-beta"
    hf_api_token: str = ""  # required to call the HF Inference API
    hf_api_timeout: int = 30

    # --- Assistant behaviour ---
    system_prompt: str = (
        "You are a helpful, concise virtual assistant. "
        "Answer clearly and admit when you are not sure."
    )
    max_new_tokens: int = 512
    temperature: float = 0.7

    # --- Service ---
    app_name: str = "AI Virtual Assistant API"
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = ["*"]
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
