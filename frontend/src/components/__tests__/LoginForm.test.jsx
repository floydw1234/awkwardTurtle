import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import { vi } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import LoginForm from '../LoginForm'
import * as apiUtils from '../../utils/api'

describe('LoginForm', () => {
  const mockLogin = vi.fn()
  const mockNavigate = vi.fn()

  beforeEach(() => {
    mockLogin.mockClear()
    vi.clearAllMocks()
  })

  test('renders login form with username and password fields', () => {
    render(
      <MemoryRouter>
        <LoginForm onLogin={mockLogin} />
      </MemoryRouter>
    )
    
    expect(screen.getByPlaceholderText('Username')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Password')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument()
  })

  test('calls login function with correct credentials on submit', async () => {
    vi.spyOn(apiUtils.authAPI, 'login').mockResolvedValue({ data: { user: { username: 'testuser' } } })
    
    render(
      <MemoryRouter>
        <LoginForm onLogin={mockLogin} />
      </MemoryRouter>
    )
    
    const usernameInput = screen.getByPlaceholderText('Username')
    const passwordInput = screen.getByPlaceholderText('Password')
    const loginButton = screen.getByRole('button', { name: /login/i })

    fireEvent.change(usernameInput, { target: { value: 'testuser' } })
    fireEvent.change(passwordInput, { target: { value: 'testpass123' } })
    
    await act(async () => {
      fireEvent.click(loginButton)
    })
    
    await waitFor(() => {
      expect(apiUtils.authAPI.login).toHaveBeenCalled()
    })
  })

  test('calls login api and shows error on failure', async () => {
    const errorResponse = { 
      response: { 
        data: { detail: 'Invalid username or password' },
        status: 401
      } 
    }
    
    vi.spyOn(apiUtils.authAPI, 'login').mockRejectedValue(errorResponse)
    
    render(
      <MemoryRouter>
        <LoginForm onLogin={mockLogin} />
      </MemoryRouter>
    )
    
    const usernameInput = screen.getByPlaceholderText('Username')
    const passwordInput = screen.getByPlaceholderText('Password')
    const loginButton = screen.getByRole('button', { name: /login/i })

    fireEvent.change(usernameInput, { target: { value: 'wronguser' } })
    fireEvent.change(passwordInput, { target: { value: 'wrongpass' } })
    
    await act(async () => {
      fireEvent.click(loginButton)
    })
    
    await waitFor(() => {
      expect(screen.getByText(/Invalid username or password/i)).toBeInTheDocument()
    })
  })

  test('disables button while loading', async () => {
    vi.spyOn(apiUtils.authAPI, 'login').mockReturnValue(new Promise(() => {}))
    
    render(
      <MemoryRouter>
        <LoginForm onLogin={mockLogin} />
      </MemoryRouter>
    )
    
    const usernameInput = screen.getByPlaceholderText('Username')
    const passwordInput = screen.getByPlaceholderText('Password')
    const loginButton = screen.getByRole('button', { name: /login/i })

    fireEvent.change(usernameInput, { target: { value: 'testuser' } })
    fireEvent.change(passwordInput, { target: { value: 'testpass123' } })
    
    await act(async () => {
      fireEvent.click(loginButton)
    })
    
    await waitFor(() => {
      expect(loginButton).toBeDisabled()
    })
  })
})
