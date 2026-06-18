import json

from backend.retrieval.retriever import Retriever

from backend.evaluation.retrieval_metrics import (
    RetrievalMetrics
)


class RetrievalEvaluator:

    def __init__(self):

        self.retriever = Retriever()

    def evaluate(
        self,
        dataset_path,
        url_hash=None
    ):

        with open(
            dataset_path,
            "r",
            encoding="utf-8"
        ) as f:

            dataset = json.load(f)

        recall_scores = []

        hit_scores = []

        mrr_scores = []

        print(
            "\nRunning Evaluation...\n"
        )

        for sample in dataset:

            question = sample[
                "question"
            ]

            relevant_ids = sample[
                "relevant_chunk_indices"
            ]

            results = (
                self.retriever.retrieve(
                    query=question,
                    top_k=5,
                    url_hash=url_hash
                )
            )

            retrieved_ids = [

                result[
                    "chunk_index"
                ]

                for result in results
            ]

            recall = (
                RetrievalMetrics
                .recall_at_k(
                    retrieved_ids,
                    relevant_ids,
                    k=5
                )
            )

            hit_rate = (
                RetrievalMetrics
                .hit_rate_at_k(
                    retrieved_ids,
                    relevant_ids,
                    k=5
                )
            )

            rr = (
                RetrievalMetrics
                .mrr(
                    retrieved_ids,
                    relevant_ids
                )
            )

            recall_scores.append(
                recall
            )

            hit_scores.append(
                hit_rate
            )

            mrr_scores.append(
                rr
            )

            print(
                f"Question: {question}"
            )

            print(
                f"Retrieved: {retrieved_ids}"
            )

            print(
                f"Expected: {relevant_ids}"
            )

            print(
                f"Recall@5: {recall:.2f}"
            )

            print(
                f"HitRate@5: {hit_rate}"
            )

            print(
                f"RR: {rr:.2f}"
            )

            print(
                "-" * 50
            )

        avg_recall = (
            sum(recall_scores)
            /
            len(recall_scores)
        )

        avg_hitrate = (
            sum(hit_scores)
            /
            len(hit_scores)
        )

        avg_mrr = (
            sum(mrr_scores)
            /
            len(mrr_scores)
        )

        print("\nFINAL RESULTS")

        print(
            f"Average Recall@5: "
            f"{avg_recall:.4f}"
        )

        print(
            f"Average HitRate@5: "
            f"{avg_hitrate:.4f}"
        )

        print(
            f"Average MRR: "
            f"{avg_mrr:.4f}"
        )

        return {

            "Recall@5":
                avg_recall,

            "HitRate@5":
                avg_hitrate,

            "MRR":
                avg_mrr
        }