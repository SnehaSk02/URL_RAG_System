import json
from datetime import datetime
from backend.retrieval.retriever import Retriever
from backend.logs.query_logger import QueryLogger

from backend.generation.prompt_builder import PromptBuilder

from backend.generation.llm_service import LLMService
class RAGPipeline:

    def __init__(self):

        self.retriever = Retriever()

        self.llm = LLMService()

        self.logger=QueryLogger()

    

    def ask(self,query,url_hash=None):
            chunks = (self.retriever.retrieve(
                query=query,
                top_k=5,
                url_hash=url_hash
            )
        )
            prompt = (
            PromptBuilder.build_prompt(
                query=query,
                retrieved_chunks=chunks
            )
        )
            answer = (
            self.llm.generate_answer(
                prompt
            )
        )
            self.logger.log_query(
                query=query,
                answer=answer,
                url_hash=url_hash,
                retrieved_chunks=chunks
            )
            sources = []

            for chunk in chunks:

                sources.append(
                {

                    "chunk_index":
                        chunk["chunk_index"],

                    "source_url":
                        chunk["source_url"],

                    "vector_score":
                        round(chunk["score"],4),

                    "rerank_score":
                        round(chunk["rerank_score"],4),

                    "text":
                        chunk["text"]
                }
                )

            return {
                    "answer": answer,
                    "citations": [

                                    {
                                        "chunk_index":
                                            c["chunk_index"],

                                        "source_url":
                                            c["source_url"]
                                    }

                                    for c in chunks
                                ],
                     "sources": sources
                }