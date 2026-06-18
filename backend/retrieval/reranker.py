from sentence_transformers import CrossEncoder


class Reranker:

    def __init__(self):

        self.model = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-6-v2"
        )

    def rerank(
        self,
        query,
        retrieved_chunks,
        top_k=5
    ):

        pairs = [

            (
                query,
                chunk["text"]
            )

            for chunk in retrieved_chunks
        ]

        scores = self.model.predict(
            pairs
        )

        for chunk, score in zip(
            retrieved_chunks,
            scores
        ):

            chunk["rerank_score"] = (float(score))

        retrieved_chunks.sort(
            key=lambda x:
            x["rerank_score"],
            reverse=True
        )

        return retrieved_chunks[:top_k]