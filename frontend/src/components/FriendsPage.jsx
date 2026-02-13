import { useState, useEffect } from 'react'
import { friendsAPI } from '../utils/api'

function FriendsPage({ username }) {
  const [friends, setFriends] = useState([])
  const [newFriend, setNewFriend] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const loadFriends = async () => {
    setLoading(true)
    setError('')
    try {
      const response = await friendsAPI.get()
      setFriends(response.data.friends)
    } catch (err) {
      setError('Failed to load friends')
    } finally {
      setLoading(false)
    }
  }

  const handleAddFriend = async (e) => {
    e.preventDefault()
    if (!newFriend.trim() || newFriend === username) return
    
    setLoading(true)
    setError('')
    setSuccess('')
    
    try {
      await friendsAPI.add(newFriend.trim())
      setSuccess(`Added '${newFriend}' as friend`)
      setNewFriend('')
      loadFriends()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to add friend')
    } finally {
      setLoading(false)
    }
  }

  const handleRemoveFriend = async (friendUsername) => {
    setLoading(true)
    setError('')
    
    try {
      await friendsAPI.remove(friendUsername)
      setSuccess(`Removed '${friendUsername}' from friends`)
      loadFriends()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to remove friend')
    } finally {
      setLoading(false)
    }
  }

  const handleRemoveClick = (friendUsername) => {
    if (window.confirm(`Are you sure you want to remove ${friendUsername}?`)) {
      handleRemoveFriend(friendUsername)
    }
  }

  useEffect(() => {
    loadFriends()
  }, [])

  return (
    <div className="friends-page">
      <h2>Friends</h2>
      
      <div className="add-friend-form">
        <form onSubmit={handleAddFriend}>
          <input
            type="text"
            placeholder="Enter username"
            value={newFriend}
            onChange={(e) => setNewFriend(e.target.value)}
            disabled={loading}
          />
          <button type="submit" disabled={loading}>
            Add friend
          </button>
        </form>
      </div>

      {success && <div className="success-message">{success}</div>}
      {error && <div className="error-message">{error}</div>}

      {loading && friends.length === 0 ? (
        <p>Loading friends...</p>
      ) : (
        <div className="friends-list">
          {friends.length === 0 ? (
            <p>No friends yet. Add some friends to get started!</p>
          ) : (
            <>
              <p>Total: {friends.length} friends</p>
              <ul>
                {friends.map((friend, index) => (
                  <li key={index}>
                    {typeof friend === 'string' ? friend : friend.username}
                    <button
                      onClick={() => handleRemoveClick(typeof friend === 'string' ? friend : friend.username)}
                      className="remove-btn"
                    >
                      Remove
                    </button>
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>
      )}

      <div className="action-buttons">
        <button onClick={loadFriends} disabled={loading}>
          Refresh Friends
        </button>
      </div>
    </div>
  )
}

export default FriendsPage
