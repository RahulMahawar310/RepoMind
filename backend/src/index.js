import express from "express";
import cors from "cors";
import repos from "./routes/repos.js";
import chat from "./routes/chat.js";

const app = express();
app.use(cors());
app.use(express.json());
app.use("/api/repos", repos);
app.use("/api/chat", chat);
app.get("/health", (_, res) => res.json({ ok: true }));
app.listen(4000, () => console.log("backend on :4000"));
