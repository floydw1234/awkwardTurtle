/*
 * NotificationsPage Component
 * Displays user notifications with read/unread status and allows marking as read
 */

import { useState, useEffect, useCallback } from 'react'

import { notificationsAPI } from '../utils/api'

function NotificationsPage({ username }) {
  const [notifications, setNotifications] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const loadNotifications = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await notificationsAPI.get()
      setNotifications(response.data.notifications || [])
    } catch (err) {
      console.error('Failed to load notifications:', err)
      setError('Failed to load notifications')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadNotifications()
  }, [loadNotifications])

  const formatTime = useCallback((dateString) => {
    const date = new Date(dateString)
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    })
  }, [])

  const handleMarkAsRead = async (notificationId) => {
    try {
      const response = await notificationsAPI.get()
      setNotifications(response.data.notifications || [])
    } catch (err) {
      console.error('Failed to mark as read:', err)
    }
  }

  const renderNotificationItem = (notification) => {
    const isUnread = !notification.is_read
    return (
      <li
        key={notification.id}
        className={`notification ${isUnread ? 'unread' : 'read'}`}
        onClick={() => isUnread && handleMarkAsRead(notification.id)}
        role="button"
        tabIndex={0}
      >
        <div className="notification-header">
          <strong>{notification.title}</strong>
          {isUnread && <span className="unread-indicator" />}
        </div>
        <div className="notification-content">{notification.message}</div>
        <div className="notification-time">{formatTime(notification.created_at)}</div>
      </li>
    )
  }

  return (
    <div className="notifications-page">
      <h2>Notifications</h2>

      {error && <div className="error-message">{error}</div>}

      {loading && notifications.length === 0 ? (
        <p>Loading notifications...</p>
      ) : (
        <div className="notifications-list-section">
          {notifications.length === 0 ? (
            <p className="empty-state">No notifications yet.</p>
          ) : (
            <ul className="notifications-list">
              {notifications.map(renderNotificationItem)}
            </ul>
          )}
        </div>
      )}
    </div>
  )
}

export default NotificationsPage
