import re
import requests
from bs4 import BeautifulSoup, Comment
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from urllib.parse import urljoin


class Preprocessor(ABC):
    """
    Abstract base class for preprocessors.
    Defines the interface for transforming raw inputs into structured data.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the preprocessor with optional configuration.

        Args:
            config: A dictionary of configuration settings.
                - keep_tags (bool): If True, keeps HTML tags in the output.
                - remove_boilerplate (bool): If True, strips header, footer and
                  navigation sections as well as official government banners
                  from the HTML before extracting text.
        """
        defaults = {
            "keep_tags": False,
            "remove_boilerplate": True,
        }
        self.config = {**defaults, **(config or {})}

    def _fetch_content(self, url: str) -> str:
        """
        Fetches and parses the text content from a URL.

        Args:
            url: The URL to fetch content from.

        Returns:
            The clean, extracted text content from the page.

        Raises:
            ValueError: If the URL cannot be fetched or processed.
        """
        try:
            # Set a User-Agent header to mimic a browser, which can help avoid
            # being blocked by some websites.
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.6",
                "Cache-Control": "max-age=0",
                "Sec-Ch-Ua": "\"Not(A:Brand\";v=\"99\", \"Brave\";v=\"133\", \"Chromium\";v=\"133\"",
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": "\"Windows\"",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
            }
            
            # Make the HTTP GET request with a timeout.
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()

            # Use the apparent encoding when the server does not specify a
            # charset to avoid garbled characters in the text.
            if response.encoding in (None, "ISO-8859-1"):
                response.encoding = response.apparent_encoding

            return response.text
            
        except requests.exceptions.RequestException as e:
            # Catch any network-related errors (DNS, connection, timeout, etc.)
            # and re-raise them as a more user-friendly ValueError.
            raise ValueError(f"Failed to fetch content from URL: {url}. Error: {e}")
        

    @abstractmethod
    def preprocess(self, content: str, is_url: bool) -> str:
        """
        Take raw content (HTML, text, etc.) and apply preprocessing steps.

        Args:
            content: The raw data to preprocess.

        Returns:
            The cleaned text content. If ``is_url`` is True, the returned
            string is prefixed with ``"Source URL: <url>"`` and all relative
            links have been expanded to absolute URLs.
        """
        pass

class BasicPreprocessor(Preprocessor):
    """Base preprocessor with common functionality."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self.last_html: Optional[str] = None

    def _clean_html(self, html_content: str, base_url: Optional[str] = None) -> str:
        """
        Cleans up the given HTML content by:
        - Removing <script> and <style> tags and their content.
        - Removing HTML comments.
        - Optionally removing page boilerplate like headers, navigation bars and
          official U.S. government banners.
        - Extracting and returning the visible text with normalized whitespace if ``keep_tags`` is False.
        - Expanding relative links to absolute URLs when ``base_url`` is provided.
        
        Args:
            html_content (str): The HTML content to clean.
        
        Returns:
            str: The cleaned, visible text from the HTML.
        """
        # Parse the HTML content
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Remove script and style elements
        for tag in soup(["script", "style"]):
            tag.decompose()

        # Optionally remove page boilerplate like headers and nav sections
        if self.config.get("remove_boilerplate", True):
            for tag in soup.find_all("header"):
                classes = tag.get("class", [])
                if "sos-dataset__header" in classes:
                    continue
                tag.decompose()

            # Remove sections that contain the US government banner
            for section in soup.find_all(
                "section",
                attrs={
                    "aria-label": re.compile(
                        r"Official website of the United States government",
                        re.I,
                    )
                },
            ):
                section.decompose()

            # Remove navigation bars
            for nav in soup.find_all("nav"):
                nav.decompose()
        
        # Remove HTML comments
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()
        
        # If keep_tags is True, return the raw HTML
        if self.config.get("keep_tags", False):
            return str(soup)

        # Preserve anchor href values by replacing each <a> tag with
        # "link text (href)" so that URLs are available to the LLM.
        for a_tag in soup.find_all("a", href=True):
            link_text = a_tag.get_text(" ", strip=True)
            href = a_tag["href"]
            if base_url:
                href = urljoin(base_url, href)
            a_tag.replace_with(f"{link_text} ({href})")

        text = soup.get_text(separator="\n", strip=True)
        text = re.sub(r"[ \t\r\f\v]+", " ", text)
        clean_text = re.sub(r"\n+", "\n", text)

        self.last_html = str(soup)
        return clean_text

    def preprocess(self, content: str, is_url: bool) -> str:
        """
        Take raw content (HTML, text, etc.) and apply preprocessing steps.

        Args:
            content: The raw data to preprocess.

        Returns:
            The cleaned text content. If ``is_url`` is True, the text is
            prefixed with ``"Source URL: <url>"`` and all relative links are
            expanded to absolute URLs.
        """
        
        html_content = content
        source_url = None
        if is_url:
            # Fetch content from the URL
            source_url = content
            html_content = self._fetch_content(content)

        # Clean the HTML content
        cleaned_content = self._clean_html(html_content, base_url=source_url)

        if source_url:
            cleaned_content = f"Source URL: {source_url}\n" + cleaned_content

        return cleaned_content.strip()  # Return the cleaned text content, stripped of leading/trailing whitespace
