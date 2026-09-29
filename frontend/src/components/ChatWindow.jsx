import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useChat } from "../hooks/useStream.js";
import SourceCard from "./SourceCard.jsx";

export default function ChatWindow({ repoId }) {
  const { messages, ask, busy } = useChat(repoId);
  const [q, setQ] = useState("");

  return (
    <div className="chat">
      <div className="messages">
        {messages.map((m, i) => (
          <div key={i} className={"msg " + m.role}>
            {m.role === "assistant" ? (
              <div className="answer">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {m.content}
                </ReactMarkdown>
              </div>
            ) : (
              <div>{m.content}</div>
            )}
            {m.sources?.length > 0 && (
              <div className="sources">
                {m.sources.map((s, j) => (
                  <SourceCard key={j} s={s} />
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (q && !busy) {
            ask(q);
            setQ("");
          }
        }}
      >
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Ask anything about this repo..."
        />
        <button disabled={busy}>Ask</button>
      </form>
    </div>
  );
}