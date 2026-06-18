import requests

import trafilatura

from bs4 import BeautifulSoup

from backend.ingestion.content_cleaner import ContentCleaner

class HybridExtractor:

    def __init__(self):

        self.cleaner = ContentCleaner()

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0"
            )
        }
    def fetch_html(self, url):

        response = requests.get(
            url,
            headers=self.headers,
            timeout=20
        )

        response.raise_for_status()

        return response.text
    def find_main_content(self, soup):

        candidates = [

            "article",

            "main",

            '[role="main"]',

            ".content",

            ".post-content",

            ".article-content",

            ".entry-content",

            ".documentation",

            ".markdown-body"
        ]

        for selector in candidates:

            content = soup.select_one(
                selector
            )

            if content:
                return content

        return soup.body

    def extract_with_bs4(
        self,
        html
    ):

        soup = BeautifulSoup(
            html,
            "html.parser"
        )
        for tag in soup.select(
            ".sidebar,"
            ".menu,"
            ".toc,"
            ".navigation,"
            ".breadcrumb,"
            ".related-posts,"
            ".advertisement,"
            ".ads"
        ):
            tag.decompose()

        for tag in soup([
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "aside",
            "noscript"
        ]):
            tag.decompose()

        content = self.find_main_content(
            soup
        )

        if not content:
            return ""

        blocks = []

        allowed_tags = [

            "h1",
            "h2",
            "h3",
            "h4",

            "p",

            "pre",

            "code",

            "li"
        ]

        for tag in content.find_all(
            allowed_tags
        ):

            text = tag.get_text(
                separator=" ",
                strip=True
            )

            if not text:
                continue

            blocks.append(text)

        return "\n\n".join(blocks)

    def extract_with_trafilatura(
        self,
        url
    ):

        downloaded = (
            trafilatura.fetch_url(url)
        )

        if not downloaded:
            return ""

        text = trafilatura.extract(
            downloaded
        )

        return text or ""
    
    def extract(
        self,
        url
    ):

        try:

            html = self.fetch_html(
                url
            )

            text = self.extract_with_bs4(
                html
            )

            if len(text) < 1000:

                print(
                    "Using Trafilatura fallback..."
                )

                text = (
                    self.extract_with_trafilatura(
                        url
                    )
                )

        except Exception as e:

            print(
                f"BS4 failed: {e}"
            )

            text = (
                self.extract_with_trafilatura(
                    url
                )
            )

        text = self.cleaner.clean(
            text
        )

        return text