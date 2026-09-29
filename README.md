# RepoMind: chat with any GitHub repo

RAG assistant for codebases: code-aware chunking, hybrid retrieval (vector + BM25 with RRF), cross-encoder reranking, streamed answers with file:line citations, Redis caching and incremental re-indexing.

**Flow:** GitHub URL -> clone -> chunk (function/class level) -> embed (MiniLM) -> Qdrant + BM25 -> RRF -> rerank -> LLM -> cited answer

## Run
```bash
cp .env.example .env        # add OPENAI_API_KEY
docker compose up --build
cd frontend && npm install && npm run dev   # http://localhost:5173
```

## Eval
```bash
python eval/run_eval.py <repo_id>   # e.g. RahulMahawar310__repomind
```
| Setup | Hit@5 | MRR |
|---|---|---|
| Vector only | - | - |
| + BM25 hybrid | - | - |
| + Reranker | - | - |

## Design decisions
- **Chunking:** ast for Python, boundary regex for JS/TS/Java/Go/C++, line windows as fallback (tree-sitter is the next upgrade).
- **Hybrid + RRF:** identifiers match keywords well, intent matches embeddings well; RRF needs no score tuning.
- **Incremental indexing:** file SHA-1 hashes; only changed files are re-chunked and re-embedded.

## Limitations / future work
Tree-sitter chunking, query rewriting for follow-ups, private repos (GitHub token), auth + rate limiting.
