# from dataclasses import dataclass
# from models.embedding_manager import EmbeddingManager
# @dataclass
# class Chunk:
#     chunk_id: str
#     text: str
#     source_url: str
#     title: str
#     chunk_index: int
#     url_hash: str

# import uuid
# import nltk
# from sentence_transformers import SentenceTransformer
# from sklearn.metrics.pairwise import cosine_similarity
# from langchain_text_splitters import RecursiveCharacterTextSplitter

# try:
#     nltk.data.find("tokenizers/punkt")
# except LookupError:
#     nltk.download("punkt")

# class SemanticChunker:

#     def __init__(
#         self,
#         similarity_threshold=0.75,
#         chunk_size=500,
#         chunk_overlap=50
#     ):

#         self.embedding_model = EmbeddingManager.get_model()

#         self.similarity_threshold = similarity_threshold

#         self.recursive_splitter = (
#             RecursiveCharacterTextSplitter(
#                 chunk_size=chunk_size,
#                 chunk_overlap=chunk_overlap
#             )
#         )
#     #sentence splitting
#     def split_sentences(
#         self,
#         text):
            
#             return nltk.sent_tokenize(text)
    
#     #embedding generation
#     def generate_embeddings(
#         self,
#         sentences):
#             return self.embedding_model.encode(
#             sentences,
#             normalize_embeddings=True,
#             batch_size=32,
#     show_progress_bar=False
#         )
#     #topic shift detection
#     def semantic_segments(
#         self,
#         sentences,
#         embeddings):

#             chunks = []

#             current_chunk = [sentences[0]]

#             for i in range(1, len(sentences)):

#                 similarity = cosine_similarity(
#                     [embeddings[i - 1]],
#                     [embeddings[i]]
#                 )[0][0]

#                 if similarity >= self.similarity_threshold:

#                     current_chunk.append(
#                         sentences[i]
#                     )

#                 else:

#                     chunks.append(
#                         " ".join(current_chunk)
#                     )

#                     current_chunk = [
#                         sentences[i]
#                     ]

#             if current_chunk:

#                 chunks.append(
#                     " ".join(current_chunk)
#                 )

#             return chunks
    
#     #size control layer
#     def enforce_size_limit(
#         self,
#         chunks):

#             final_chunks = []

#             for chunk in chunks:

#                 if len(chunk) > 1500:

#                     split_parts = (
#                         self.recursive_splitter
#                         .split_text(chunk)
#                     )

#                     final_chunks.extend(
#                         split_parts
#                     )

#                 else:

#                     final_chunks.append(
#                         chunk
#                     )

#             return final_chunks
    
#     #final
#     def chunk_document(
#         self,
#         text,
#         title,
#         source_url,
#         url_hash):

#             sentences = self.split_sentences(text)
#             if not sentences:
#                 return []
#             embeddings = self.generate_embeddings(
#                 sentences
#             )

#             semantic_chunks = (
#                 self.semantic_segments(
#                     sentences,
#                     embeddings
#                 )
#             )

#             final_text_chunks = (
#                 self.enforce_size_limit(
#                     semantic_chunks
#                 )
#             )

#             output = []

#             for idx, chunk_text in enumerate(final_text_chunks):

#                 output.append(
#                     Chunk(
#                         chunk_id=str(
#                             uuid.uuid4()
#                         ),
#                         text=chunk_text,
#                         source_url=source_url,
#                         title=title,
#                         chunk_index=idx,
#                         url_hash=url_hash
#                     )
#                 )

#             return output

import uuid

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)

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