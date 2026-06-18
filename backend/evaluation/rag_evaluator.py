import pandas as pd

from backend.evaluation.retrieval_metrics import (
    RetrievalMetrics
)


class RAGEvaluator:

    def evaluate(
        self,
        dataset
    ):

        results = []

        for sample in dataset:

            retrieved_ids = sample[
                "retrieved_ids"
            ]

            relevant_ids = sample[
                "relevant_ids"
            ]

            results.append({
            #How much relevant information did we find?
                "recall@5":
                RetrievalMetrics.recall_at_k(
                    retrieved_ids,
                    relevant_ids,
                    5
                ),
            #Did we find ANY useful chunk?
                "hitrate@5":
                RetrievalMetrics.hit_rate_at_k(
                    retrieved_ids,
                    relevant_ids,
                    5
                ),
            #MRR (Mean Reciprocal Rank) -Higher = better ranking
                "mrr":
                RetrievalMetrics.mrr(
                    retrieved_ids,
                    relevant_ids
                )
            })

        df = pd.DataFrame(results)

        return {

            "Recall@5":
            df["recall@5"].mean(),

            "HitRate@5":
            df["hitrate@5"].mean(),

            "MRR":
            df["mrr"].mean()
        }