from backend.models.embedding_manager import (
    EmbeddingManager
)

from backend.vectorstore.qdrant_manager import (
    QdrantManager
)

from backend.retrieval.reranker import (
    Reranker
)
from backend.retrieval.bm25_manager import (
    BM25Manager
)


class Retriever:

    def __init__(self):

        self.model = (
            EmbeddingManager.get_model()
        )

        self.qdrant = (
            QdrantManager()
        )

        self.reranker = (
            Reranker()
        )

        self.bm25_manager = (
            BM25Manager()
        )


    def embed_query(
        self,
        query
    ):

        return self.model.encode(
            query,
            normalize_embeddings=True
        )
    
    def _fetch_all_chunks(
        self,
        url_hash=None
    ):
        """
        Fetch all chunks for the given url_hash
        from Qdrant to build the BM25 index.
        """

        results = self.qdrant.scroll_vectors(
            url_hash=url_hash
        )

        chunks = []

        for result in results:

            chunks.append({

                "score": 0.0,

                "text":
                    result.payload["text"],
                
                "parent_text":result.payload.get("parent_text"),

                "source_url":
                    result.payload[
                        "source_url"
                    ],

                "title":
                    result.payload[
                        "title"
                    ],

                "chunk_index":
                    result.payload.get(
                        "chunk_index"
                    ),

                "url_hash":
                    result.payload.get(
                        "url_hash"
                    )
            })

        return chunks

    def _reciprocal_rank_fusion(
        self,
        dense_chunks,
        bm25_chunks,
        k=60
    ):

        rrf_scores = {}

        for rank, chunk in enumerate(dense_chunks):

            key = (chunk["url_hash"],
                   chunk["chunk_index"])

            if key not in rrf_scores:
                rrf_scores[key] = {
                    "chunk": chunk,
                    "rrf_score": 0.0
                }

            rrf_scores[key]["rrf_score"] += (
                1.0 / (k + rank + 1)
            )

        for rank, chunk in enumerate(bm25_chunks):

            key = (chunk["url_hash"],
                   chunk["chunk_index"])

            if key not in rrf_scores:
                rrf_scores[key] = {
                    "chunk": chunk,
                    "rrf_score": 0.0
                }

            rrf_scores[key]["rrf_score"] += (
                1.0 / (k + rank + 1)
            )

        merged = sorted(
            rrf_scores.values(),
            key=lambda x: x["rrf_score"],
            reverse=True
        )

        fused_chunks = []

        for entry in merged:

            chunk = entry["chunk"]
            chunk["score"] = entry["rrf_score"]
            fused_chunks.append(chunk)

        return fused_chunks


    def retrieve(
        self,
        query,
        top_k=8,
        initial_k=100,
        url_hash=None
    ):

        query_embedding = (self.embed_query(query))

        dense_results = (
            self.qdrant.search_vectors(
                query_embedding=query_embedding,
                top_k=initial_k,
                url_hash=url_hash
            )
        )

        dense_chunks = []

        for result in dense_results:

            dense_chunks.append({

                "score":
                    float(result.score),

                "text": result.payload["text"],

                "parent_text":
                    result.payload.get(
                        "parent_text"
                    ),

                "source_url":
                    result.payload[
                        "source_url"
                    ],

                "title":
                    result.payload[
                        "title"
                    ],

                "chunk_index":
                    result.payload.get(
                        "chunk_index"
                    ),

                "url_hash":
                result.payload.get("url_hash")
            })
            # --- BM25 retrieval ---

        all_chunks = self._fetch_all_chunks(
            url_hash=url_hash
        )

        self.bm25_manager.build_index(all_chunks)

        bm25_chunks = self.bm25_manager.search(
            query=query,
            top_k=initial_k
        )

        # --- Reciprocal Rank Fusion ---

        fused_chunks = (
            self._reciprocal_rank_fusion(
                dense_chunks=dense_chunks,
                bm25_chunks=bm25_chunks
            )
        )
        reranked = (
            self.reranker.rerank(
                query=query,
                retrieved_chunks=fused_chunks,
                top_k=top_k
            )
        )

        for chunk in reranked:

            if chunk.get("parent_text"):

                chunk["text"] = (
                    chunk["parent_text"]
                )

        return reranked