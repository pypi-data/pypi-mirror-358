import json
import requests
import sseclient
from typing import Dict, List, Iterator, Generator

from .config import Model
from .exceptions import APIError

def _byte_iterator_to_generator(iterator: Iterator[bytes]) -> Generator[bytes, None, None]:
    yield from iterator

class ApiClient:
    def __init__(self, model: Model):
        self.model = model
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.model.openai_api_key}",
            "Content-Type": "application/json"
        })

    def call(self, messages: List[Dict[str, str]], use_sse: bool) -> Iterator[str]:
        body = {
            "model": self.model.model_tag,
            "messages": messages,
            "stream": use_sse
        }
        
        if 0 <= self.model.temperature <= 2:
            body["temperature"] = self.model.temperature

        try:
            response = self.session.post(
                self.model.api_base_url,
                json=body,
                stream=use_sse
            )
            response.raise_for_status()

            if use_sse:
                client = sseclient.SSEClient(_byte_iterator_to_generator(response.iter_content()))
                is_sse_done = False
                for event in client.events():
                    if event.data == "[DONE]":
                        is_sse_done = True
                        break
                    try:
                        chunk = json.loads(event.data)
                        delta = chunk['choices'][0]['delta']
                        content = delta.get('content')
                        if content:
                            yield content
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue
                if not is_sse_done:
                    raise APIError("SSE client returns empty. It might caused by wrong BaseURL.")
            else:
                data = response.json()
                content = data['choices'][0]['message']['content']
                yield content

        except requests.RequestException as e:
            raise APIError(f"API request failed: {e}") from e
