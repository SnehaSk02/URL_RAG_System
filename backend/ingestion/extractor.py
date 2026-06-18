# import trafilatura
# from playwright.sync_api import sync_playwright
# import re

# class PlaywrightRenderer:

#     def render(self, url: str) -> str:

#         with sync_playwright() as p:

#             browser = p.chromium.launch(
#                 headless=True
#             )

#             page = browser.new_page()

#             page.goto(
#                 url,
#                 wait_until="networkidle"
#             )

#             html = page.content()

#             browser.close()

#             return html

# # class ContentExtractor:

# #     def extract(self, url: str) -> str:

# #         downloaded = trafilatura.fetch_url(url)

# #         if downloaded:

# #             text = trafilatura.extract(downloaded)

# #             if text:
# #                 return text

# #         html = PlaywrightRenderer().render(url)

# #         text = trafilatura.extract(html)

# #         if not text:
# #             raise Exception(
# #                 "Extraction failed"
# #             )

# #         return text
    


# import requests
# import trafilatura
# from bs4 import BeautifulSoup, UnicodeDammit
# from ingestion.content_cleaner import ContentCleaner
# class HybridExtractor:

#     def __init__(self):

#         self.cleaner = ContentCleaner()

#         self.headers = {
#             "User-Agent": "Mozilla/5.0"
#         }

#     def fetch_html(
#     self,
#     url
# ):

#         response = requests.get(
#             url,
#             headers=self.headers,
#             timeout=15
#         )

#         response.raise_for_status()

#         response.encoding = (
#             response.apparent_encoding
#         )

#         return response.text

#     def extract_with_bs4(
#     self,
#     html: str
# ):

#         html = UnicodeDammit(
#             html
#         ).unicode_markup

#         soup = BeautifulSoup(
#             html,
#             "html.parser"
#         )

#         # Remove obvious noise
#         for tag in soup.select(
#             "script, style, nav, footer, header, aside"
#         ):
#             tag.decompose()

#         # Remove documentation sidebars
#         noise_classes = [
#             "sidebar",
#             "sphinxsidebar",
#             "related",
#             "toc",
#             "breadcrumb",
#             "wy-nav-side",
#             "wy-side-nav-search"
#         ]

#         for cls in noise_classes:

#             for tag in soup.find_all(
#                 class_=lambda x:
#                 x and cls.lower() in str(x).lower()
#             ):
#                 tag.decompose()

#         # Locate main content
#         content = (
#             soup.find("main")
#             or soup.find("article")
#             or soup.find(attrs={"role": "main"})
#             or soup.body
#             or soup
#         )

#         blocks = []

#         for element in content.find_all(
#             [
#                 "h1",
#                 "h2",
#                 "h3",
#                 "h4",
#                 "p",
#                 "li",
#                 "pre",
#                 "code"
#             ]
#         ):

#             text = element.get_text(
#                 separator="\n",
#                 strip=True
#             )

#             if not text:
#                 continue

#             if element.name.startswith("h"):

#                 blocks.append(
#                     {
#                         "type": "heading",
#                         "text": text
#                     }
#                 )

#             elif element.name in [
#                 "pre",
#                 "code"
#             ]:

#                 blocks.append(
#                     {
#                         "type": "code",
#                         "text": text
#                     }
#                 )

#             elif element.name == "li":

#                 blocks.append(
#                     {
#                         "type": "list_item",
#                         "text": text
#                     }
#                 )

#             else:

#                 blocks.append(
#                     {
#                         "type": "paragraph",
#                         "text": text
#                     }
#                 )

#         return blocks
    
#     def extract_with_trafilatura(
#         self,
#         url: str
#     ):

#         downloaded = trafilatura.fetch_url(
#             url
#         )

#         if not downloaded:
#             return []

#         text = trafilatura.extract(
#             downloaded
#         )

#         if not text:
#             return []

#         text = self.cleaner.clean(
#             text
#         )

#         return [
#             {
#                 "type": "text",
#                 "text": text
#             }
#         ]

# #     def extract(
# #         self,
# #         url: str
# #     ):

# #         try:

# #             html = self.fetch_html(
# #                 url
# #             )

# #             blocks = self.extract_with_bs4(
# #                 html
# #             )
# # #             return "\n\n".join(
# # #                      block["text"]
# # #                 for block in blocks
# # # )

# #             if len(blocks) < 5:

# #                 print(
# #                     "Using Trafilatura fallback..."
# #                 )

# #                 return (
# #                     self.extract_with_trafilatura(
# #                         url
# #                     )
# #                 )

# #             return blocks

# #         except Exception as e:

# #             print(
# #                 f"BS4 extraction failed: {e}"
# #             )

# #             return (
# #                 self.extract_with_trafilatura(
# #                     url
# #                 )
# #             )    

#     def extract(
#     self,
#     url
# ):

#         try:

#             html = self.fetch_html(url)

#             blocks = self.extract_with_bs4(
#                 html
#             )

#             if len(blocks) < 10:

#                 print(
#                     "Using Trafilatura fallback..."
#                 )

#                 blocks = (
#                     self.extract_with_trafilatura(
#                         url
#                     )
#                 )

#         except Exception as e:

#             print(
#                 f"Extraction failed: {e}"
#             )

#             blocks = (
#                 self.extract_with_trafilatura(
#                     url
#                 )
#             )

#         text = "\n\n".join(
#             block["text"]
#             for block in blocks
#         )

#         return text


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