import { Bot, UserRound } from "lucide-react";

export default function ChatMessage({ message }) {
  const assistant = message.role === "assistant";
  return (
    <article className={`chat-message ${assistant ? "chat-message--assistant" : "chat-message--user"}`}>
      <div className="message-avatar">{assistant ? <Bot size={15} /> : <UserRound size={15} />}</div>
      <div className="message-content"><p>{message.content}</p><time>{new Date(message.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</time></div>
    </article>
  );
}
