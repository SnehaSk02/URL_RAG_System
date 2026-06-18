import json
import os
from datetime import datetime


class QueryLogger:

    def __init__(
        self,
        log_file="logs/query_logs.jsonl"
    ):

        self.log_file = log_file

        os.makedirs(
            os.path.dirname(log_file),
            exist_ok=True
        )

    def log_query(
        self,
        query,
        answer,
        url_hash,
        retrieved_chunks
    ):

        log_entry = {

            "timestamp":
                datetime.now().isoformat(),

            "query":
                query,

            "answer":
                answer,

            "url_hash":
                url_hash,

            "retrieved_chunks": [

                {

                    "chunk_index":
                        chunk.get(
                            "chunk_index"
                        ),

                    "source_url":
                        chunk.get(
                            "source_url"
                        ),

                    "vector_score":
                        float(
                            chunk.get(
                                "score",
                                0
                            )
                        ),

                    "rerank_score":
                        float(
                            chunk.get(
                                "rerank_score",
                                0
                            )
                        )

                }

                for chunk in retrieved_chunks
            ]
        }

        with open(
            self.log_file,
            "a",
            encoding="utf-8"
        ) as f:

            f.write(
                json.dumps(
                    log_entry,
                    ensure_ascii=False
                )
                + "\n"
            )