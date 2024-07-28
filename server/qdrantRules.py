import numpy as np
from qdrant_client.models import PointStruct
from qdrant_client import models, QdrantClient
import uuid
import os
from sentence_transformers import SentenceTransformer
encoder = SentenceTransformer("all-MiniLM-L6-v2")

def insert_rule(payload, collection_name=os.environ["QDRANT_COLLECTION"]):
    # vector = np.random.rand(20)
    # # Initialize Qdrant client
    client = QdrantClient(
        url=os.environ["QDRANT_URL"],
        api_key=os.environ["QDRANT_API_KEY"],
    )
    point_id = str(uuid.uuid4())
    documents=[payload]
    client.upload_points(
    collection_name=os.environ["QDRANT_COLLECTION"],
    points=[
        models.PointStruct(
            id=point_id, vector=encoder.encode(doc["description"]).tolist(), payload=doc
        )
        for idx, doc in enumerate(documents)
    ],
)
