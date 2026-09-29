"""Code-aware chunking: Python via ast, other languages via boundary regex,
fallback to line windows. (Swap in tree-sitter later for exact parsing.)"""
import ast
import re

BOUNDARY = re.compile(
    r"^\s*(export\s+)?(default\s+)?(async\s+)?(function|class|interface|func|public|private|protected)\b"
    r"|^\s*(export\s+)?const\s+\w+\s*=\s*(async\s*)?(\(|function)"
)


def _mk(rel, lines, s, e, kind):
    return {"file": rel, "start": s, "end": e, "kind": kind, "text": "\n".join(lines[s - 1:e])}


def _window(rel, lines, s, e, kind, size=60, overlap=10):
    out, i = [], s
    while i <= e:
        j = min(i + size - 1, e)
        out.append(_mk(rel, lines, i, j, kind))
        if j == e:
            break
        i = j - overlap + 1
    return out


def _span(rel, lines, s, e, kind, limit=120):
    return [_mk(rel, lines, s, e, kind)] if e - s + 1 <= limit else _window(rel, lines, s, e, kind)


def _py(rel, text, lines):
    out, prev_end = [], 0
    for n in ast.parse(text).body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if n.lineno - 1 > prev_end + 1:  # module-level code before this def
                out += _span(rel, lines, prev_end + 1, n.lineno - 1, "module")
            out += _span(rel, lines, n.lineno, n.end_lineno, type(n).__name__)
            prev_end = n.end_lineno
    if prev_end < len(lines):
        out += _span(rel, lines, prev_end + 1, len(lines), "module")
    return out


def _regex(rel, lines):
    starts = [i + 1 for i, l in enumerate(lines) if BOUNDARY.match(l)]
    if not starts:
        return _window(rel, lines, 1, len(lines), "block")
    starts = ([1] if starts[0] != 1 else []) + starts
    out = []
    for a, b in zip(starts, starts[1:] + [len(lines) + 1]):
        out += _span(rel, lines, a, b - 1, "block")
    return out


def chunk_file(rel: str, text: str):
    lines = text.splitlines()
    if not lines:
        return []
    chunks = []
    if rel.endswith(".py"):
        try:
            chunks = _py(rel, text, lines)
        except SyntaxError:
            pass
    elif rel.endswith((".js", ".jsx", ".ts", ".tsx", ".java", ".go", ".cpp", ".c")):
        chunks = _regex(rel, lines)
    if not chunks:
        chunks = _window(rel, lines, 1, len(lines), "text")
    return [c for c in chunks if c["text"].strip()]
