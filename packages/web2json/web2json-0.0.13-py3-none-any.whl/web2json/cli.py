import argparse
import json
import os
import sys
from typing import Any, Dict, Optional
import dotenv

# Import shared pipeline modules
from .preprocessor import BasicPreprocessor
from .ai_extractor import AIExtractor, OllamaLLMClient, OpenAILLMClient
from .postprocessor import PostProcessor

# Default patterns used by ``PostProcessor`` to recover missing URLs
DEFAULT_LINK_PATTERNS: Dict[str, str] = {}
from .pipeline import Pipeline
from .crawler import crawl_urls

from pydantic import BaseModel, Field, create_model


def parse_schema_input(schema_input: str) -> BaseModel:
    """Parse a JSON Schema string into a ``BaseModel`` subclass.

    Args:
        schema_input: Text describing the desired schema.

    Returns:
        A dynamically created ``BaseModel`` representing the schema.
    """
    schema_input = schema_input.strip()
    if not schema_input:
        return create_model(
            "DefaultSchema",
            title=(Optional[str], Field(default=None, description="Title of the content")),
            content=(Optional[str], Field(default=None, description="Main content")),
        )

    if not schema_input.startswith("{"):
        raise ValueError("Schema must be provided as JSON Schema text")

    schema_dict = json.loads(schema_input)
    return json_schema_to_basemodel(schema_dict)


def json_schema_to_basemodel(schema_dict: Dict[str, Any]) -> BaseModel:
    """Convert a JSON Schema dictionary to a dynamic ``BaseModel``."""
    fields = {}
    properties = schema_dict.get("properties", {})
    for field_name, field_info in properties.items():
        field_type = get_python_type(field_info.get("type", "string"))
        field_description = field_info.get("description", "")
        fields[field_name] = (
            Optional[field_type],
            Field(default=None, description=field_description),
        )

    return create_model("DynamicSchema", **fields)




def get_python_type(type_str: str):
    """Return the Python type object for a simple string alias."""
    type_str = type_str.lower().strip()
    mapping = {
        "string": str,
        "str": str,
        "integer": int,
        "int": int,
        "number": float,
        "float": float,
        "boolean": bool,
        "bool": bool,
        "array": list,
        "list": list,
        "object": dict,
        "dict": dict,
    }
    return mapping.get(type_str, str)


def load_schema_and_postprocess(path: str) -> tuple[str, Dict[str, Any], Optional[str]]:
    """Load a schema JSON file and return the schema text, postprocess options and optional prompt."""
    with open(path, "r", encoding="utf-8") as fh:
        config = json.load(fh)
    postprocess = config.pop("postprocess", {})
    prompt = config.pop("prompt", None)
    schema_text = json.dumps(config)
    return schema_text, postprocess, prompt


def run_pipeline(
    content: str,
    is_url: bool,
    schema_text: str,
    model_name: str,
    *,
    debug: bool = False,
    postprocess_config: Optional[Dict[str, Any]] = None,
    extra_prompt: Optional[str] = None,
) -> Dict[str, Any]:
    """Run the entire extraction pipeline for a single piece of content.

    Parameters:
        extra_prompt: Additional instructions appended to the LLM prompt.
    """
    # Parse the schema text into a Pydantic model
    schema_model = parse_schema_input(schema_text)
    # Template used to construct the LLM prompt
    has_content_field = "content" in schema_model.model_fields
    prompt_lines = [
        "Extract structured data from the cleaned web content below using the provided schema.",
        "",
        "Content to analyze:",
        "{content}",
        "",
        "Schema requirements:",
        "{schema}",
        "",
        "Guidelines:",
        "- Use only the information present in the content. Do not guess values.",
        "- Resolve any relative URLs against the 'Source URL' prefix if one is given.",
    ]
    if has_content_field:
        prompt_lines.append(
            "- Ignore page headers and footers when populating the 'content' field."
        )
    prompt_lines.append(
        "- Output a single JSON object matching the schema exactly. Use null when information is missing."
    )
    if extra_prompt:
        prompt_lines.append("")
        prompt_lines.append(extra_prompt)
    prompt_template = "\n".join(prompt_lines)

    # Create pipeline components
    preprocessor = BasicPreprocessor(
        config={"keep_tags": False, "remove_boilerplate": has_content_field}
    )
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key and not openai_key.startswith("${"):
        llm = OpenAILLMClient(
            config={
                "api_key": openai_key,
                "model_name": os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            }
        )
    else:
        ollama_host = os.getenv("OLLAMA_BASE_URL") or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        llm = OllamaLLMClient(
            config={
                "host": ollama_host,
                "model_name": os.getenv("OLLAMA_MODEL", model_name),
            }
        )
    ai_extractor = AIExtractor(llm_client=llm, prompt_template=prompt_template)
    link_patterns = DEFAULT_LINK_PATTERNS.copy()
    css_selectors: Optional[Dict[str, Any]] = None
    if postprocess_config:
        link_patterns.update(postprocess_config.get("link_patterns", {}))
        css_selectors = postprocess_config.get("css_selectors")
    postprocessor = PostProcessor(link_patterns=link_patterns, css_selectors=css_selectors)
    pipeline = Pipeline(preprocessor, ai_extractor, postprocessor, debug=debug)
    # Execute the pipeline
    result = pipeline.run(content, is_url, schema_model)

    if is_url and "url" in schema_model.model_fields:
        result["url"] = content

    for field_name in schema_model.model_fields:
        result.setdefault(field_name, None)

    # Validate the resulting JSON against the provided schema
    try:
        validated = schema_model(**result)
        return validated.model_dump()
    except Exception as exc:  # Catch validation errors
        print(f"Schema validation error: {exc}", file=sys.stderr)
        return result


def crawl_and_extract(
    start_url: str,
    schema_text: str,
    model_name: str,
    max_pages: int,
    *,
    debug: bool = False,
    postprocess_config: Optional[Dict[str, Any]] = None,
    extra_prompt: Optional[str] = None,
) -> Dict[str, Any]:
    """Crawl ``start_url`` and run the extraction pipeline on each page.

    Parameters:
        extra_prompt: Additional instructions appended to the LLM prompt for each page.
    """
    # Find all pages starting from ``start_url``
    urls = crawl_urls(start_url, max_pages)
    print("URLs found:", file=sys.stderr)
    for url in urls:
        print(url, file=sys.stderr)
    results: Dict[str, Any] = {}
    # Run the pipeline on each discovered URL
    for url in urls:
        results[url] = run_pipeline(
            url,
            True,
            schema_text,
            model_name,
            debug=debug,
            postprocess_config=postprocess_config,
            extra_prompt=extra_prompt,
        )
    return results


def main() -> None:
    """Entry point for the ``web2json`` command line interface."""
    parser = argparse.ArgumentParser(description="Convert web content to JSON")
    parser.add_argument("content", help="URL or raw text to process")
    parser.add_argument("--url", action="store_true", help="Treat content as a URL")
    parser.add_argument("--crawl", action="store_true", help="Crawl starting from the given URL")
    parser.add_argument("--max_pages", type=int, default=10, help="Maximum pages to crawl")
    parser.add_argument("--schema", default="site-config/default.json", help="Schema text or path to file")
    parser.add_argument("--model_name", default="gemma3:12b", help="Name of the Ollama model to use.")
    parser.add_argument(
        "--output",
        help="Save the resulting JSON to a file instead of only printing",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print intermediate preprocessing and extraction information to stderr",
    )
    args = parser.parse_args()

    dotenv.load_dotenv()

    schema_text = args.schema
    post_cfg: Optional[Dict[str, Any]] = None
    extra_prompt: Optional[str] = None
    if os.path.isfile(schema_text):
        try:
            schema_text, post_cfg, extra_prompt = load_schema_and_postprocess(schema_text)
        except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
            print(f"Error loading schema and postprocess configuration: {e}", file=sys.stderr)
            with open(schema_text, "r", encoding="utf-8") as fh:
                schema_text = fh.read()

    if args.crawl:
        results = crawl_and_extract(
            args.content,
            schema_text,
            args.model_name,
            args.max_pages,
            debug=args.debug,
            postprocess_config=post_cfg,
            extra_prompt=extra_prompt,
        )
        output_json = json.dumps(results, indent=2, ensure_ascii=False)
        print(output_json)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as fh:
                fh.write(output_json)

    else:
        result = run_pipeline(
            args.content,
            args.url,
            schema_text,
            args.model_name,
            debug=args.debug,
            postprocess_config=post_cfg,
            extra_prompt=extra_prompt,
        )
        if not result or "error" in result:  # Check for empty result or error key
            print("Error: Failed to process content.", file=sys.stderr)
            sys.exit(1)
        output_json = json.dumps(result, indent=2, ensure_ascii=False)
        print(output_json)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as fh:
                fh.write(output_json)


if __name__ == "__main__":
    main()
