from backend.models.embedding_manager import EmbeddingManager

class Embedder:

    def __init__(self):

        self.model = (EmbeddingManager.get_model())

    def embed_chunks(self,chunks):

        texts = [
            chunk.text for chunk in chunks]

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            batch_size=32,
            show_progress_bar=True
        )

        return embeddings