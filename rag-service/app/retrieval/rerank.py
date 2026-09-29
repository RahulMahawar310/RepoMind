from sentence_transformers import CrossEncoder

_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


def rerank(q, chunks, k=5):
    if not chunks:
        return []
    scores = _model.predict([(q, c["file"] + "\n" + c["text"]) for c in chunks])
    return [c for _, c in sorted(zip(scores, chunks), key=lambda x: -x[0])][:k]
