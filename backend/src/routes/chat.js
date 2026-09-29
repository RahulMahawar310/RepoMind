import { Router } from "express";
import crypto from "crypto";
import * as cache from "../services/cacheService.js";
import { RAG } from "../services/repoService.js";

const router = Router();
router.post("/", async (req, res) => {
  const { repo_id, question, history = [] } = req.body;
  const first = history.length === 0; // only cache standalone questions
  const key = "chat:" + crypto.createHash("sha1").update(repo_id + "|" + question).digest("hex");
  res.set({ "Content-Type": "text/event-stream", "Cache-Control": "no-cache" });

  if (first) {
    const hit = await cache.get(key);
    if (hit) return res.end(hit);
  }
  const r = await fetch(`${RAG}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ repo_id, question, history }),
  });
  const bufs = [];
  for await (const c of r.body) {
    bufs.push(Buffer.from(c));
    res.write(c);
  }
  if (first && r.ok) await cache.set(key, Buffer.concat(bufs).toString());
  res.end();
});
export default router;
