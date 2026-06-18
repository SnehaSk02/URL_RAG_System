from sentence_transformers import SentenceTransformer
_model_instance = None
class EmbeddingManager:
    MODEL_NAME = (
        "BAAI/bge-m3"  
    )

    @classmethod
    def get_model(cls):
        global _model_instance

        if _model_instance is None:

            _model_instance = (SentenceTransformer(cls.MODEL_NAME))

        return _model_instance