import React, { useState, useEffect, useRef } from 'react';
import { gameAPI } from '../../services/api';
import type { TeamMessage } from '../../types/team';
import './team-chat.css';

interface TeamChatProps {
  teamId: string;
  playerId: string;
  playerName: string;
}

export const TeamChat: React.FC<TeamChatProps> = ({ teamId, playerId, playerName }) => {
  const [messages, setMessages] = useState<TeamMessage[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadMessages();
    // Poll for new messages every 5 seconds
    const interval = setInterval(loadMessages, 5000);
    return () => clearInterval(interval);
  }, [teamId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadMessages = async () => {
    try {
      const response = await gameAPI.team.getMessages(teamId, 100);
      const msgs = response.messages || [];
      setMessages(msgs);
      setLoading(false);
      
      // Note: markMessagesRead might need a different API endpoint
      // For now, we'll skip marking as read since it's not in the API contract
    } catch (error) {
      console.error('Failed to load messages:', error);
      setLoading(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!newMessage.trim() || sending) return;
    
    setSending(true);
    try {
      const response = await gameAPI.team.sendMessage(teamId, newMessage.trim());
      setMessages([...messages, response.message]);
      setNewMessage('');
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setSending(false);
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    
    if (diff < 60000) return 'just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    if (diff < 604800000) return `${Math.floor(diff / 86400000)}d ago`;
    
    return date.toLocaleDateString();
  };

  const renderMessage = (message: TeamMessage) => {
    const isOwnMessage = message.senderId === playerId;
    
    return (
      <div 
        key={message.id} 
        className={`chat-message ${message.type} ${isOwnMessage ? 'own' : ''}`}
      >
        {message.type === 'system' ? (
          <div className="system-message">
            <span className="message-content">{message.content}</span>
            <span className="message-time">{formatTimestamp(message.timestamp)}</span>
          </div>
        ) : (
          <>
            <div className="message-header">
              <span className="message-sender">
                {message.senderName}
                <span className={`role-indicator ${message.senderRole}`}>
                  {message.senderRole === 'leader' && ' 👑'}
                  {message.senderRole === 'officer' && ' ⭐'}
                </span>
              </span>
              <span className="message-time">{formatTimestamp(message.timestamp)}</span>
            </div>
            <div className="message-content">{message.content}</div>
            {message.readBy.length > 0 && (
              <div className="message-read-status">
                Read by {message.readBy.length} member{message.readBy.length !== 1 && 's'}
              </div>
            )}
          </>
        )}
      </div>
    );
  };

  if (loading) {
    return <div className="team-chat loading">Loading chat...</div>;
  }

  return (
    <div className="team-chat">
      <div className="chat-header">
        <h3>Team Chat</h3>
        <div className="chat-info">
          <span className="member-count">👥 12 members</span>
          <span className="online-count">🟢 8 online</span>
        </div>
      </div>

      <div className="chat-messages" ref={chatContainerRef}>
        {messages.length === 0 ? (
          <div className="no-messages">
            <p>No messages yet. Start the conversation!</p>
          </div>
        ) : (
          messages.map(renderMessage)
        )}
        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-form" onSubmit={handleSendMessage}>
        <div className="input-wrapper">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Type your message..."
            disabled={sending}
            maxLength={500}
          />
          <button type="submit" disabled={!newMessage.trim() || sending}>
            {sending ? '...' : 'Send'}
          </button>
        </div>
        <div className="input-info">
          <span className="char-count">{newMessage.length}/500</span>
          <span className="typing-indicator">Press Enter to send</span>
        </div>
      </form>

      <div className="chat-shortcuts">
        <button onClick={() => setNewMessage('/mission ')}>Mission</button>
        <button onClick={() => setNewMessage('/rally ')}>Rally</button>
        <button onClick={() => setNewMessage('/help ')}>Help</button>
        <button onClick={() => setNewMessage('/status ')}>Status</button>
      </div>
    </div>
  );
};