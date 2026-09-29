import { useState, useCallback } from "react";

export function useChat(repoId) {
  const [messages, setMessages] = useState([]);
  const [busy, setBusy] = useState(false);

  const ask = useCallback(async (question) => {
    const history = messages.map(({ role, content }) => ({ role, content }));
    setMessages((m) => [...m, { role: "user", content: question }, { role: "assistant", content: "", sources: [] }]);
    setBusy(true);
    const patch = (fn) => setMessages((m) => m.map((x, i) => (i === m.length - 1 ? fn(x) : x)));
    const r = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ repo_id: repoId, question, history }),
    });
    const reader = r.body.getReader();
    const dec = new TextDecoder();
    let buf = "";
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      buf += dec.decode(value, { stream: true });
      const parts = buf.split("\n\n");
      buf = parts.pop();
      for (const p of parts) {
        if (!p.startsWith("data: ")) continue;
        const ev = JSON.parse(p.slice(6));
        if (ev.type === "sources") patch((x) => ({ ...x, sources: ev.sources }));
        if (ev.type === "token") patch((x) => ({ ...x, content: x.content + ev.t }));
      }
    }
    setBusy(false);
  }, [messages, repoId]);

  return { messages, ask, busy };
}
