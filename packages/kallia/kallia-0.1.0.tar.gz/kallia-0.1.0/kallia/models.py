from typing import List
from pydantic import BaseModel


class ChunksRequest(BaseModel):
    url: str
    page_number: int = 1
    temperature: float = 0.0
    max_tokens: int = 8192


class Chunk(BaseModel):
    original_text: str
    concise_summary: str


class ChunksResponse(BaseModel):
    chunks: List[Chunk] = []
