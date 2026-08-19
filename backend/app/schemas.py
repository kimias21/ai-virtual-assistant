"""Pydantic request/response models for the API."""
from enum import Enum

from pydantic import BaseModel, Field


class Role(str, Enum):
    system = "system"
    user = "user"
    assistant = "assistant"


class Message(BaseModel):
    role: Role
    content: str = Field(..., min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000, description="Latest user message")
    history: list[Message] = Field(
        default_factory=list,
        description="Prior turns of the conversation, oldest first (excludes the current message).",
    )


class ChatResponse(BaseModel):
    reply: str
    model: str


class HealthResponse(BaseModel):
    status: str
    model: str
