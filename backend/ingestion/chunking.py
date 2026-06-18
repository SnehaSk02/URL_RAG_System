import uuid

from langchain_text_splitters import RecursiveCharacterTextSplitter

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
            chunk_size=1500,
            chunk_overlap=100,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        # 2. Child Splitter: Creates small chunks for precise vector search
        self.child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", ". ", " ", ""]
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

        # Step A: Split document into large "Parent" chunks
        parent_chunks = self.parent_splitter.split_text(text)

        chunks = []

        # Step B: Split each "Parent" into smaller "Child" chunks
        for parent_idx, parent_text in enumerate(parent_chunks):
            
            # Clean the parent text slightly (optional)
            parent_text = parent_text.strip()
            
            # Skip if too short
            if len(parent_text) < 50:
                continue

            # Split parent into children
            child_chunks = self.child_splitter.split_text(parent_text)

            for child_idx, child_text in enumerate(child_chunks):
                
                child_text = child_text.strip()

                # Skip tiny fragments
                if len(child_text) < 20:
                    continue

                # Create the chunk object
                # Crucial: We store 'parent_text' so the LLM gets the full list!
                chunk = DocumentChunk(
                    chunk_id=str(uuid.uuid4()),
                    text=child_text,         # Used for Embedding/Search
                    parent_text=parent_text, # Used for LLM Context/Answer
                    title=title,
                    source_url=source_url,
                    url_hash=url_hash,
                    chunk_index=f"{parent_idx}_{child_idx}" # Composite index
                )

                chunks.append(chunk)

        return chunks