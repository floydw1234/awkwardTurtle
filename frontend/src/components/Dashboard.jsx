import { Link, Outlet } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { authAPI, notificationsAPI } from '../utils/api'

function Dashboard({ username, onLogout }) {
  const [unreadCount, setUnreadCount] = useState(0)
  
  const handleLogout = async () => {
    try {
      await authAPI.logout()
      onLogout()
    } catch (err) {
      console.error('Logout failed:', err)
      onLogout()
    }
  }

  useEffect(() => {
    const loadNotificationCount = async () => {
      try {
        const response = await notificationsAPI.get()
        const notifications = response.data.notifications || []
        const unread = notifications.filter(n => !n.is_read).length
        setUnreadCount(unread)
      } catch (err) {
        console.error('Failed to load notification count:', err)
      }
    }
    
    loadNotificationCount()
  }, [])

  return (
    <div className="dashboard">
      <nav className="dashboard-nav">
        <h1 className="logo">Awkward Turtle</h1>
        <div className="user-info">
          <span className="username-display">
            Hello, <strong>{username}</strong>
          </span>
          <button onClick={handleLogout} className="logout-btn">
            Logout
          </button>
        </div>
      </nav>
      <div className="dashboard-content">
        <nav className="secondary-nav">
          <Link to="/friends" className="nav-link">
            👥 Friends
            {unreadCount > 0 && (
              <span className="notification-badge">
                {unreadCount}
              </span>
            )}
          </Link>
          <Link to="/messages" className="nav-link">
            💬 Messages
          </Link>
        </nav>
        <main className="main-content">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default Dashboard
