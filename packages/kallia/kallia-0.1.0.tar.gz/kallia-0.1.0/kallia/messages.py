import requests
import kallia.settings as Settings
from typing import Any, Dict, List, Optional


class Messages:
    @staticmethod
    def send(
        messages: List[Dict[str, Any]],
        temperature: float,
        max_tokens: int,
        stream: bool = False,
    ) -> Optional[str]:
        endpoint_url = f"{Settings.BASE_URL}/chat/completions"
        headers = {
            "Authorization": f"Bearer {Settings.API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "model": Settings.MODEL,
            "stream": stream,
        }
        response = requests.post(endpoint_url, headers=headers, json=payload)
        data = response.json()
        return data["choices"][0]["message"]["content"]
