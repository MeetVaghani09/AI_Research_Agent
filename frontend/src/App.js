import React, { useState } from 'react';

import './App.css';

import Sidebar from './components/Sidebar';
import Chat from './components/Chat';
import InputArea from './components/InputArea';

import { queryAPI } from './services/api';

function App() {

  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content:
        "👋 Welcome to ResearchOS! I'm your AI research assistant. Ask me anything about your research or upload a PDF to get started.",
      timestamp: new Date().toLocaleTimeString(),
      sources: []
    }
  ]);

  const [isLoading, setIsLoading] = useState(false);

  const [uploadStatus, setUploadStatus] = useState('');

  // Used to tell Sidebar to reload documents
  const [documentsRefreshKey, setDocumentsRefreshKey] = useState(0);

  const handleSend = async (question) => {

    const userMessage = {
      role: 'user',
      content: question,
      timestamp: new Date().toLocaleTimeString(),
      sources: []
    };

    setMessages(prev => [...prev, userMessage]);

    setIsLoading(true);

    try {

      console.log('📤 Sending query:', question);

      const response = await queryAPI.sendQuery(question);

      console.log('📥 Response received:', response);

      const assistantMessage = {
        role: 'assistant',
        content:
          response.answer ||
          response.response ||
          'No response generated.',
        timestamp: new Date().toLocaleTimeString(),
        sources: response.sources || []
      };

      setMessages(prev => [...prev, assistantMessage]);

    } catch (error) {

      console.error('❌ Full error:', error);

      let errorMessage =
        '❌ Sorry, I encountered an error. Please try again.';

      if (error.code === 'ECONNABORTED') {

        errorMessage =
          '❌ Request timed out. The AI might be taking too long to respond.';

      } else if (error.response) {

        errorMessage =
          `❌ Server Error: ${
            error.response.data?.detail ||
            error.response.statusText
          }`;

      } else if (error.request) {

        errorMessage =
          "❌ Cannot reach the backend server. Make sure it's running on http://localhost:8000";

      }

      const errorMsg = {
        role: 'assistant',
        content: errorMessage,
        timestamp: new Date().toLocaleTimeString(),
        sources: []
      };

      setMessages(prev => [...prev, errorMsg]);

    } finally {

      setIsLoading(false);

    }
  };

  const handleUpload = async (file) => {

    if (!file) return;

    setIsLoading(true);
    setUploadStatus('Uploading...');

    try {

      console.log('📤 Uploading:', file.name);

      const response = await queryAPI.uploadPDF(file);

      console.log('📥 Upload response:', response);

      const uploadMessage = {
        role: 'assistant',
        content:
          `📄 Successfully uploaded **${
            response.filename || file.name
          }**\n\n` +
          `📊 Pages: ${response.pages || 'N/A'}\n` +
          `📑 Chunks: ${response.chunks || 'N/A'}\n\n` +
          `You can now ask questions about this document!`,
        timestamp: new Date().toLocaleTimeString(),
        sources: []
      };

      setMessages(prev => [...prev, uploadMessage]);

      setUploadStatus(
        `✅ ${file.name} uploaded successfully!`
      );

      // 🔄 Refresh document list
      setDocumentsRefreshKey(prev => prev + 1);

    } catch (error) {

      console.error('❌ Upload error:', error);

      const errorMessage = {
        role: 'assistant',
        content:
          `❌ Failed to upload: ${
            error.response?.data?.detail ||
            error.message
          }`,
        timestamp: new Date().toLocaleTimeString(),
        sources: []
      };

      setMessages(prev => [...prev, errorMessage]);

      setUploadStatus('❌ Upload failed');

    } finally {

      setIsLoading(false);

      setTimeout(() => {
        setUploadStatus('');
      }, 5000);

    }
  };

  const handleNewConversation = () => {

    setMessages([
      {
        role: 'assistant',
        content:
          '🔄 New conversation started! How can I help you with your research today?',
        timestamp: new Date().toLocaleTimeString(),
        sources: []
      }
    ]);

  };

  const handleClearDocuments = async () => {

    if (
      window.confirm(
        'Are you sure you want to clear all uploaded documents?'
      )
    ) {

      try {

        await queryAPI.clearSession();

        setMessages(prev => [
          ...prev,
          {
            role: 'assistant',
            content:
              '🗑️ All uploaded documents have been cleared from this session.',
            timestamp: new Date().toLocaleTimeString(),
            sources: []
          }
        ]);

        // 🔄 Refresh document list
        setDocumentsRefreshKey(prev => prev + 1);

      } catch (error) {

        console.error(
          '❌ Clear documents error:',
          error
        );

      }

    }

  };

  return (

    <div className="App">

      <Sidebar
        onNewConversation={handleNewConversation}
        onClearDocuments={handleClearDocuments}
        documentsRefreshKey={documentsRefreshKey}
      />

      <div className="main-content">

        <Chat
          messages={messages}
          isTyping={isLoading}
        />

        {uploadStatus && (
          <div
            className={`upload-status ${
              uploadStatus.includes('✅')
                ? 'success'
                : 'error'
            }`}
          >
            {uploadStatus}
          </div>
        )}

        <InputArea
          onSend={handleSend}
          onUpload={handleUpload}
          isLoading={isLoading}
        />

      </div>

    </div>

  );
}

export default App;