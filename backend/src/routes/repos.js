import { Router } from "express";
import { indexRepo } from "../services/repoService.js";

const router = Router();
router.post("/", async (req, res) => {
  const { repo_url } = req.body;
  if (!/^https:\/\/github\.com\/[\w.-]+\/[\w.-]+/.test(repo_url || ""))
    return res.status(400).json({ error: "Valid GitHub repo URL required" });
  try {
    res.json(await indexRepo(repo_url));
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});
export default router;
