import json

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.ingest.chunker import chunk_file
from app.ingest.clone import DATA, fetch, files, sha
from app.llm import generate
from app.retrieval import bm25, hybrid, rerank, vector

app = FastAPI(title="RepoMind RAG service")


class IndexReq(BaseModel):
    repo_url: str


class QueryReq(BaseModel):
    repo_id: str
    question: str
    mode: str = "rerank"  # vector | hybrid | rerank
    k: int = 5
    history: list = []


def _state(rid):
    p = DATA / rid / "state.json"
    return json.loads(p.read_text()) if p.exists() else {"hashes": {}, "chunks": []}


@app.post("/index")
def index(req: IndexReq):
    rid, path = fetch(req.repo_url)
    state = _state(rid)
    new, changed = {}, []
    for p in files(path):
        rel = str(p.relative_to(path))
        new[rel] = sha(p)
        if state["hashes"].get(rel) != new[rel]:
            changed.append(rel)
    removed = [r for r in state["hashes"] if r not in new]
    stale = set(changed) | set(removed)  # incremental: only these get re-embedded
    kept = [c for c in state["chunks"] if c["file"] not in stale]
    fresh = [c for rel in changed for c in chunk_file(rel, (path / rel).read_text(errors="ignore"))]
    vector.ensure(rid)
    vector.delete_files(rid, list(stale))
    vector.upsert(rid, fresh)
    chunks = kept + fresh
    (DATA / rid / "state.json").write_text(json.dumps({"hashes": new, "chunks": chunks}))
    bm25.load(rid, chunks)
    return {"repo_id": rid, "files_changed": len(changed), "files_removed": len(removed), "chunks": len(chunks)}


def retrieve(rid, q, mode, k):
    if not bm25.loaded(rid):
        st = _state(rid)
        if not st["chunks"]:
            raise HTTPException(404, "repo not indexed")
        bm25.load(rid, st["chunks"])
    vec = vector.search(rid, q, 20)
    if mode == "vector":
        return vec[:k]
    fused = hybrid.rrf([vec, bm25.search(rid, q, 20)])
    if mode == "hybrid":
        return fused[:k]
    return rerank.rerank(q, fused[:20], k)


@app.post("/search")
def search(req: QueryReq):
    return [{k: v for k, v in c.items() if k != "text"} for c in retrieve(req.repo_id, req.question, req.mode, req.k)]


@app.post("/chat")
def chat(req: QueryReq):
    ctx = retrieve(req.repo_id, req.question, req.mode, req.k)

    def events():
        srcs = [{"file": c["file"], "start": c["start"], "end": c["end"]} for c in ctx]
        yield f"data: {json.dumps({'type': 'sources', 'sources': srcs})}\n\n"
        for t in generate.stream(req.question, ctx, req.history):
            yield f"data: {json.dumps({'type': 'token', 't': t})}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream")
