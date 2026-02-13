import { Link, Outlet } from 'react-router-dom'
import { authAPI } from '../utils/api'

function Dashboard({ username, onLogout }) {
  const handleLogout = async () => {
    try {
      await authAPI.logout()
      onLogout()
    } catch (err) {
      console.error('Logout failed:', err)
      onLogout()
    }
  }

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
