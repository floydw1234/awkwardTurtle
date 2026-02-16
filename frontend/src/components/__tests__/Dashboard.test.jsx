import { render, screen, waitFor, act } from '@testing-library/react'
import { vi } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import Dashboard from '../Dashboard'
import * as apiUtils from '../../utils/api'

describe('Dashboard', () => {
  test('renders dashboard with user info and logout button', () => {
    render(
      <MemoryRouter>
        <Dashboard username="testuser" onLogout={() => {}} />
      </MemoryRouter>
    )
    
    expect(screen.getByText('testuser')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /logout/i })).toBeInTheDocument()
  })

  test('calls onLogout when logout button clicked', async () => {
    vi.spyOn(apiUtils.authAPI, 'logout').mockResolvedValue({ data: { message: 'Logged out' } })
    
    const mockLogout = vi.fn()
    render(
      <MemoryRouter>
        <Dashboard username="testuser" onLogout={mockLogout} />
      </MemoryRouter>
    )
    
    const logoutButton = screen.getByRole('button', { name: /logout/i })
    
    await act(async () => {
      logoutButton.click()
    })
    
    await waitFor(() => {
      expect(mockLogout).toHaveBeenCalled()
    })
  })

  test('displays notification count badge', async () => {
    vi.spyOn(apiUtils.notificationsAPI, 'get').mockResolvedValue({
      data: { notifications: [{ id: 1, is_read: false }], total: 1 }
    })
    
    render(
      <MemoryRouter>
        <Dashboard username="testuser" onLogout={() => {}} />
      </MemoryRouter>
    )
    
    await waitFor(() => {
      expect(screen.getByText('1')).toBeInTheDocument()
    })
  })
})
