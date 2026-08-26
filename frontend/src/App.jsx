import { useState } from "react";
import { orient } from "./api/client.js";
import ChatBox from "./components/ChatBox.jsx";
import TraceViewer from "./components/TraceViewer.jsx";

export default function App() {
  const [result, setResult] = useState(null);
  return <main><h1>Orient'AI</h1><ChatBox onResult={(answers) => orient(answers).then(setResult)} /><TraceViewer result={result} /></main>;
}