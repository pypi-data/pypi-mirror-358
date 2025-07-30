from json_repair import repair_json
import json
from typing import Dict, Optional, Any
import re


from bs4 import BeautifulSoup


class PostProcessor:

    def __init__(
        self,
        link_patterns: Optional[Dict[str, str]] = None,
        css_selectors: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Create a postprocessor with optional link and selector patterns.

        Args:
            link_patterns: Mapping of output field names to regex patterns used
                to populate missing URL fields.
            css_selectors: Mapping of field names to CSS selector configs used
                to extract values from the raw HTML when those fields are
                missing. A config may be a selector string or an object with
                ``selector`` and optional ``attr`` and ``list`` keys.
        """
        self.link_patterns = link_patterns or {}
        self.css_selectors = css_selectors or {}

    def _get_nested(self, data: Dict[str, Any], path: str) -> Optional[Any]:
        obj: Any = data
        for part in path.split("."):
            if not isinstance(obj, dict) or part not in obj:
                return None
            obj = obj[part]
        return obj

    def _set_nested(self, data: Dict[str, Any], path: str, value: Any) -> None:
        obj = data
        parts = path.split(".")
        for part in parts[:-1]:
            if part not in obj or not isinstance(obj[part], dict):
                obj[part] = {}
            obj = obj[part]
        obj[parts[-1]] = value

    def process(
        self,
        response: str,
        preprocessed: Optional[str] = None,
        html: Optional[str] = None,
    ) -> dict:
        """Parse JSON from the LLM response and optionally fill missing URLs.

        Args:
            response: The raw text returned by the language model.
            preprocessed: The cleaned content that was provided to the model.

        Returns:
            A dictionary of the parsed JSON data. When ``preprocessed`` is
            supplied and ``link_patterns`` are set, missing URL fields are
            recovered by applying the regex patterns to the cleaned content.
        """
        json_response = {}
        try:
            # Extract the JSON from the generated text. Handle variations in
            # output format.
            json_string = response
            if "```json" in response:
                json_string = response.split("```json")[1].split("```", 1)[0]
            elif "{" in response and "}" in response:
                start_index = response.find("{")
                end_index = response.rfind("}") + 1
                json_string = response[start_index:end_index]

            json_response = json.loads(repair_json(json_string))
        except Exception as e:
            print(f"Error parsing JSON: {e}")
            print(f"Generated text: {response}")
            json_response = {}

        if preprocessed:
            for field, pattern in self.link_patterns.items():
                current = self._get_nested(json_response, field)
                html_matches = re.findall(pattern, preprocessed, re.S)
                if html_matches:
                    match = html_matches[-1]
                    html_value = match[-1] if isinstance(match, tuple) else match
                    if current is None or not re.search(pattern, str(current)):
                        self._set_nested(json_response, field, html_value)

        if html and self.css_selectors:
            soup = BeautifulSoup(html, "html.parser")
            for field, cfg in self.css_selectors.items():
                if isinstance(cfg, str):
                    selector = cfg
                    attr = "text"
                    is_list = False
                else:
                    selector = cfg.get("selector")
                    attr = cfg.get("attr", "text")
                    is_list = cfg.get("list", False)
                if not selector:
                    continue
                elements = soup.select(selector)
                if not elements:
                    continue
                values = []
                for el in elements:
                    val = el.get(attr) if attr != "text" else el.get_text(strip=True)
                    if val:
                        values.append(val)
                    if not is_list:
                        break
                if not values:
                    continue
                if is_list:
                    if not self._get_nested(json_response, field):
                        self._set_nested(json_response, field, values)
                else:
                    if not self._get_nested(json_response, field):
                        self._set_nested(json_response, field, values[0])

        if preprocessed:
            if "notable_features" not in json_response or not json_response.get("notable_features"):
                feat_match = re.search(
                    r"Notable Features\n(?P<section>.+?)(?:\n(?:Contacts|Related Datasets|Search|Science On a Sphere))",
                    preprocessed,
                    re.S,
                )
                if feat_match:
                    lines = [
                        line.strip(" -*")
                        for line in feat_match.group("section").split("\n")
                        if line.strip() and not line.lower().startswith("permalink")
                    ]
                    if lines:
                        json_response["notable_features"] = lines

            cat_match = re.search(
                r"Categories\n(?P<section>.+?)(?:\n(?:Keywords|Download|Description|Notable Features|Contacts|Related Datasets|Search|Science On a Sphere))",
                preprocessed,
                re.S,
            )
            if cat_match:
                lines = [l.strip() for l in cat_match.group("section").split("\n") if l.strip()]
                categories: Dict[str, list[str]] = {}
                current = None
                for line in lines:
                    if line.endswith(":"):
                        current = line.rstrip(":")
                        categories[current] = []
                    elif current:
                        categories[current].append(line)
                if categories and categories != json_response.get("categories"):
                    json_response["categories"] = categories

            kw_match = re.search(
                r"Keywords\n(?P<section>.+?)(?:\n(?:Download|Description|Notable Features|Contacts|Related Datasets|Search|Science On a Sphere))",
                preprocessed,
                re.S,
            )
            if kw_match:
                keywords = [l.strip() for l in kw_match.group("section").split("\n") if l.strip()]
                if keywords and keywords != json_response.get("keywords"):
                    json_response["keywords"] = keywords

            date_match = re.search(r"Added to the Catalog\n([^\n]+)", preprocessed)
            if date_match:
                found_date = date_match.group(1).strip()
                if json_response.get("date_added") != found_date:
                    json_response["date_added"] = found_date

            avail_match = re.search(
                r"Available for\n(?P<section>.+?)(?:\n(?:Categories|Keywords|Download|Description|Notable Features|Contacts|Related Datasets|Search|Science On a Sphere))",
                preprocessed,
                re.S,
            )
            if avail_match:
                items = [l.strip() for l in avail_match.group("section").split("\n") if l.strip()]
                if items:
                    json_response["available_for"] = items

            for section, key in [
                ("Dataset Developer", "dataset_developer"),
                ("Dataset Vis Developer", "vis_developer"),
            ]:
                dev_match = re.search(
                    section + r"\n(?:[^\n]*\n)?([^\n]+?) \([^\n]+\)\n([^\n]+)",
                    preprocessed,
                    re.S,
                )
                if dev_match:
                    info = json_response.get(key, {})
                    info.setdefault("affiliation", dev_match.group(1).strip())
                    info.setdefault("name", dev_match.group(2).strip())
                    json_response[key] = info

            rel_match = re.search(
                r"Related Datasets\n(?P<section>.+?)(?:\n(?:Search|Science On a Sphere))",
                preprocessed,
                re.S,
            )
            if rel_match:
                lines = [l.strip() for l in rel_match.group("section").split("\n") if l.strip()]
                rel = []
                for line in lines:
                    if line.lower().startswith("permalink") or line[0].isdigit() or line.lower().startswith(("variations", "added on")):
                        continue
                    m = re.match(r"(.+?) \((https?://[^\s)]+)\)", line)
                    if m:
                        rel.append({"title": m.group(1).strip(), "url": m.group(2)})
                if rel:
                    json_response["related_datasets"] = rel

            desc_match = re.search(
                r"Description\n(?:Permalink[^\n]*\n)?(?P<section>.+?)(?:\n(?:Notable Features|Contacts|Related Datasets|Search|Science On a Sphere))",
                preprocessed,
                re.S,
            )
            if desc_match:
                desc = desc_match.group("section").strip()
                if desc and desc != json_response.get("description"):
                    json_response["description"] = desc

        return json_response
