import uuid
import re
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils.chunk_filter import ChunkFilter
from dataclasses import dataclass


@dataclass
class DocumentChunk:

    chunk_id: str

    text: str

    title: str

    parent_text :str

    source_url: str

    url_hash: str

    chunk_index: int


class SemanticChunker:

    def __init__(self):
        # 1. Parent Splitter: Creates large chunks to hold full lists/sections
        #    We use a larger size (1500) and overlap to ensure we don't cut lists in half.
        self.parent_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1700,
            chunk_overlap=200,
            separators=[ "\n## ","\n### ","\n#### ","\n\n", "\n", ". ", " ", ""]
        )

        # 2. Child Splitter: Creates small chunks for precise vector search
        self.child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=700,
            chunk_overlap=70,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    #preserve lists
    def preserve_lists(self, text):

        text = re.sub(
            r"\n\s*[-*]\s+",
            "\n• ",
            text
        )

        text = re.sub(
            r"\n\s*\d+\.\s+",
            lambda m: "\n§" + m.group(0).strip(),
            text
        )

        return text
    #for codes
    def extract_code_blocks(self, text):

        pattern = r"```.*?```"

        code_blocks = re.findall(
            pattern,
            text,
            flags=re.DOTALL
        )

        placeholders = {}

        for idx, block in enumerate(code_blocks):

            token = f"CODE_BLOCK_{idx}"

            placeholders[token] = block

            text = text.replace(
                block,
                token
            )

        return text, placeholders
    
    def restore_code_blocks(
        self,
        text: str,
        placeholders
    ):

        for token, block in (
            placeholders.items()
        ):

            text = text.replace(
                token,
                block
            )

        return text

    def normalize_text(
        self,
        text: str
    ):

        text = text.replace(
            "\r",
            "\n"
        )

        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text
        )

        text = re.sub(
            r"[ \t]+",
            " ",
            text
        )

        return text.strip()
    
    def protect_code_blocks(
        self,
        text: str
    ):

        placeholders = {}

        pattern = r"```.*?```"

        code_blocks = re.findall(
            pattern,
            text,
            flags=re.DOTALL
        )

        for idx, block in enumerate(
            code_blocks
        ):

            token = (
                f"CODE_BLOCK_{idx}"
            )

            placeholders[token] = block

            text = text.replace(
                block,
                token
            )

        return (
            text,
            placeholders
        )


    def chunk_document(
        self,
        text: str,
        title: str,
        source_url: str,
        url_hash: str
    ):

        if not text:
            return []

        text = self.normalize_text(text)

        text = self.preserve_lists(text)

        (
            text,
            code_placeholders
        ) = self.protect_code_blocks(
            text
        )

        parent_chunks = (
            self.parent_splitter
            .split_text(text)
        )

        chunks = []

        chunk_index = 0

        for parent_text in parent_chunks:

            parent_text = (
                parent_text.strip()
            )

            if len(parent_text) < 100:
                continue

            parent_text = (
                self.restore_code_blocks(
                    parent_text,
                    code_placeholders
                )
            )

            child_chunks = (
                self.child_splitter
                .split_text(parent_text)
            )

            for child_text in child_chunks:

                child_text = (
                    child_text.strip()
                )

                child_text = (
                    self.restore_code_blocks(
                        child_text,
                        code_placeholders
                    )
                )

                if (
                    ChunkFilter
                    .is_low_quality(
                        child_text
                    )
                ):
                    continue

                chunk = DocumentChunk(

                    chunk_id=str(
                        uuid.uuid4()
                    ),

                    text=child_text,

                    parent_text=parent_text,

                    title=title,

                    source_url=source_url,

                    url_hash=url_hash,

                    chunk_index=chunk_index
                )

                chunks.append(
                    chunk
                )

                chunk_index += 1

        return chunks