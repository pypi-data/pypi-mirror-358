# web2json

`web2json` converts web content into structured JSON using a local [Ollama](https://ollama.com/) server. It exposes a simple command line interface.

This repository began from code by [abdo-Mansour](https://huggingface.co/abdo-Mansour) and was adapted for use at the NOAA Global Systems Laboratory.

[![PyPI version](https://badge.fury.io/py/web2json.svg)](https://pypi.org/project/web2json/)

## Installation

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install the package in editable mode so the `web2json` command is available:
   ```bash
   pip install -e .
   ```
4. Optionally set `OLLAMA_HOST` (or `OLLAMA_BASE_URL`) and `OLLAMA_MODEL` to point to your Ollama instance and model. The dev container defaults to `gemma3:12b`.
5. Set `OPENAI_API_KEY` to use the OpenAI API instead of the local Ollama server. When this variable is present, the `OLLAMA_*` settings are ignored. Use `OPENAI_MODEL` to choose a model (default `gpt-3.5-turbo`). If `OPENAI_API_KEY` is left undefined in the dev container, it may be set to a placeholder value like `${{ secrets.OPENAI_API_KEY }}`; this is ignored and the local Ollama server will be used.

## Command line usage

Run the CLI module with the content to process and your schema definition. The tool can also crawl multiple pages from a starting URL:

```bash
python -m web2json.cli --schema SCHEMA [--url] [--crawl] [--max_pages N] [--output FILE] CONTENT
```

- `CONTENT` can be a URL or raw text.
- `--url` tells the tool to treat `CONTENT` as a URL.
- `--schema` accepts a JSON Schema definition directly or the path to a JSON file containing it.
- When loading a schema from a file, an optional `prompt` string may be included to append additional instructions for the language model.
- The file may also contain a `postprocess` section with `link_patterns` that map field names to regular expressions and optional `css_selectors` for extracting values using CSS paths. These settings help fill in missing data based on the cleaned HTML.
- `--crawl` treats the content as a starting URL and processes each discovered page.
- `--max_pages` limits how many pages are crawled when using `--crawl` (default: 10).
- `--debug` prints the preprocessed content and other intermediate information to stderr.
- `--output` writes the resulting JSON to `FILE` instead of only printing to stdout.
- When a URL is provided, relative links in the page are converted to absolute URLs so they can be extracted correctly. The page URL itself is assigned to the `url` field if that key exists in the schema. Missing URLs can be filled using regex patterns in the post-processor when provided.
- Character encoding is determined automatically when downloading pages so accented characters are preserved correctly.
- If your schema defines a `content` field, the CLI removes common header, footer
  and navigation sections (including the official U.S. government banner) so that
  field only contains the main page body.

Example:

```bash
python -m web2json.cli https://example.com --url --schema '{"properties": {"title": {"type": "string", "description": "Page title"}}}'
```

You can place the schema in a file instead. For example `schema.json`:

```json
{
  "properties": {"title": {"type": "string"}},
  "postprocess": {
    "link_patterns": {"ftp_download": "(ftp://\\S+)"},
    "css_selectors": {"preview": {"selector": "a.preview", "attr": "href"}}
  }
}
```

Run the CLI using that file:

```bash
python -m web2json.cli https://example.com --url --schema schema.json
```

To crawl and process multiple pages under `https://example.com/docs/`:

```bash
python -m web2json.cli https://example.com/docs/ --crawl --schema '{"properties": {"title": {"type": "string"}}}'
```

The extracted JSON is printed to standard output. Unicode characters are
preserved so accent marks appear correctly. Any schema validation errors are
reported to standard error. When `--debug` is used, intermediate output such as the cleaned HTML is also sent to standard error.


## Library usage

The pipeline components are exposed as Python classes so you can build custom workflows.

```python
from web2json.cli import parse_schema_input
from web2json.preprocessor import BasicPreprocessor
from web2json.postprocessor import PostProcessor
from web2json.pipeline import Pipeline
from web2json.ai_extractor import OllamaLLMClient

schema_json = '{"properties": {"title": {"type": "string"}, "content": {"type": "string"}}}'
schema = parse_schema_input(schema_json)
# Exclude header, footer and navigation markup when cleaning HTML
pre = BasicPreprocessor(config={"remove_boilerplate": True})
llm = OllamaLLMClient()
post = PostProcessor()
pipe = Pipeline(pre, llm, post)
result = pipe.run("<h1>Title</h1>", False, schema)
```

Regex `link_patterns` and `css_selectors` can be supplied for special cases where the language model misses links or other values.

The post-processor also applies simple heuristics to recover **categories**,
**keywords**, and **notable features** directly from the cleaned HTML. These
values replace the model output when they differ from the page content.

## Code overview

1. **Preprocessor** - cleans and normalizes HTML or text input.
   When `remove_boilerplate` is enabled, common header, footer and navigation
   elements (like the U.S. government banner) are stripped before text
   extraction. The CLI turns this setting on automatically if your schema
   includes a `content` field.
2. **AIExtractor** - sends a prompt to the LLM and returns the raw JSON text.
3. **PostProcessor** - repairs malformed JSON and adds missing URLs.

These pieces are wired together by the `Pipeline` class and driven by the CLI script.



## Running tests

Install `pytest` and run the suite:

```bash
pip install -r requirements.txt
pip install pytest
pytest
```

Tests also run automatically through GitHub Actions on every push and pull request.

## Dev container

The `.devcontainer` folder provides a configuration for
[Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers)
and GitHub Codespaces. Open the project in Visual Studio Code and choose
**Reopen in Container** to automatically build the image and install the
dependencies listed in `requirements.txt`.
Environment variables like `OPENAI_API_KEY`, `OLLAMA_BASE_URL`,
and `OLLAMA_MODEL` are set through the `remoteEnv` section of
`devcontainer.json`. The repository is mounted inside the container at
`/workspace/web2json` and the `site-config` directory is available at
`/workspace/site-config`.

## Additional tests

The test suite now covers the CLI utilities as well as core components.
Additional tests live under `tests/` and exercise:
- The `AIExtractor` prompt formatting logic.
- Error handling in `PostProcessor.process` when invalid JSON is returned.
- The `_fetch_content` method in `BasicPreprocessor`.
- run_pipeline success and error scenarios.
- Pipeline operation with a mocked LLM.
