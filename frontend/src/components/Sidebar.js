
import React, { useEffect, useState } from 'react';

import StatusIndicator from './StatusIndicator';
import { queryAPI } from '../services/api';

const API_BASE_URL = 'http://127.0.0.1:8000';
const SESSION_ID = 'research-user';

const Sidebar = ({
  onNewConversation,
  onClearDocuments,
  documentsRefreshKey,
}) => {
  const [documents, setDocuments] = useState([]);
  const [loadingDocuments, setLoadingDocuments] = useState(true);
  const [deletingDocument, setDeletingDocument] = useState(null);

  const formatFileSize = (bytes) => {
    if (!bytes) return '0 B';

    const units = ['B', 'KB', 'MB', 'GB'];

    const index = Math.floor(
      Math.log(bytes) / Math.log(1024)
    );

    return `${(bytes / Math.pow(1024, index)).toFixed(1)} ${
      units[index]
    }`;
  };

  const formatUploadDate = (dateString) => {
    if (!dateString) return 'Unknown date';

    return new Date(dateString).toLocaleString(
      'en-IN',
      {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      }
    );
  };

  const loadDocuments = async () => {
    try {
      setLoadingDocuments(true);

      const response = await queryAPI.getDocuments(
        SESSION_ID
      );

      setDocuments(response.documents || []);
    } catch (error) {
      console.error(
        '❌ Failed to load documents:',
        error
      );

      setDocuments([]);
    } finally {
      setLoadingDocuments(false);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, [documentsRefreshKey]);

  const handleDeleteDocument = async (filename) => {
    const confirmed = window.confirm(
      `Are you sure you want to delete "${filename}"?`
    );

    if (!confirmed) {
      return;
    }

    try {
      setDeletingDocument(filename);

      await queryAPI.deleteDocument(
        filename,
        SESSION_ID
      );

      setDocuments((prev) =>
        prev.filter(
          (document) =>
            document.filename !== filename
        )
      );

      console.log(
        '🗑️ Deleted document:',
        filename
      );
    } catch (error) {
      console.error(
        '❌ Failed to delete document:',
        error
      );

      alert(
        error.response?.data?.detail ||
          'Failed to delete document.'
      );
    } finally {
      setDeletingDocument(null);
    }
  };

  const getDocumentUrl = (filename) => {
    return `${API_BASE_URL}/api/source/${encodeURIComponent(
      SESSION_ID
    )}/${encodeURIComponent(filename)}`;
  };

  return (
    <div className="sidebar">

      {/* Sidebar Header */}
      <div className="sidebar-header">
        <h1>🔬 ResearchOS</h1>

        <p className="subtitle">
          AI Research Workspace
        </p>
      </div>

      {/* System Status */}
      <div className="sidebar-section">
        <StatusIndicator />
      </div>

      {/* Session */}
      <div className="sidebar-section">
        <h3>👤 Session</h3>

        <div className="session-info">

          <code>
            {SESSION_ID}
          </code>

          <button
            onClick={onNewConversation}
            className="new-chat-btn"
          >
            🔄 New Conversation
          </button>

          <button
            onClick={onClearDocuments}
            className="clear-docs-btn"
          >
            🗑️ Clear Documents
          </button>

        </div>
      </div>

      {/* Documents */}
      <div className="sidebar-section">

        <h3>
          📚 Documents
        </h3>

        {/* Loading */}
        {loadingDocuments ? (

          <p className="document-loading">
            Loading documents...
          </p>

        ) : documents.length === 0 ? (

          /* Empty */
          <p className="no-documents">
            No documents uploaded.
          </p>

        ) : (

          /* Document List */
          <div className="document-list">

            {documents.map((document) => (

              <div
                key={document.filename}
                className="document-item"
              >

                {/* PDF Link */}
                <a
                  href={getDocumentUrl(
                    document.filename
                  )}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="document-link"
                >

                  <span className="document-icon">
                    📄
                  </span>

                  <div className="document-info">

                    {/* Filename */}
                    <div className="document-name">
                      {document.filename}
                    </div>

                    {/* Pages + File Size */}
                    <div className="document-meta">
                      {document.pages} pages
                      {' • '}
                      {formatFileSize(
                        document.size_bytes
                      )}
                    </div>

                    {/* Upload Date */}
                    <div className="document-date">
                      {formatUploadDate(
                        document.uploaded_at
                      )}
                    </div>

                    {/* Status */}
                    <div className="document-status">

                      <span className="status-dot">
                        ●
                      </span>

                      Ready

                    </div>

                  </div>

                </a>

                {/* Delete Button */}
                <button
                  className="delete-document-btn"
                  onClick={() =>
                    handleDeleteDocument(
                      document.filename
                    )
                  }
                  disabled={
                    deletingDocument ===
                    document.filename
                  }
                  title="Delete document"
                >

                  {deletingDocument ===
                  document.filename
                    ? '⏳'
                    : '🗑️'}

                </button>

              </div>

            ))}

          </div>

        )}

      </div>

      {/* Footer */}
      <div className="sidebar-footer">

        <div className="version">
          v3.0.0
        </div>

        <div className="secure">
          🔒 Secure • Encrypted
        </div>

      </div>

    </div>
  );
};

export default Sidebar;

