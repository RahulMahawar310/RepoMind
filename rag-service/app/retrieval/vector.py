import os, uuid
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer

client = QdrantClient(url=os.getenv("QDRANT_URL", "http://localhost:6333"))
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def embed(texts):
    return model.encode(texts, normalize_embeddings=True, batch_size=32).tolist()


def ensure(col):
    if not client.collection_exists(col):
        client.create_collection(col, vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE))


def delete_files(col, files):
    if files:
        flt = models.Filter(must=[models.FieldCondition(key="file", match=models.MatchAny(any=files))])
        client.delete(col, points_selector=models.FilterSelector(filter=flt))


def upsert(col, chunks):
    for i in range(0, len(chunks), 64):
        b = chunks[i:i + 64]
        vecs = embed([c["file"] + "\n" + c["text"] for c in b])
        client.upsert(col, points=[
            models.PointStruct(id=str(uuid.uuid5(uuid.NAMESPACE_URL, f'{c["file"]}:{c["start"]}')), vector=v, payload=c)
            for c, v in zip(b, vecs)
        ])


def search(col, q, k=20):
    return [h.payload for h in client.query_points(col, query=embed([q])[0], limit=k).points]
