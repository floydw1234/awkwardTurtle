import { useState, useEffect } from 'react'
import { friendsAPI, messagesAPI } from '../utils/api'
import ChatInterface from './ChatInterface'

function MessagesPage({ username }) {
  const [friends, setFriends] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [selectedFriend, setSelectedFriend] = useState(null)
  const [messages, setMessages] = useState([])
  const [newMessage, setNewMessage] = useState('')

  const loadFriends = async () => {
    setLoading(true)
    setError('')
    setSuccess('')
    try {
      const response = await friendsAPI.get()
      setFriends(response.data.friends)
    } catch (err) {
      setError('Failed to load friends')
    } finally {
      setLoading(false)
    }
  }

  const loadMessages = async (friendId, friendUsername) => {
    setSelectedFriend({ username: friendUsername, id: friendId })
    setError('')
    setSuccess('')
    try {
      const inboxResponse = await messagesAPI.inbox()
      setMessages(inboxResponse.data.messages.filter(msg => 
        msg.sender_id === friendId || msg.receiver_id === friendId
      ))
    } catch (err) {
      setError('Failed to load messages')
    }
  }

  const handleSendMessage = async (e) => {
    e.preventDefault()
    if (!newMessage.trim() || !selectedFriend) return
    
    setError('')
    setSuccess('')
    try {
      await messagesAPI.send(selectedFriend.id, newMessage.trim())
      setNewMessage('')
      setSuccess('Message sent')
      loadMessages(selectedFriend.id, selectedFriend.username)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to send message')
    }
  }

  useEffect(() => {
    loadFriends()
  }, [])

  return (
    <div className="messages-page">
      <h2>Messages</h2>
      
      <div className="messages-layout">
        <div className="friends-list-section">
          <h3>Your Friends</h3>
          
          {error && <div className="error-message">{error}</div>}
          {success && <div className="success-message">{success}</div>}
          
          {loading && friends.length === 0 ? (
            <p>Loading friends...</p>
          ) : (
            <div className="friends-grid">
              {friends.length === 0 ? (
                <p>No friends yet. Add some friends to get started!</p>
              ) : (
                <ul>
                  {friends.map((friend, index) => (
                    <li key={index} onClick={() => loadMessages(friend.id, friend.username)}>
                      {friend.username}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
          
          <div className="refresh-btn">
            <button onClick={loadFriends} disabled={loading}>
              Refresh Friends
            </button>
          </div>
        </div>
        
        <div className="chat-section">
          {selectedFriend ? (
            <ChatInterface 
              friend={selectedFriend} 
              currentUser={{ username, id: 0 }}
              messages={messages}
            />
          ) : (
            <div className="select-friend-message">
              <p>Select a friend to start chatting</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default MessagesPage
