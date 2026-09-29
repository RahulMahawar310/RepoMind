def rrf(rankings, k=60):
    """Reciprocal Rank Fusion over several ranked chunk lists."""
    score, keep = {}, {}
    for ranking in rankings:
        for r, c in enumerate(ranking):
            key = f'{c["file"]}:{c["start"]}'
            score[key] = score.get(key, 0) + 1 / (k + r + 1)
            keep[key] = c
    return [keep[key] for key in sorted(score, key=score.get, reverse=True)]
