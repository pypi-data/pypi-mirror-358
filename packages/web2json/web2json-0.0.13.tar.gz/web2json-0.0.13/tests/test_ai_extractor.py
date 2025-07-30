import os
import sys
import json
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from web2json.ai_extractor import AIExtractor, LLMClient
from web2json.cli import parse_schema_input

class CaptureLLM(LLMClient):
    def __init__(self):
        super().__init__()
        self.prompt = None

    def call_api(self, prompt: str) -> str:
        self.prompt = prompt
        return json.dumps({"title": "My Title"})

def test_ai_extractor_formats_prompt():
    llm = CaptureLLM()
    schema = parse_schema_input('{"type": "object", "properties": {"title": {"type": "string"}}}')
    extractor = AIExtractor(llm, "CONTENT:{content} SCHEMA:{schema}")
    extractor.extract("hello", schema)
    assert "hello" in llm.prompt
    assert 'title' in llm.prompt
