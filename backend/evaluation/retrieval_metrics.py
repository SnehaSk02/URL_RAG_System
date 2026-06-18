class RetrievalMetrics:
    @staticmethod
    def recall_at_k(retrieved_ids,relevant_ids,k):
        retrieved_k=set(retrieved_ids[:k])
        relevant=set(relevant_ids)
        hits=len(retrieved_k.intersection(relevant))
        if len(relevant) == 0:
            return 0
        return hits/len(relevant)

    @staticmethod
    def hit_rate_at_k(retrieved_ids,relevant_ids,k):
        retrieved_k=set(retrieved_ids[:k])
        relevant=set(relevant_ids)
        return int(len(retrieved_k.intersection(relevant))>0)
    
    @staticmethod
    def mrr(retrieved_ids,relevant_ids):
        for rank,doc_id in enumerate(retrieved_ids,start=1):
            if doc_id in relevant_ids:
                return 1/rank
        return 0