import { useState } from "react";

export default function ChatBox({ onResult }) {
  const [text, setText] = useState("");
  return <form onSubmit={(event) => { event.preventDefault(); onResult({ interests: text }); }}><label>Vos centres d'intérêt<textarea value={text} onChange={(event) => setText(event.target.value)} /></label><button type="submit">Analyser</button></form>;
}