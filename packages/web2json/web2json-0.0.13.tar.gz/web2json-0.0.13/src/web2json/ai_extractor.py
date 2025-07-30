from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import requests
from pydantic import BaseModel
import json


class LLMClient(ABC):
    """Abstract base class for calling LLM APIs."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}

    @abstractmethod
    def call_api(self, prompt: str) -> str:
        """Call the underlying LLM API with the given prompt."""
        raise NotImplementedError


class OllamaLLMClient(LLMClient):
    """LLM client for a local Ollama server."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self.host = self.config.get("host", "http://localhost:11434")
        self.model_name = self.config.get("model_name", "gemma3:12b")
        self.generate_kwargs = self.config.get("generate_kwargs", {})

    def call_api(self, prompt: str) -> str:
        url = f"{self.host}/api/generate"
        # Build the request payload expected by the Ollama API
        payload: Dict[str, Any] = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": True,
        }
        payload.update(self.generate_kwargs)

        try:
            response = requests.post(url, json=payload, stream=True, timeout=60)
            response.raise_for_status()

            output = []
            # The API streams back JSON objects line by line
            for line in response.iter_lines():
                if line:
                    try:
                        parsed = json.loads(line.decode("utf-8"))
                        output.append(parsed.get("response", ""))
                    except json.JSONDecodeError:
                        continue
            return "".join(output).strip()

        except requests.RequestException as exc:
            raise RuntimeError(f"Ollama API request failed: {exc}") from exc


class OpenAILLMClient(LLMClient):
    """LLM client for the OpenAI API."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self.api_key = self.config.get("api_key")
        self.model_name = self.config.get("model_name", "gpt-3.5-turbo")
        self.base_url = self.config.get("base_url", "https://api.openai.com/v1")

    def call_api(self, prompt: str) -> str:
        if not self.api_key:
            raise RuntimeError("OpenAI API key not provided")
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except requests.RequestException as exc:
            raise RuntimeError(f"OpenAI API request failed: {exc}") from exc


class AIExtractor:
    """Use an LLM to extract structured data from content."""

    def __init__(self, llm_client: LLMClient, prompt_template: str) -> None:
        self.llm_client = llm_client
        self.prompt_template = prompt_template

    def extract(self, content: str, schema: BaseModel) -> str:
        """Generate structured data for ``content`` using the provided schema.

        The schema is converted to a JSON schema and inserted into the
        ``prompt_template``. The resulting prompt is sent to the underlying
        language model and the raw response text is returned.

        Args:
            content: Preprocessed content to analyse.
            schema: Pydantic model describing the desired output structure.

        Returns:
            Raw text response from the language model.
        """
        # Format the prompt with the cleaned content and JSON schema
        prompt = self.prompt_template.format(
            content=content, schema=schema.model_json_schema()
        )
        return self.llm_client.call_api(prompt)
