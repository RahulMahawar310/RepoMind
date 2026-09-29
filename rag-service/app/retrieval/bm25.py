import re

from rank_bm25 import BM25Okapi

_cache = {}


def tok(s):
    return re.findall(r"[a-z0-9]+", re.sub(r"([a-z])([A-Z])", r"\1 \2", s).lower().replace("_", " "))


def load(rid, chunks):
    _cache[rid] = (BM25Okapi([tok(c["file"] + " " + c["text"]) for c in chunks]), chunks)


def loaded(rid):
    return rid in _cache


def search(rid, q, k=20):
    bm, chunks = _cache[rid]
    scores = bm.get_scores(tok(q))
    idx = sorted(range(len(scores)), key=lambda i: -scores[i])[:k]
    return [chunks[i] for i in idx if scores[i] > 0]
