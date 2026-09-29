import { useState } from "react";
import RepoInput from "./components/RepoInput.jsx";
import ChatWindow from "./components/ChatWindow.jsx";

export default function App() {
  const [repoId, setRepoId] = useState(null);
  return (
    <main>
      <h1>RepoMind</h1>
      <RepoInput onIndexed={setRepoId} />
      {repoId && <ChatWindow repoId={repoId} />}
    </main>
  );
}
