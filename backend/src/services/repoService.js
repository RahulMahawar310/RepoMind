export const RAG = process.env.RAG_URL || "http://localhost:8000";

export async function indexRepo(repo_url) {
  const r = await fetch(`${RAG}/index`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ repo_url }),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}
