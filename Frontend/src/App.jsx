import { useEffect, useRef, useState } from "react";
import "./App.css";
import { askBackend } from "./api/chat";

function Bubble({ role, text }) {
  return (
    <div className={`bubbleRow ${role}`}>
      <div className={`bubble ${role}`}>{text}</div>
    </div>
  );
}

export default function App() {
  const [messages, setMessages] = useState([
    { role: "assistant", text: "Përshëndetje! Jam asistenti i Spitalit Hygeia. Si mund t’ju ndihmoj sot?" }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function send() {
    const q = input.trim();
    if (!q || loading) return;

    setMessages((m) => [...m, { role: "user", text: q }]);
    setInput("");
    setLoading(true);

    try {
  const lastTurns = messages
    .filter(m => m.role === "user" || m.role === "assistant")
    .slice(-6)
    .map(m => ({ role: m.role, content: m.text }));

  const data = await askBackend(q, lastTurns);

  setTimeout(() => {
    setMessages((m) => [...m, { role: "assistant", text: data.answer }]);
  }, 250);
} catch (e) {
  setMessages((m) => [
    ...m,
    { role: "assistant", text: "Ndodhi një gabim gjatë lidhjes me serverin. Provo përsëri." }
  ]);
} finally {
  setLoading(false);
}

  }

  return (
    <div className="page">
      <div className="shell">
        <div className="header">
          <div className="brand">
            <div className="logo"><span>HA</span></div>
            <div className="title">
              <h1>Hygeia Assistant</h1>
              <p>Informacion i saktë për shërbimet shëndetësore të Spitalit Hygeia</p>
            </div>
          </div>
        </div>

        <div className="chat">
          {messages.map((m, i) => (
            <Bubble key={i} role={m.role} text={m.text} />
          ))}

          {loading && (
            <div className="bubbleRow assistant">
              <div className="bubble assistant">
                Po mendoj<span className="typing"></span>
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        <div className="footer">
          <div className="inputRow">
            <input
              className="input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter") send(); }}
              placeholder="✦ ✧ Shëndeti yt, një pyetje larg... ✧ ✦"
            />
            <button className="btn" onClick={send} disabled={loading}>
              Dërgo
            </button>
          </div>


        </div>
      </div>
    </div>
  );
}
