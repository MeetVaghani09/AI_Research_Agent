import React, { useState, useEffect } from 'react';

import { queryAPI } from '../services/api';

const StatusIndicator = () => {
  const [status, setStatus] = useState({
    deepseek: false,
    tavily: false,
    qdrant: false,
    redis: false,
  });

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const data = await queryAPI.getStatus();

        setStatus({
          deepseek: data.services?.deepseek === 'online',
          tavily: data.services?.tavily === 'online',
          qdrant: data.services?.qdrant === 'online',
          redis: data.services?.redis === 'online',
        });
      } catch (error) {
        console.error('Failed to fetch status:', error);
      }
    };

    fetchStatus();

    const interval = setInterval(fetchStatus, 30000);

    return () => clearInterval(interval);
  }, []);

  const statusItems = [
    { key: 'deepseek', label: 'DeepSeek', icon: '🧠' },
    { key: 'tavily', label: 'Tavily', icon: '🌐' },
    { key: 'qdrant', label: 'Qdrant', icon: '💾' },
    { key: 'redis', label: 'Redis', icon: '⚡' },
  ];

  return (
    <div className="status-indicator">
      <h3>📊 System Status</h3>

      {statusItems.map((item) => (
        <div key={item.key} className="status-item">
          <span className="status-icon">{item.icon}</span>

          <span className="status-label">
            {item.label}
          </span>

          <span
            className={`status-value ${
              status[item.key] ? 'online' : 'offline'
            }`}
          >
            {status[item.key]
              ? '🟢 Online'
              : '🔴 Offline'}
          </span>
        </div>
      ))}
    </div>
  );
};

export default StatusIndicator;