import { useEffect, useRef, useState } from "react";
import { askBackendStream } from "./api/chat";

const AGENT_BADGES = {
  billing: { emoji: "💊", label: "Billing" },
  doctors: { emoji: "👨‍⚕️", label: "Doctors" },
  departments: { emoji: "🏥", label: "Departments" },
  reception: { emoji: "📋", label: "Reception" },
};

const QUICK_STARTS = [
  "My stomach hurts — which doctor should I see?",
  "I have chest pain, who should I consult?",
  "How do I book an appointment?",
  "What maternity packages do you offer?",
];

function formatTime(date) {
  return new Intl.DateTimeFormat("en", { hour: "2-digit", minute: "2-digit" }).format(date);
}

function AgentBadge({ agent }) {
  const badge = AGENT_BADGES[agent];
  if (!badge) return null;
  return (
    <span className="inline-flex items-center gap-1 text-xs text-teal-700 bg-teal-50 border border-teal-200 px-2 py-0.5 rounded-full font-medium">
      {badge.emoji} {badge.label}
    </span>
  );
}

function TypingIndicator() {
  return (
    <div className="flex justify-start mb-4 px-4 sm:px-6">
      <div className="w-8 h-8 rounded-full bg-[#0891b2] flex items-center justify-center text-white text-xs font-bold mr-2 mt-0.5 flex-shrink-0">
        H
      </div>
      <div className="bg-white rounded-2xl rounded-tl-sm shadow border border-gray-100 px-4 py-3">
        <div className="flex gap-1.5 items-center h-5">
          <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
          <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "160ms" }} />
          <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "320ms" }} />
        </div>
      </div>
    </div>
  );
}

function Message({ msg }) {
  const isUser = msg.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4 px-4 sm:px-6`}>
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-[#0891b2] flex items-center justify-center text-white text-xs font-bold mr-2 mt-0.5 flex-shrink-0">
          H
        </div>
      )}
      <div className={`flex flex-col ${isUser ? "items-end" : "items-start"} max-w-[75%] sm:max-w-[65%]`}>
        <div
          className={`px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap shadow-sm ${
            isUser
              ? "bg-[#1e3a5f] text-white rounded-tr-sm"
              : "bg-white text-gray-800 rounded-tl-sm border border-gray-100"
          }`}
        >
          {msg.text}
        </div>
        <div className="flex items-center gap-2 mt-1 flex-wrap">
          {msg.agent && <AgentBadge agent={msg.agent} />}
          <span className="text-xs text-gray-400">{formatTime(msg.timestamp)}</span>
        </div>
      </div>
      {isUser && (
        <div className="w-8 h-8 rounded-full bg-[#1e3a5f] flex items-center justify-center text-white text-[10px] font-bold ml-2 mt-0.5 flex-shrink-0">
          You
        </div>
      )}
    </div>
  );
}

function WelcomeScreen({ onQuickStart }) {
  return (
    <div className="flex flex-col items-center justify-center min-h-full px-6 py-16 text-center">
      <div className="w-20 h-20 rounded-3xl bg-gradient-to-br from-[#1e3a5f] to-[#0891b2] flex items-center justify-center shadow-xl mb-6">
        <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v6m3-3H9m12 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
        </svg>
      </div>
      <h2 className="text-2xl sm:text-3xl font-bold text-[#1e3a5f] mb-3">Hygeia Hospital AI Assistant</h2>
      <p className="text-gray-500 text-sm max-w-sm mb-1">
        Your intelligent assistant for Hygeia Hospital Tirana.
      </p>
      <p className="text-gray-400 text-xs mb-10">Ask me anything in Albanian or English.</p>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-lg">
        {QUICK_STARTS.map((q) => (
          <button
            key={q}
            onClick={() => onQuickStart(q)}
            className="text-left px-4 py-3.5 rounded-xl border border-blue-100 bg-white hover:bg-blue-50 hover:border-[#0891b2] text-sm text-[#1e3a5f] font-medium shadow-sm transition-all duration-150 cursor-pointer"
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);
  const textareaRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function send(questionText) {
    const q = typeof questionText === "string" ? questionText.trim() : input.trim();
    if (!q || loading) return;

    const userMsg = { role: "user", text: q, agent: null, sources: [], timestamp: new Date() };
    const placeholder = { role: "assistant", text: "", agent: null, sources: [], timestamp: new Date() };

    setInput("");
    if (textareaRef.current) textareaRef.current.style.height = "auto";
    setLoading(true);

    const history = messages
      .filter((m) => m.role === "user" || m.role === "assistant")
      .slice(-10)
      .map((m) => ({ role: m.role, content: m.text }));

    setMessages((prev) => [...prev, userMsg, placeholder]);

    try {
      let fullText = "";
      const meta = await askBackendStream(q, history, (token) => {
        fullText += token;
        setMessages((m) => {
          const next = [...m];
          next[next.length - 1] = { ...next[next.length - 1], text: fullText };
          return next;
        });
      });

      setMessages((m) => {
        const next = [...m];
        next[next.length - 1] = {
          ...next[next.length - 1],
          text: fullText,
          agent: meta.agent,
          sources: meta.sources || [],
        };
        return next;
      });
    } catch {
      setMessages((m) => {
        const next = [...m];
        next[next.length - 1] = {
          ...next[next.length - 1],
          text: "Connection error — please try again.\n(Ndodhi një gabim. Provo përsëri.)",
        };
        return next;
      });
    } finally {
      setLoading(false);
      textareaRef.current?.focus();
    }
  }

  const isEmpty = messages.length === 0;
  const lastMsg = messages[messages.length - 1];
  const showTyping = loading && lastMsg?.role === "assistant" && lastMsg?.text === "";

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <header className="flex-shrink-0 bg-[#1e3a5f] text-white px-4 sm:px-6 py-3 shadow-lg">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-[#0891b2] flex items-center justify-center shadow-md flex-shrink-0">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v6m3-3H9m12 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
              </svg>
            </div>
            <div>
              <h1 className="font-bold text-base leading-tight">Hygeia Hospital AI Assistant</h1>
              <p className="text-blue-300 text-xs">Shqip / English · Powered by Gemini</p>
            </div>
          </div>
          {!isEmpty && (
            <button
              onClick={() => setMessages([])}
              className="text-blue-300 hover:text-white text-xs border border-blue-700 hover:border-blue-400 px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1.5 flex-shrink-0"
            >
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
              </svg>
              Clear
            </button>
          )}
        </div>
      </header>

      {/* Chat / Welcome */}
      <main className="flex-1 overflow-y-auto">
        {isEmpty ? (
          <WelcomeScreen onQuickStart={send} />
        ) : (
          <div className="py-6 max-w-4xl mx-auto">
            {messages.map((msg, i) => {
              if (msg.role === "assistant" && msg.text === "") return null;
              return <Message key={i} msg={msg} />;
            })}
            {showTyping && <TypingIndicator />}
            <div ref={bottomRef} />
          </div>
        )}
      </main>

      {/* Input */}
      <footer className="flex-shrink-0 bg-white border-t border-gray-200 px-4 py-3">
        <div className="max-w-4xl mx-auto flex gap-2 items-end">
          <textarea
            ref={textareaRef}
            className="flex-1 resize-none rounded-xl border border-gray-300 focus:border-[#0891b2] focus:ring-2 focus:ring-cyan-100 outline-none px-4 py-2.5 text-sm text-gray-800 bg-white placeholder-gray-400 transition-colors overflow-y-hidden"
            style={{ minHeight: "44px", maxHeight: "120px" }}
            value={input}
            onChange={(e) => {
              setInput(e.target.value);
              e.target.style.height = "auto";
              e.target.style.height = Math.min(e.target.scrollHeight, 120) + "px";
            }}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                send();
              }
            }}
            placeholder="Ask anything... / Shkruani pyetjen..."
            disabled={loading}
            rows={1}
          />
          <button
            onClick={() => send()}
            disabled={loading || !input.trim()}
            className="flex-shrink-0 w-11 h-11 rounded-xl bg-[#1e3a5f] hover:bg-[#0891b2] disabled:opacity-40 disabled:cursor-not-allowed text-white flex items-center justify-center shadow transition-colors duration-150"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M2.01 21 23 12 2.01 3 2 10l15 2-15 2z" />
            </svg>
          </button>
        </div>
        <p className="text-center text-xs text-gray-400 mt-1.5">Shift+Enter for new line</p>
      </footer>
    </div>
  );
}
