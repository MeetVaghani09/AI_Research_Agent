
import React from 'react';
import ReactMarkdown from 'react-markdown';

const API_BASE_URL = 'http://127.0.0.1:8000';

const Message = ({ message }) => {
  const isUser = message.role === 'user';

  const getDocumentUrl = (source) => {
    const filename = encodeURIComponent(source.file);

    return `${API_BASE_URL}/api/source/${encodeURIComponent(
      source.session_id
    )}/${filename}#page=${source.page}`;
  };

  return (
    <div className={`message ${isUser ? 'user' : 'assistant'}`}>
      <div className="message-header">
        <span className="message-avatar">
          {isUser ? '👤' : '🤖'}
        </span>

        <span className="message-role">
          {isUser ? 'You' : 'ResearchOS'}
        </span>

        <span className="message-time">
          {message.timestamp || new Date().toLocaleTimeString()}
        </span>
      </div>

      <div className="message-content">
        <ReactMarkdown>
          {message.content}
        </ReactMarkdown>

        {message.sources && message.sources.length > 0 && (
          <div className="message-sources">
            <strong>📚 Sources</strong>

            <ul>
              {message.sources.map((source, idx) => (
                <li key={idx}>
                  {source.type === 'web' ? (
                    <a
                      href={source.url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      🌐 {source.citation || `[Web ${idx + 1}]`}{' '}
                      {source.title || source.label}
                    </a>
                  ) : (
                    <a
                      href={getDocumentUrl(source)}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      📄 {source.citation || `[Document ${idx + 1}]`}{' '}
                      {source.file} — Page {source.page}
                    </a>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default Message;

