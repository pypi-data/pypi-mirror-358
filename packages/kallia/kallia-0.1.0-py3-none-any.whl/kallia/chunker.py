import json
import kallia.models as Models
import kallia.prompts as Prompts
from typing import List
from kallia.utils import Utils
from kallia.messages import Messages


class Chunker:
    @staticmethod
    def create(text: str, temperature: float, max_tokens: int) -> List[Models.Chunk]:
        messages = [
            {"role": "system", "content": Prompts.SEMANTIC_CHUNKING_PROMPT},
            {"role": "user", "content": text},
        ]
        response = Messages.send(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        content = Utils.unwrap("information", response)
        return json.loads(content)
