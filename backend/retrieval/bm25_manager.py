from rank_bm25 import BM25Okapi
import re


class BM25Manager:

    def __init__(self):
        self.bm25 = None
        self.corpus_chunks = []

    def build_index(
        self,
        chunks
    ):
        self.corpus_chunks = chunks

        tokenized_corpus = [
            self._tokenize(chunk["text"])
            for chunk in chunks
        ]

        self.bm25 = BM25Okapi(tokenized_corpus)

    def _tokenize(
        self,
        text
    ):
        return re.findall(r"\w+", text.lower())

    def search(
        self,
        query,
        top_k=20
    ):
        if self.bm25 is None or not self.corpus_chunks:
            return []

        tokenized_query = self._tokenize(query)

        scores = self.bm25.get_scores(tokenized_query)

        scored_chunks = [
            {
                **self.corpus_chunks[i],
                "score": float(scores[i])
            }
            for i in range(len(self.corpus_chunks))
        ]

        scored_chunks.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        return scored_chunks[:top_k]