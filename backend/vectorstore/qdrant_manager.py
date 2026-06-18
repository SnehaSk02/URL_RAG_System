import os
from dotenv import load_dotenv

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue

load_dotenv()

class QdrantManager:
    def __init__(self):
        self.collection_name = os.getenv(
            "QDRANT_COLLECTION",
            "url_rag"
        )

        self.client=QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key= os.getenv("QDRANT_API_KEY"))
        self.validate_connection()

        self.create_collection()
    #Validating connection
    def validate_connection(self):
        try:
            collections=self.client.get_collections()
            print("Qdrant connection successful.")
            return True
        
        except Exception as e:
            print(f"Qdrant connection failed:{e}")
            return False
        
    #creating collections
    def create_payload_indexes(self):

        try:

            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="url_hash",
                field_schema="keyword"
            )

        except Exception:
            pass

        try:

            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="source_url",
                field_schema="keyword"
            )

        except Exception:
            pass
    def create_collection(self):

        collections = self.client.get_collections()

        existing = [
            collection.name
            for collection in collections.collections
        ]

        if self.collection_name not in existing:
            self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=1024,
                distance=Distance.COSINE
            )
         )

            print(
                f"Collection '{self.collection_name}' created"

            )
        else:

            print(
            f"Using existing collection: "
            f"{self.collection_name}"
        )

    # Always ensure indexes exist
        self.create_payload_indexes()


    def store_vectors(self,chunks,embeddings):
        points=[]
        for chunk,vector in zip(chunks,embeddings):
            point=PointStruct(
                id=str(chunk.chunk_id),
                vector=vector.tolist(),
                payload={
                    "chunk_id":chunk.chunk_id,
                    "title":chunk.title,
                    "source_url":chunk.source_url,
                    "text":chunk.text,
                    "url_hash": chunk.url_hash,
                    "chunk_index": chunk.chunk_index,
                    "parent_text": chunk.parent_text
                }
            )
            points.append(point)
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        print(f"{len(points)} vectors stored")

        #Semantic search
    def search_vectors(
        self,
        query_embedding,
        top_k=20,
        url_hash=None
    ):
        search_filter=None
        if url_hash:
            search_filter=Filter(must=[
                FieldCondition(
                    key="url_hash",
                    match=MatchValue(value=url_hash)
                )
            ])


        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding.tolist(),
            query_filter=search_filter,
            limit=top_k
        )

        return results.points



    # --------------------------------------------------
    # Check URL Exists
    # --------------------------------------------------

    def url_exists(
        self,
        source_url
    ):

        results, _ = self.client.scroll(
            collection_name=self.collection_name,

            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="source_url",
                        match=MatchValue(
                            value=source_url
                        )
                    )
                ]
            ),

            limit=1
        )

        return len(results) > 0

    # --------------------------------------------------
    # Delete URL
    # --------------------------------------------------

    def delete_url(
        self,
        source_url
    ):

        self.client.delete(
            collection_name=self.collection_name,

            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="source_url",
                        match=MatchValue(
                            value=source_url
                        )
                    )
                ]
            )
        )

        print(
            f"Deleted chunks for {source_url}"
        )

    # --------------------------------------------------
    # Collection Stats
    # --------------------------------------------------

    def collection_info(self):

        info = (
            self.client.get_collection(
                self.collection_name
            )
        )

        return info

    def url_hash_exists(
    self,
    url_hash):

        results, _ = self.client.scroll(
            collection_name=self.collection_name,

            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="url_hash",
                        match=MatchValue(
                            value=url_hash
                        )
                    )
                ]
            ),

            limit=1
        )

        return len(results) > 0

    #url_lists
    def list_urls(self):

        results, _ = self.client.scroll(
            collection_name=self.collection_name,
            limit=10000,
            with_payload=True
    )

        urls = {}

        for point in results:

            url = point.payload["source_url"]

            if url not in urls:

                urls[url] = {
                    "url_hash":
                        point.payload["url_hash"],
                    "chunks": 0
                }

            urls[url]["chunks"] += 1

        return urls

    def scroll_vectors(
    self,
    url_hash=None,
    batch_size=100
):
        """
        Scroll through all points in the collection,
        optionally filtered by url_hash.
        """

        scroll_filter = None

        if url_hash:

            from qdrant_client.models import (
                Filter, FieldCondition, MatchValue
            )

            scroll_filter = Filter(
                must=[
                    FieldCondition(
                        key="url_hash",
                        match=MatchValue(value=url_hash)
                    )
                ]
            )

        all_results = []
        next_offset = None

        while True:

            results, next_offset = (
                self.client.scroll(
                    collection_name=self.collection_name,
                    scroll_filter=scroll_filter,
                    limit=batch_size,
                    offset=next_offset,
                    with_payload=True,
                    with_vectors=False
                )
            )

            all_results.extend(results)

            if next_offset is None:
                break

        return all_results