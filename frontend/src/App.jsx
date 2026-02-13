import { useState } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import './App.css'
import LoginForm from './components/LoginForm'
import RegisterForm from './components/RegisterForm'
import Dashboard from './components/Dashboard'
import FriendsPage from './components/FriendsPage'
import MessagesPage from './components/MessagesPage'

function App() {
  const [currentUser, setCurrentUser] = useState(null)

  const handleLogin = (username) => {
    setCurrentUser(username)
  }

  const handleLogout = () => {
    setCurrentUser(null)
  }

  const handleRegister = (username) => {
    setCurrentUser(username)
  }

  return (
    <BrowserRouter>
      <div className="app">
        <Routes>
          <Route 
            path="/login" 
            element={!currentUser ? <LoginForm onLogin={handleLogin} /> : <Navigate to="/dashboard" replace />}
          />
          <Route 
            path="/register" 
            element={!currentUser ? <RegisterForm onRegister={handleRegister} /> : <Navigate to="/dashboard" replace />}
          />
          <Route 
            path="/dashboard" 
            element={currentUser ? <Dashboard username={currentUser} onLogout={handleLogout} /> : <Navigate to="/login" replace />}
          >
            <Route index element={<Navigate to="/friends" replace />} />
            <Route path="friends" element={<FriendsPage username={currentUser} />} />
            <Route path="messages" element={<MessagesPage username={currentUser} />} />
          </Route>
          <Route path="/" element={<Navigate to={currentUser ? "/dashboard" : "/login"} replace />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}

export default App
