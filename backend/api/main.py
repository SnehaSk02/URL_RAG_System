import sys
import os

# Get the absolute path to the project root directory (RAG_Proj)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

# Add it to Python's system path
sys.path.append(project_root)
import uvicorn
from fastapi import FastAPI, HTTPException
from typing import Optional

from pydantic import BaseModel

from backend.rag.rag_pipeline import (
    RAGPipeline
)
from backend.vectorstore.qdrant_manager import QdrantManager
from backend.ingestion.ingestion_pipeline import (
    IngestionPipeline
)

app = FastAPI()

qdrant_manager= QdrantManager()

rag = RAGPipeline(qdrant_client=qdrant_manager)

ingestion = IngestionPipeline(qdrant_client=qdrant_manager)



class URLRequest(
    BaseModel
):
    url: str

class QueryRequest(
    BaseModel
):
    query: str
    url_hash: Optional[str] = None

class DeleteUrlModel(BaseModel):
    source_url: str

@app.get("/")
def home():
    return {"status": "Backend is running!"}

@app.post("/predict")
def predict(data: dict):
    # Your AI model logic goes here
    user_text = data.get("text", "")
    return {"prediction": f"Backend received: {user_text}"}

@app.post("/ingest")
def ingest_url(
    request: URLRequest
):

    result = (
        ingestion.ingest_url(
            request.url
        )
    )

    return result

@app.post("/ask")
def ask_question(
    request: QueryRequest
):

    return rag.ask(
        request.query,
        url_hash=request.url_hash

    )

@app.get("/urls")
def get_list_urls():
    """
    Endpoint to list all ingested URLs and their stats.
    Maps to: qdrant_manager.list_urls()
    """
    try:
        return qdrant_manager.list_urls()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/url")
def delete_url_endpoint(data: DeleteUrlModel):
    """
    Endpoint to delete a specific URL.
    Maps to: qdrant_manager.delete_url(source_url=...)
    """
    try:
        qdrant_manager.delete_url(source_url=data.source_url)
        return {"status": "success", "message": f"Deleted {data.source_url}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
def get_collection_stats():
    """
    Endpoint to get collection info.
    Maps to: qdrant_manager.collection_info()
    """
    try:
        info = qdrant_manager.collection_info()
        return {
            "points_count": info.points_count,
            "status": info.status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
if __name__ == "__main__":
    # Hugging Face strictly requires port 7860 and host 0.0.0.0
    uvicorn.run(app, host="0.0.0.0", port=7860)