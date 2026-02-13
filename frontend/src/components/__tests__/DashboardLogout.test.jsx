import { render, screen, waitFor, act, fireEvent } from '@testing-library/react'
import { vi } from 'vitest'
import { MemoryRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useState } from 'react'
import Dashboard from '../Dashboard'
import LoginForm from '../LoginForm'
import * as apiUtils from '../../utils/api'

vi.mock('../../utils/api', () => ({
  __esModule: true,
  authAPI: {
    login: vi.fn(),
    logout: vi.fn(),
  },
  friendsAPI: {
    get: vi.fn(),
    add: vi.fn(),
    remove: vi.fn(),
  },
  messagesAPI: {
    send: vi.fn(),
    inbox: vi.fn(),
    outbox: vi.fn(),
  },
}))

function AppForLogoutTest() {
  const [currentUser, setCurrentUser] = useState(null)
  
  const handleLogin = (username) => {
    setCurrentUser(username)
  }
  
  const handleLogout = () => {
    setCurrentUser(null)
  }
  
  return (
    <MemoryRouter initialEntries={currentUser ? ['/dashboard'] : ['/login']}>
      <Routes>
        <Route 
          path="/login" 
          element={!currentUser ? <LoginForm onLogin={handleLogin} /> : <Navigate to="/dashboard" replace />}
        />
        <Route 
          path="/dashboard" 
          element={currentUser ? <Dashboard username={currentUser} onLogout={handleLogout} /> : <Navigate to="/login" replace />}
        />
      </Routes>
    </MemoryRouter>
  )
}

describe('Dashboard Logout Flow', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  test('logout button is rendered in dashboard', async () => {
    apiUtils.authAPI.login.mockResolvedValue({ 
      data: { message: 'Login successful', user: { username: 'testuser' } } 
    })
    
    render(<AppForLogoutTest />)
    
    // Login first
    const usernameInput = screen.getByPlaceholderText('Username')
    const passwordInput = screen.getByPlaceholderText('Password')
    const loginButton = screen.getByRole('button', { name: /login/i })
    
    await act(async () => {
      fireEvent.change(usernameInput, { target: { value: 'testuser' } })
      fireEvent.change(passwordInput, { target: { value: 'testpass' } })
      fireEvent.click(loginButton)
    })
    
    // Verify user info is displayed
    await waitFor(() => {
      expect(screen.getByText('testuser')).toBeInTheDocument()
    })
    
    // Verify logout button exists
    expect(screen.getByRole('button', { name: /Logout/i })).toBeInTheDocument()
  })

  test('logout calls authAPI.logout to clear cookie on backend', async () => {
    apiUtils.authAPI.login.mockResolvedValue({ 
      data: { message: 'Login successful', user: { username: 'testuser' } } 
    })
    apiUtils.authAPI.logout.mockResolvedValue({ 
      data: { message: 'Logged out successfully' } 
    })
    
    render(<AppForLogoutTest />)
    
    // Login
    await act(async () => {
      fireEvent.change(screen.getByPlaceholderText('Username'), { target: { value: 'testuser' } })
      fireEvent.change(screen.getByPlaceholderText('Password'), { target: { value: 'testpass' } })
      fireEvent.click(screen.getByRole('button', { name: /login/i }))
    })
    
    await waitFor(() => {
      expect(screen.getByText('testuser')).toBeInTheDocument()
    })
    
    // Logout
    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: /Logout/i }))
    })
    
    // Verify logout API was called (this clears the cookie on backend)
    expect(apiUtils.authAPI.logout).toHaveBeenCalled()
  })

  test('logout clears current user state', async () => {
    apiUtils.authAPI.login.mockResolvedValue({ 
      data: { message: 'Login successful', user: { username: 'testuser' } } 
    })
    apiUtils.authAPI.logout.mockResolvedValue({ 
      data: { message: 'Logged out successfully' } 
    })
    
    render(<AppForLogoutTest />)
    
    // Login
    await act(async () => {
      fireEvent.change(screen.getByPlaceholderText('Username'), { target: { value: 'testuser' } })
      fireEvent.change(screen.getByPlaceholderText('Password'), { target: { value: 'testpass' } })
      fireEvent.click(screen.getByRole('button', { name: /login/i }))
    })
    
    await waitFor(() => {
      expect(screen.getByText('testuser')).toBeInTheDocument()
    })
    
    // Click logout button - this should clear auth state
    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: /Logout/i }))
    })
    
    // After logout, auth state is cleared (user is null)
    // The app should show login form again
    await waitFor(() => {
      expect(screen.getByPlaceholderText('Username')).toBeInTheDocument()
    })
  })
})
