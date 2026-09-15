import React, { useRef, useEffect } from 'react';
import Message from './Message';

const Chat = ({ messages, isTyping }) => {
  const chatContainerRef = useRef(null);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="chat-container" ref={chatContainerRef}>
      {messages.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">🔬</div>
          <h3>Welcome to ResearchOS</h3>
          <p>Ask a research question or upload a PDF to get started</p>
        </div>
      ) : (
        messages.map((message, index) => (
          <Message key={index} message={message} />
        ))
      )}
      {isTyping && (
        <div className="typing-indicator">
          <span>🤖 ResearchOS is thinking</span>
          <span className="dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
      )}
    </div>
  );
};

export default Chat;