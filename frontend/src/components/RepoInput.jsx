import { useState } from "react";

export default function RepoInput({ onIndexed }) {
  const [url, setUrl] = useState("");
  const [status, setStatus] = useState("");

  async function submit(e) {
    e.preventDefault();
    setStatus("Indexing... (the first run may take a minute)");
    const r = await fetch("/api/repos", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ repo_url: url }),
    });
    const d = await r.json();
    if (!r.ok) return setStatus(d.error);
    setStatus(`Indexed: ${d.chunks} chunks (${d.files_changed} files updated)`);
    onIndexed(d.repo_id);
  }

  return (
    <form onSubmit={submit} className="repo-input">
      <input value={url} onChange={(e) => setUrl(e.target.value)} placeholder="https://github.com/user/repo" />
      <button>Index</button>
      <small>{status}</small>
    </form>
  );
}
