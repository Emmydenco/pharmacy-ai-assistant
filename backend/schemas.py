"""Pydantic models shared by the API and its tests."""

from typing import Literal

from pydantic import BaseModel, Field


class HistoryMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4_000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2_000)
    history: list[HistoryMessage] = Field(default_factory=list, max_length=20)


class SourceReference(BaseModel):
    label: str
    url: str


class ChatResponse(BaseModel):
    status: Literal["ok", "blocked", "error"]
    message: str
    category: str
    simulated: bool
    provider: str
    source: SourceReference | None = None
    disclaimer: str
