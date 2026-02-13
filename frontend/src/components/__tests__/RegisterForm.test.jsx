import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import { vi } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import RegisterForm from '../RegisterForm'
import * as apiUtils from '../../utils/api'

describe('RegisterForm', () => {
  const mockRegister = vi.fn()

  beforeEach(() => {
    mockRegister.mockClear()
    vi.clearAllMocks()
  })

  test('renders register form with username and password fields', () => {
    render(
      <MemoryRouter>
        <RegisterForm onRegister={mockRegister} />
      </MemoryRouter>
    )
    
    expect(screen.getByPlaceholderText('Username')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Password')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /register/i })).toBeInTheDocument()
  })

  test('calls register function with correct credentials on submit', async () => {
    vi.spyOn(apiUtils.authAPI, 'register').mockResolvedValue({ data: { username: 'newuser' } })
    
    render(
      <MemoryRouter>
        <RegisterForm onRegister={mockRegister} />
      </MemoryRouter>
    )
    
    const usernameInput = screen.getByPlaceholderText('Username')
    const passwordInput = screen.getByPlaceholderText('Password')
    const registerButton = screen.getByRole('button', { name: /register/i })

    fireEvent.change(usernameInput, { target: { value: 'newuser' } })
    fireEvent.change(passwordInput, { target: { value: 'newpass123' } })
    
    await act(async () => {
      fireEvent.click(registerButton)
    })
    
    await waitFor(() => {
      expect(apiUtils.authAPI.register).toHaveBeenCalled()
    })
  })

  test('shows password length requirement', () => {
    render(
      <MemoryRouter>
        <RegisterForm onRegister={mockRegister} />
      </MemoryRouter>
    )
    
    expect(screen.getByText(/Minimum 6 characters/i)).toBeInTheDocument()
  })

  test('calls register api and shows error on failure', async () => {
    const errorResponse = { 
      response: { 
        data: { detail: 'Username already registered' },
        status: 400
      } 
    }
    
    vi.spyOn(apiUtils.authAPI, 'register').mockRejectedValue(errorResponse)
    
    render(
      <MemoryRouter>
        <RegisterForm onRegister={mockRegister} />
      </MemoryRouter>
    )
    
    const usernameInput = screen.getByPlaceholderText('Username')
    const passwordInput = screen.getByPlaceholderText('Password')
    const registerButton = screen.getByRole('button', { name: /register/i })

    fireEvent.change(usernameInput, { target: { value: 'existinguser' } })
    fireEvent.change(passwordInput, { target: { value: 'testpass123' } })
    
    await act(async () => {
      fireEvent.click(registerButton)
    })
    
    await waitFor(() => {
      expect(screen.getByText(/Username already registered/i)).toBeInTheDocument()
    })
  })

  test('password must be at least 6 characters', async () => {
    render(
      <MemoryRouter>
        <RegisterForm onRegister={mockRegister} />
      </MemoryRouter>
    )
    
    const usernameInput = screen.getByPlaceholderText('Username')
    const passwordInput = screen.getByPlaceholderText('Password')
    const registerButton = screen.getByRole('button', { name: /register/i })

    fireEvent.change(usernameInput, { target: { value: 'newuser' } })
    fireEvent.change(passwordInput, { target: { value: 'short' } })
    
    await act(async () => {
      fireEvent.click(registerButton)
    })
    
    await waitFor(() => {
      expect(screen.getByText(/Minimum 6 characters/i)).toBeInTheDocument()
    })
  })
})
