import React, { useState, useRef } from 'react';

const InputArea = ({ onSend, onUpload, isLoading }) => {
  const [input, setInput] = useState('');
  const fileInputRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSend(input);
      setInput('');
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files.length > 0) {
      onUpload(e.target.files[0]);
      e.target.value = '';
    }
  };

  return (
    <div className="input-area">
      <form onSubmit={handleSubmit} className="input-form">
        <div className="input-wrapper">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask your research question..."
            disabled={isLoading}
          />
          
          <div className="input-actions">
            <button
              type="button"
              className="upload-btn"
              onClick={() => fileInputRef.current?.click()}
              disabled={isLoading}
              title="Upload PDF"
            >
              📄
            </button>
            <button
              type="submit"
              className="send-btn"
              disabled={!input.trim() || isLoading}
            >
              {isLoading ? '⏳' : '🚀 Send'}
            </button>
          </div>
        </div>
      </form>
      
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf"
        onChange={handleFileChange}
        style={{ display: 'none' }}
      />
      
      <div className="upload-hint">
        <span>📄 Upload PDF (max 25MB)</span>
      </div>
    </div>
  );
};

export default InputArea;