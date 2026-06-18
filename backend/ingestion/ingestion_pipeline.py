import hashlib
from qdrant_client.models import Filter, FieldCondition, MatchValue

from backend.ingestion.URL_validation import URLValidator

from backend.ingestion.extractor import (HybridExtractor,ContentCleaner)

from backend.ingestion.chunking import SemanticChunker

from backend.models.embedder import Embedder

from backend.vectorstore.qdrant_manager import QdrantManager


class IngestionPipeline:

    def __init__(self,qdrant_client=None):

        self.validator = URLValidator()

        self.extractor = HybridExtractor()

        self.cleaner = ContentCleaner()

        self.chunker = SemanticChunker()

        self.embedder = Embedder()

        self.qdrant = qdrant_client if qdrant_client else QdrantManager()

    def generate_url_hash(
        self,
        url
    ):

        return hashlib.sha256(
            url.encode()
        ).hexdigest()
    
    def ingest_url(self,url):

        if not self.validator.is_valid_url(url):
            return {
                "status": "failed",
                "message": "Invalid URL"
            }

        if not self.validator.validate_scheme(url):
            return {
                "status": "failed",
                "message":
                    "Only HTTP/HTTPS allowed"
            }

        normalized_url = (self.validator.normalize_url(url))

        if not (
            self.validator
            .check_url_accessible(
                normalized_url
            )
        ):
            return {
                "status": "failed",
                "message":
                    "URL not accessible"
            }

        if not (
            self.validator
            .validate_content_type(
                normalized_url
            )
        ):
            return {
                "status": "failed",
                "message":
                    "Unsupported content type"
            }
        
        url_hash = self.generate_url_hash(normalized_url)

        if self.qdrant.url_hash_exists(
            url_hash
        ):
            return {
                "status": "skipped",
                "message": "URL already ingested"
            }
        #extract
        document_text = (
            self.extractor.extract(
                normalized_url
            )
        )


        cleaned_text = document_text

        chunks = (
            self.chunker.chunk_document(
                text=cleaned_text,
                title=normalized_url,
                source_url=normalized_url,
                url_hash=url_hash
            )
        )
        from backend.utils.chunk_filter import ChunkFilter

        chunks = [chunk for chunk in chunks if not ChunkFilter.is_low_quality(
        chunk.text)]

        # Reassign indices
        for idx, chunk in enumerate(chunks):
            chunk.chunk_index = idx

        if not chunks:
            return {
                "status": "failed",
                "message":
                    "Chunking failed"
            }

        embeddings = (
            self.embedder.embed_chunks(
                chunks
            )
        )

        self.qdrant.store_vectors(
            chunks,
            embeddings
        )

        return {

            "status":
                "success",

            "url":
                normalized_url,

            "url_hash":
                url_hash,

            "chunks_created":
                len(chunks),

            "embeddings_created":
                len(embeddings)
        }
    
