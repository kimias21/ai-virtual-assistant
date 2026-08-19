"""
Thin wrapper around the Hugging Face Inference API.

Kept isolated from the FastAPI routes so it can be unit-tested in isolation
(mock this module in tests instead of hitting the network) and so the model
backend can be swapped later (e.g. a locally fine-tuned model) without
touching the API layer.
"""
from __future__ import annotations

import logging

from huggingface_hub import InferenceClient
from huggingface_hub.errors import HfHubHTTPError

from app.config import Settings
from app.schemas import Message, Role

logger = logging.getLogger(__name__)


class LLMClientError(RuntimeError):
    """Raised when the upstream Hugging Face call fails."""


def _build_client(settings: Settings) -> InferenceClient:
    return InferenceClient(model=settings.hf_model_id, token=settings.hf_api_token or None,
                            timeout=settings.hf_api_timeout)


def generate_reply(user_message: str, history: list[Message], settings: Settings) -> str:
    """Call the HF chat-completion API and return the assistant's reply text."""
    client = _build_client(settings)

    messages = [{"role": Role.system.value, "content": settings.system_prompt}]
    messages += [{"role": m.role.value, "content": m.content} for m in history]
    messages.append({"role": Role.user.value, "content": user_message})

    try:
        completion = client.chat_completion(
            messages=messages,
            max_tokens=settings.max_new_tokens,
            temperature=settings.temperature,
        )
        return completion.choices[0].message.content.strip()
    except HfHubHTTPError as exc:
        logger.exception("Hugging Face Inference API call failed")
        raise LLMClientError(str(exc)) from exc
    except Exception as exc:  # noqa: BLE001 - surface any unexpected upstream failure uniformly
        logger.exception("Unexpected error calling the LLM backend")
        raise LLMClientError(str(exc)) from exc
