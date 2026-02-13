import { useState, useEffect } from 'react'
import { messagesAPI } from '../utils/api'

function ChatInterface({ friend, currentUser, messages = [] }) {
  const [newMessage, setNewMessage] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSendMessage = async (e) => {
    e.preventDefault()
    if (!newMessage.trim()) return
    
    setError('')
    setLoading(true)
    
    try {
      await messagesAPI.send(friend.id, newMessage.trim())
      setNewMessage('')
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to send message')
    } finally {
      setLoading(false)
    }
  }

  const formatTime = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h3>Chat with {friend.username}</h3>
      </div>
      
      <div className="chat-messages">
        {messages.length === 0 ? (
          <p className="empty-messages">No messages yet. Say hello!</p>
        ) : (
          messages.map((msg) => {
            const isSent = msg.sender_id === currentUser.id
            return (
              <div key={msg.id} className={`message ${isSent ? 'sent' : 'received'}`}>
                <div className="message-content">{msg.content}</div>
                <div className="message-time">{formatTime(msg.created_at)}</div>
              </div>
            )
          })
        )}
      </div>
      
      {error && <div className="error-message">{error}</div>}
      
      <form className="chat-input-form" onSubmit={handleSendMessage}>
        <input
          type="text"
          placeholder="Type a message..."
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          disabled={loading}
        />
        <button type="submit" disabled={loading || !newMessage.trim()}>
          Send
        </button>
      </form>
    </div>
  )
}

export default ChatInterface
