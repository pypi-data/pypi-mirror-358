import os
import sys
import json
import requests
from typing import Optional
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from web2json.cli import parse_schema_input, run_pipeline
from web2json.ai_extractor import (
    LLMClient,
    AIExtractor,
    OllamaLLMClient,
    OpenAILLMClient,
)
from web2json.preprocessor import BasicPreprocessor
from web2json.postprocessor import PostProcessor
from web2json.pipeline import Pipeline
from web2json.crawler import crawl_urls
from pydantic import BaseModel


class DummyLLM(LLMClient):
    def call_api(self, prompt: str) -> str:
        return json.dumps({"title": "My Title", "content": "Hello"})


def test_parse_schema_input():
    schema_text = '{"type": "object", "properties": {"title": {"type": "string"}, "content": {"type": "string"}}}'
    model = parse_schema_input(schema_text)
    fields = set(model.model_fields.keys())
    assert fields == {"title", "content"}


def test_run_pipeline_with_dummy_llm():
    schema_text = '{"type": "object", "properties": {"title": {"type": "string"}, "content": {"type": "string"}}}'
    content = "<h1>My Title</h1><p>Hello</p>"
    schema_model = parse_schema_input(schema_text)
    llm = DummyLLM()
    extractor = AIExtractor(llm, "{content}\n{schema}")
    pipeline = Pipeline(BasicPreprocessor(), extractor, PostProcessor())
    result = pipeline.run(content, False, schema_model)
    assert result == {"title": "My Title", "content": "Hello"}


def test_parse_schema_input_json_schema():
    schema_json = """
    {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "views": {"type": "integer"}
        },
        "required": ["title", "views"]
    }
    """
    model = parse_schema_input(schema_json)
    fields = model.model_fields
    assert set(fields.keys()) == {"title", "views"}
    assert fields["title"].annotation == Optional[str]
    assert fields["views"].annotation == Optional[int]


def test_run_pipeline_function(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    def dummy_call_api(self, prompt: str) -> str:
        return json.dumps({"title": "My Title", "content": "Hello"})

    monkeypatch.setattr(OllamaLLMClient, "call_api", dummy_call_api)
    result = run_pipeline(
        "<h1>My Title</h1><p>Hello</p>",
        False,
        '{"type": "object", "properties": {"title": {"type": "string"}, "content": {"type": "string"}}}',
        model_name="dummy"
    )
    assert result == {"title": "My Title", "content": "Hello"}


def test_run_pipeline_prefers_openai(monkeypatch):
    def openai_api(self, prompt: str) -> str:
        return json.dumps({"title": "From OpenAI"})

    monkeypatch.setattr(OpenAILLMClient, "call_api", openai_api)
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")

    result = run_pipeline(
        "<h1>Hi</h1>",
        False,
        '{"type": "object", "properties": {"title": {"type": "string"}}}',
        model_name="ignored",
    )

    assert result == {"title": "From OpenAI"}
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)


def test_run_pipeline_ignores_placeholder_key(monkeypatch):
    def dummy_ollama(self, prompt: str) -> str:
        return json.dumps({"title": "From Ollama"})

    monkeypatch.setattr(OllamaLLMClient, "call_api", dummy_ollama)
    monkeypatch.setenv("OPENAI_API_KEY", "${{ secrets.OPENAI_API_KEY }}")

    result = run_pipeline(
        "<h1>Hi</h1>",
        False,
        '{"type": "object", "properties": {"title": {"type": "string"}}}',
        model_name="ignored",
    )

    assert result == {"title": "From Ollama"}
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)


def test_run_pipeline_missing_field(monkeypatch):
    def dummy_call_api(self, prompt: str) -> str:
        return json.dumps({"title": "My Title"})

    monkeypatch.setattr(OllamaLLMClient, "call_api", dummy_call_api)
    result = run_pipeline(
        "<h1>My Title</h1>",
        False,
        '{"type": "object", "properties": {"title": {"type": "string"}, "content": {"type": "string"}, "views": {"type": "integer"}}}',
        model_name="dummy",
    )
    assert result == {"title": "My Title", "content": None, "views": None}


def test_crawl_urls(monkeypatch):
    pages = {
        "https://example.com/docs/": "<a href='/docs/page1.html'>p1</a><a href='/about'>about</a>",
        "https://example.com/docs/page1.html": "<a href='/docs/page2.html'>p2</a>",
        "https://example.com/docs/page2.html": ""
    }

    def fake_get(url, timeout=10):
        class Resp:
            def __init__(self, text):
                self.text = text
        return Resp(pages[url])

    monkeypatch.setattr(requests, "get", fake_get)

    urls = crawl_urls("https://example.com/docs/", max_pages=2)
    assert urls == [
        "https://example.com/docs/",
        "https://example.com/docs/page1.html",
    ]


def test_cli_output_file(tmp_path, monkeypatch):
    def dummy_call_api(self, prompt: str) -> str:
        return json.dumps({"title": "My Title", "content": "Hello"})

    monkeypatch.setattr(OllamaLLMClient, "call_api", dummy_call_api)
    out_file = tmp_path / "out.json"
    argv = [
        "prog",
        "<h1>My Title</h1><p>Hello</p>",
        "--schema",
        '{"type": "object", "properties": {"title": {"type": "string"}, "content": {"type": "string"}}}',
        "--model_name",
        "dummy",
        "--output",
        str(out_file),
    ]
    monkeypatch.setattr(sys, "argv", argv)
    from web2json.cli import main

    main()
    with open(out_file, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    assert data == {"title": "My Title", "content": "Hello"}

def test_run_pipeline_validation_error(monkeypatch):
    def invalid_api(self, prompt: str) -> str:
        return json.dumps({"title": "Hello", "views": "not_an_int"})

    monkeypatch.setattr(OllamaLLMClient, "call_api", invalid_api)
    result = run_pipeline(
        "<h1>Hi</h1>",
        False,
        '{"type": "object", "properties": {"title": {"type": "string"}, "views": {"type": "integer"}}}',
        model_name="dummy",
    )
    assert result == {"title": "Hello", "views": "not_an_int"}


def test_run_pipeline_fetch_error(monkeypatch):
    def fetch_error(self, url: str):
        raise ValueError("fail")

    monkeypatch.setattr(BasicPreprocessor, "_fetch_content", fetch_error)
    with pytest.raises(ValueError):
        run_pipeline(
            "http://bad",
            True,
            '{"type": "object", "properties": {"title": {"type": "string"}}}',
            model_name="dummy",
        )


def test_run_pipeline_without_content_field(monkeypatch):
    created_config = {}

    class DummyPreprocessor(BasicPreprocessor):
        def __init__(self, config=None):
            super().__init__(config)
            created_config.update(self.config)

    def dummy_call_api(self, prompt: str) -> str:
        return json.dumps({"title": "Hello"})

    monkeypatch.setattr(OllamaLLMClient, "call_api", dummy_call_api)
    monkeypatch.setattr(sys.modules["web2json.cli"], "BasicPreprocessor", DummyPreprocessor)

    result = run_pipeline(
        "<h1>Hello</h1>",
        False,
        '{"type": "object", "properties": {"title": {"type": "string"}}}',
        model_name="dummy",
    )

    assert result == {"title": "Hello"}
    assert created_config.get("remove_boilerplate") is False


def test_run_pipeline_with_content_field(monkeypatch):
    created_config = {}

    class DummyPreprocessor(BasicPreprocessor):
        def __init__(self, config=None):
            super().__init__(config)
            created_config.update(self.config)

    def dummy_call_api(self, prompt: str) -> str:
        return json.dumps({"content": "Body"})

    monkeypatch.setattr(OllamaLLMClient, "call_api", dummy_call_api)
    monkeypatch.setattr(sys.modules["web2json.cli"], "BasicPreprocessor", DummyPreprocessor)

    result = run_pipeline(
        "<p>Body</p>",
        False,
        '{"type": "object", "properties": {"content": {"type": "string"}}}',
        model_name="dummy",
    )

    assert result == {"content": "Body"}
    assert created_config.get("remove_boilerplate") is True


def test_load_schema_and_postprocess_with_prompt(tmp_path):
    schema_path = tmp_path / "schema.json"
    schema_data = {
        "type": "object",
        "properties": {
            "title": {"type": "string"}
        },
        "prompt": "Extra instructions"
    }
    with open(schema_path, "w", encoding="utf-8") as fh:
        json.dump(schema_data, fh)

    from web2json.cli import load_schema_and_postprocess

    schema_text, post_cfg, prompt = load_schema_and_postprocess(str(schema_path))

    assert json.loads(schema_text)["properties"]["title"]["type"] == "string"
    assert post_cfg == {}
    assert prompt == "Extra instructions"


def test_run_pipeline_includes_extra_prompt(monkeypatch):
    captured = {}

    def dummy_call_api(self, prompt: str) -> str:
        captured["prompt"] = prompt
        return json.dumps({"title": "Hi"})

    monkeypatch.setattr(OllamaLLMClient, "call_api", dummy_call_api)

    run_pipeline(
        "<h1>Hi</h1>",
        False,
        '{"type": "object", "properties": {"title": {"type": "string"}}}',
        model_name="dummy",
        extra_prompt="Please extract carefully",
    )

    assert "Please extract carefully" in captured.get("prompt", "")

