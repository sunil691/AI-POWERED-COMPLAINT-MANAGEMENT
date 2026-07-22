import { useEffect, useRef, useState } from "react";
import { FileUp, LoaderCircle, Send, Sparkles } from "lucide-react";
import { useDispatch, useSelector } from "react-redux";
import ChatMessage from "./ChatMessage";
import { addUserMessage, sendMessage, uploadPdf } from "../store/chatSlice";

export default function CopilotChat({ onAiResponse }) {
  const dispatch = useDispatch();
  const { messages, isLoading, error } = useSelector((state) => state.chat);
  const [draft, setDraft] = useState("");
  const fileInput = useRef(null);
  const threadEnd = useRef(null);

  useEffect(() => { threadEnd.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, isLoading]);

  async function submitMessage(event) {
    event.preventDefault();
    const message = draft.trim();
    if (!message || isLoading) return;
    setDraft("");
    dispatch(addUserMessage(message));
    const action = await dispatch(sendMessage(message));
    if (sendMessage.fulfilled.match(action)) onAiResponse();
  }

  async function handleFile(event) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file || isLoading) return;
    const action = await dispatch(uploadPdf(file));
    if (uploadPdf.fulfilled.match(action)) onAiResponse();
  }

  return (
    <section className="copilot-panel">
      <header className="copilot-header"><div className="copilot-mark"><Sparkles size={18} /></div><div><p className="eyebrow">AIVOA</p><h2>Copilot</h2></div><span className="online-dot">Live</span></header>
      <div className="chat-thread">
        {!messages.length && <div className="empty-chat"><Sparkles size={27} /><h3>Bring me the complaint.</h3><p>Paste the customer narrative or attach a PDF. I will structure the record as we work.</p></div>}
        {messages.map((message) => <ChatMessage message={message} key={message.id} />)}
        {isLoading && <div className="typing"><LoaderCircle className="spin" size={16} /> Thinking through the complaint...</div>}
        <div ref={threadEnd} />
      </div>
      {error && <p className="chat-error">{error}</p>}
      <form className="chat-composer" onSubmit={submitMessage}>
        <input value={draft} onChange={(event) => setDraft(event.target.value)} placeholder="Describe the complaint or a correction..." disabled={isLoading} />
        <input ref={fileInput} type="file" accept="application/pdf" onChange={handleFile} hidden />
        <button className="icon-button" type="button" onClick={() => fileInput.current?.click()} title="Attach PDF" disabled={isLoading}><FileUp size={18} /></button>
        <button className="send-button" type="submit" title="Send message" disabled={!draft.trim() || isLoading}><Send size={17} /></button>
      </form>
      <p className="powered-by">Powered by LangGraph <span>•</span> Groq</p>
    </section>
  );
}
