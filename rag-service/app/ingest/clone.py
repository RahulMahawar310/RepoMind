import hashlib
import pathlib
import subprocess

DATA = pathlib.Path("data")
EXT = {".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".cpp", ".c", ".go", ".md"}
SKIP = {"node_modules", ".git", "dist", "build", "__pycache__", ".venv"}


def repo_id(url: str) -> str:
    return url.rstrip("/").removesuffix(".git").split("github.com/")[-1].replace("/", "__")


def fetch(url: str):
    rid = repo_id(url)
    path = DATA / rid / "src"
    if path.exists():
        subprocess.run(["git", "-C", str(path), "pull", "--ff-only"], check=True)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "clone", "--depth", "1", url, str(path)], check=True)
    return rid, path


def files(path: pathlib.Path):
    for p in path.rglob("*"):
        if p.is_file() and p.suffix in EXT and not (SKIP & set(p.parts)) and p.stat().st_size < 200_000:
            yield p


def sha(p: pathlib.Path) -> str:
    return hashlib.sha1(p.read_bytes()).hexdigest()
