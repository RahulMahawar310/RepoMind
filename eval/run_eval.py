"""Usage: python eval/run_eval.py <repo_id>
Replace questions.json with 30-40 Q&A pairs about the repo you index
(expect_files = ground truth)."""
import json
import sys

import requests

API = "http://localhost:8000"


def run(repo, mode, k=5):
    with open("eval/questions.json", encoding="utf-8") as f:
        qs = json.load(f)
    hits = rr = 0
    for q in qs:
        res = requests.post(
            f"{API}/search",
            json={"repo_id": repo, "question": q["q"], "mode": mode, "k": k},
        ).json()
        rank = next(
            (i + 1 for i, r in enumerate(res) if r["file"] in q["expect_files"]),
            None,
        )
        if rank:
            hits += 1
            rr += 1 / rank
    return hits / len(qs), rr / len(qs)


if __name__ == "__main__":
    repo = sys.argv[1]
    print("| Setup | Hit@5 | MRR |\n|---|---|---|")
    modes = [
        ("vector", "Vector only"),
        ("hybrid", "+ BM25 hybrid"),
        ("rerank", "+ Reranker"),
    ]
    for mode, name in modes:
        h, m = run(repo, mode)
        print(f"| {name} | {h:.2f} | {m:.2f} |")