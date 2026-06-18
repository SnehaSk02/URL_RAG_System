# URL RAG System
##Introduction
The URL-RAG system is a retrieval-augmented generation pipeline designed to answer queries grounded in the content of user-provided web URLs.

### 1. Data Ingestion Methodology
The system was designed to ingest knowledge directly from publicly accessible web URLs and transform the content into a searchable knowledge base for Retrieval-Augmented Generation (RAG).
The ingestion pipeline consists of the following stages:
#### 1. URL Validation
Validates URL format.
Restricts ingestion to HTTP/HTTPS schemes.
Checks URL accessibility.
Verifies supported content types before processing.
#### 2.Content Extraction
HTML pages are fetched using the Requests library.
Content is parsed using BeautifulSoup.
Important content elements such as headings, paragraphs, list items, and code blocks are extracted while preserving document structure.
Navigation menus, advertisements, scripts, styles, headers, footers, and other non-content elements are removed.
Trafilatura is used as a fallback extractor when BeautifulSoup extraction produces insufficient content.
#### 3.Content Cleaning
Removes common web-page noise such as:
Cookie banners
Breadcrumb navigation
Footer content
Social media links
Site navigation elements
Normalizes whitespace and formatting.
#### 4.Duplicate Detection
Each URL is normalized and converted into a SHA-256 hash.
Before ingestion, the system checks whether the URL hash already exists in the vector database.
Duplicate URLs are skipped to avoid redundant storage.
The final cleaned document is then passed to the chunking pipeline.
### 2. Chunking Strategy
Effective chunking is critical for retrieval quality.
Initially, sentence-based chunking produced many very small chunks and fragmented context. To improve retrieval quality, a semantic chunking strategy was adopted.
Chunking Approach
Split content into sentences.
Group semantically related sentences together.
Create chunks with a target size of approximately:
500–800 characters
15–25% overlap between adjacent chunks
Metadata Stored Per Chunk
Each chunk stores:
Chunk text
Source URL
URL hash
Chunk index
Document title
### 3. Embedding Model Selection
The system uses a Sentence Transformer embedding model to convert text chunks into dense vector representations.
Selected Model
Sentence Transformers based embedding model here "BAAI/bge-m3"
Selection Criteria
The model was selected because it:
Produces strong semantic representations
Supports retrieval tasks efficiently
Has low inference latency
Works well on technical and documentation-style content
Can be executed locally without external APIs
Embedding Workflow
For every chunk:
Chunk text is passed to the embedding model.
A dense vector representation is generated.
The vector and metadata are stored in the vector database.
User queries are embedded using the same model to ensure semantic alignment between stored chunks and search queries.
### 4. Vector Database Choice
The project uses Qdrant as the vector database.
Reasons for Choosing Qdrant
Open-source
Lightweight deployment
Fast vector similarity search
Rich metadata filtering
REST and Python SDK support
Suitable for production-scale RAG systems
Stored Payload
Each vector stores:
chunk_text
source_url
url_hash
chunk_index
title
This metadata enables filtering, citation generation, and future document management features.
### 5. Retrieval Pipeline (Hybrid Strategy)
To maximize retrieval accuracy, the system employs a Hybrid Search Strategy that combines dense vector embeddings (semantic search) with BM25 (lexical/keyword search). This ensures the system captures both the intent of the user's question and the specific terminology used in the documents.
The retrieval pipeline consists of the following stages:

Step 1: Dual Query Processing
The user's question is processed in parallel for both retrieval methods:
Dense: The query is converted into an embedding vector using the Sentence Transformer model.
Sparse: The raw query text is tokenized for BM25 keyword matching.

Step 2: Parallel Retrieval
The system performs two simultaneous searches:
Dense Retrieval: Qdrant performs a similarity search to find the top-K chunks that are semantically similar to the query embedding.
Keyword Retrieval: The BM25 index is queried to find the top-K chunks containing exact keywords or rare terms from the query.

Step 3: Result Fusion
The results from both the Dense and BM25 retrievers are merged into a single candidate list. Deduplication logic is applied to ensure that if the same chunk appears in both search results, it is not double-counted.

Step 4: Reranking
The merged list of candidate chunks is reranked using a Cross-Encoder model.
This step re-evaluates the relevance of the combined list, prioritizing chunks that directly answer the specific user question.
This fusion method ensures that contextually relevant (Dense) and factually specific (BM25) chunks are both considered for the final answer.

Step 5: Context Construction
The highest-ranked chunks from the reranking stage are combined to form the final retrieval context.

Step 6: Answer Generation
The retrieval context and user query are passed to the LLM for grounded answer generation.

### 6. Prompt Design
Prompt engineering was used to ensure grounded and accurate responses.
Prompt Structure
The LLM receives:
System instructions
Retrieved context
User question
Example structure:
System:
You are a helpful assistant. Answer only using the provided context.
Context:


Question:


Answer:
Design Goals
Reduce hallucinations
Encourage source-grounded answers
Improve factual accuracy
Prevent generation outside retrieved knowledge
The prompt explicitly instructs the model to prioritize retrieved context over prior knowledge.
### 7. Evaluation Results
Retrieval quality was evaluated using standard Information Retrieval metrics.
Metrics Used
Recall@K
Measures whether relevant chunks appear within the top-K retrieved results.
HitRate@K
Measures whether at least one relevant chunk is retrieved.
Mean Reciprocal Rank (MRR)
Measures how early the first relevant result appears.
Sample Evaluation Results
Initial Evaluation:
Recall@5 = 1.00
HitRate@5 = 1.00
MRR = 1.00
Extended Evaluation:
Recall@5 = 0.33
HitRate@5 = 0.33
MRR = 0.125
Analysis
The first evaluation used direct questions whose answers were clearly represented within the dataset and retrieval pipeline.
The second evaluation introduced more challenging semantic questions requiring deeper contextual understanding. Results revealed opportunities for improving chunk quality, retrieval ranking, and query understanding.

### 8. Limitations and Future Work
Current Limitation
No user authentication.
Limited citation support.
Retrieval quality depends heavily on chunk quality.
No conversational memory.
Future Enhancements
Chat History
Maintain conversational context across multiple user queries.
User Authentication
Implement login and user-specific document collections.
Dashboard
Provide a frontend interface for:
URL ingestion
Querying
Source inspection
Retrieval analytics
### 9. Installation and Execution Guide
To run the URL-RAG system locally, the application is divided into two distinct services: the Backend API (handling processing and retrieval) and the Frontend Interface (handling user interaction).
Prerequisites
-Python 3.11.9 or higher
-pip (Python package installer)
Step 1: Environment Setup
It is recommended to create a virtual environment to isolate dependencies:

->python -m venv venv
# Windows
venv\Scripts\activate  

pip install -r requirements.txt  

Step 2: Backend Installation and Execution  

Navigate to the backend directory:
->cd backend

Start the API Server:  

Launch the FastAPI server using Uvicorn. The --reload flag enables auto-reloading during development:
bash  

->uvicorn api.main:app --reload  

The backend will be available at http://127.0.0.1:8000.  

Step 3: Frontend Installation and Execution
Note: Open a new terminal window to run the frontend while keeping the backend server running.
Navigate to the frontend directory:  

->cd frontend  

Launch the Streamlit Application:
->streamlit run app.py  

The browser will automatically open the interface at http://localhost:8501.
Accessing the System
Once both services are running, users can interact with the system via the Streamlit frontend at http://localhost:8501. The frontend will communicate with the backend API to ingest URLs and answer queries.

## Deployment
The URL-based RAG system was deployed using a cloud-native architecture that separates the frontend and backend services for scalability and ease of maintenance.
Backend Deployment-The backend was developed using FastAPI and deployed on Hugging Face Spaces (Docker/SDK environment).
Frontend Deployment-The user interface was built using Streamlit.

## Conclusion
The developed URL-based RAG system successfully demonstrates the complete Retrieval-Augmented Generation workflow, including web content ingestion, semantic chunking, embedding generation, vector storage, retrieval, reranking, and answer generation. The system provides a strong foundation for building production-grade knowledge assistants while remaining modular and extensible for future enhancements.



 
