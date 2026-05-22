import { useEffect, useRef, useState } from "react";
import "./App.css";
import { askBackendStream } from "./api/chat";

const STORAGE_KEY = "hygeia_chat_history";

const WELCOME = {
  role: "assistant",
  text: "Përshëndetje! Jam asistenti i Spitalit Hygeia.\nMund t'ju ndihmoj me informacion për mjekë, departamente, çmime dhe rezervime.\n\nHello! I'm the Hygeia Hospital assistant. Ask me anything in Albanian or English.",
  sources: []
};

function Bubble({ role, text, sources }) {
  const agentLabel = sources && sources.length > 0 ? sources[0].file?.replace(/.*[\\/]/, '') : null;

  return (
    <div className={`bubbleRow ${role}`}>
      <div className={`bubble ${role}`}>
        <span style={{ whiteSpace: "pre-wrap" }}>{text}</span>
        {agentLabel && (
          <div className="source-tag">📄 {agentLabel}</div>
        )}
      </div>
    </div>
  );
}

export default function App() {
  const [messages, setMessages] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      return saved ? JSON.parse(saved) : [WELCOME];
    } catch {
      return [WELCOME];
    }
  });

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  // Persist chat to localStorage whenever messages change
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
    } catch {
      // storage full — ignore
    }
  }, [messages]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  function clearChat() {
    setMessages([WELCOME]);
    localStorage.removeItem(STORAGE_KEY);
  }

  async function send() {
    const q = input.trim();
    if (!q || loading) return;

    const userMsg = { role: "user", text: q, sources: [] };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setLoading(true);

    // Build history for backend (last 6 turns)
    const history = messages
      .filter(m => m.role === "user" || m.role === "assistant")
      .slice(-6)
      .map(m => ({ role: m.role, content: m.text }));

    // Add a placeholder assistant message we'll update token by token
    const placeholderIndex = messages.length + 1; // after userMsg
    setMessages((m) => [...m, { role: "assistant", text: "", sources: [] }]);

    try {
      let fullText = "";

      const meta = await askBackendStream(q, history, (token) => {
        fullText += token;
        setMessages((m) => {
          const updated = [...m];
          updated[updated.length - 1] = {
            role: "assistant",
            text: fullText,
            sources: []
          };
          return updated;
        });
      });

      // Final update with sources
      setMessages((m) => {
        const updated = [...m];
        updated[updated.length - 1] = {
          role: "assistant",
          text: fullText,
          sources: meta.sources || []
        };
        return updated;
      });

    } catch (e) {
      setMessages((m) => {
        const updated = [...m];
        updated[updated.length - 1] = {
          role: "assistant",
          text: "Ndodhi një gabim gjatë lidhjes me serverin. Provo përsëri.\n(Connection error — please try again.)",
          sources: []
        };
        return updated;
      });
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
              <p>Informacion i saktë për shërbimet e Spitalit Hygeia · English supported</p>
            </div>
          </div>
          <button className="clear-btn" onClick={clearChat} title="Clear conversation">
            ✕ Clear
          </button>
        </div>

        <div className="chat">
          {messages.map((m, i) => (
            <Bubble key={i} role={m.role} text={m.text} sources={m.sources} />
          ))}

          {loading && messages[messages.length - 1]?.text === "" && (
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
              onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) send(); }}
              placeholder="Shkruani pyetjen... / Ask anything..."
              disabled={loading}
            />
            <button className="btn" onClick={send} disabled={loading}>
              {loading ? "..." : "Dërgo"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
