import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import { vi } from 'vitest'

import * as apiUtils from '../../utils/api'

vi.mock('../../utils/api', () => ({
  friendsAPI: {
    add: vi.fn(),
    remove: vi.fn(),
    get: vi.fn().mockResolvedValue({ data: { friends: [] } }),
  },
}))

import FriendsPage from '../FriendsPage'

describe('FriendsPage', () => {
  const mockFriends = [
    { username: 'friend1', id: 1 },
    { username: 'friend2', id: 2 },
  ]

  beforeEach(() => {
    vi.clearAllMocks()
  })

  test('renders add friend input and button', () => {
    render(<FriendsPage username="currentUser" />)
    
    expect(screen.getByPlaceholderText(/Enter username/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Add friend/i })).toBeInTheDocument()
  })

  test('calls add friend when button clicked', async () => {
    apiUtils.friendsAPI.add.mockResolvedValue({ data: { message: 'Added friend' } })
    
    render(<FriendsPage username="currentUser" />)
    
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Add friend/i })).toBeEnabled()
    })
    
    const input = screen.getByPlaceholderText(/Enter username/i)
    const addButton = screen.getByRole('button', { name: /Add friend/i })
    
    fireEvent.change(input, { target: { value: 'newfriend' } })
    
    await act(async () => {
      fireEvent.click(addButton)
    })
    
    await waitFor(() => {
      expect(apiUtils.friendsAPI.add).toHaveBeenCalledWith('newfriend')
    })
  })

  test('shows success message after adding friend', async () => {
    apiUtils.friendsAPI.add.mockResolvedValue({ data: { message: 'Added friend' } })
    
    render(<FriendsPage username="currentUser" />)
    
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Add friend/i })).toBeEnabled()
    })
    
    const input = screen.getByPlaceholderText(/Enter username/i)
    const addButton = screen.getByRole('button', { name: /Add friend/i })
    
    fireEvent.change(input, { target: { value: 'newfriend' } })
    
    await act(async () => {
      fireEvent.click(addButton)
    })
    
    await waitFor(() => {
      expect(screen.getByText(/Added 'newfriend' as friend/i)).toBeInTheDocument()
    })
  })

  test('shows error message when add friend fails', async () => {
    const errorResponse = {
      response: {
        data: { detail: "User 'nonexistent' not found" },
        status: 404
      }
    }
    apiUtils.friendsAPI.add.mockRejectedValue(errorResponse)
    
    render(<FriendsPage username="currentUser" />)
    
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Add friend/i })).toBeEnabled()
    })
    
    const input = screen.getByPlaceholderText(/Enter username/i)
    const addButton = screen.getByRole('button', { name: /Add friend/i })
    
    fireEvent.change(input, { target: { value: 'nonexistent' } })
    
    await act(async () => {
      fireEvent.click(addButton)
    })
    
    await waitFor(() => {
      expect(screen.getByText(/not found/i)).toBeInTheDocument()
    })
  })

  test('can remove friends', async () => {
    vi.stubGlobal('confirm', () => true)
    
    apiUtils.friendsAPI.get.mockResolvedValue({ data: { friends: ['friend1', 'friend2'] } })
    apiUtils.friendsAPI.remove.mockResolvedValue({ data: { message: 'Removed friend' } })
    
    render(<FriendsPage username="currentUser" />)
    
    await waitFor(() => {
      expect(screen.getByText('friend1')).toBeInTheDocument()
    })
    
    const removeBtn = screen.getAllByRole('button', { name: /Remove/i })[0]
    
    await act(async () => {
      removeBtn.click()
    })
    
    await waitFor(() => {
      expect(apiUtils.friendsAPI.remove).toHaveBeenCalledWith('friend1')
    })
  })

  test('displays friends correctly when API returns object array', async () => {
    apiUtils.friendsAPI.get.mockResolvedValue({ 
      data: { 
        friends: [
          { username: 'alice', id: 1 },
          { username: 'bob', id: 2 }
        ] 
      } 
    })
    
    render(<FriendsPage username="currentUser" />)
    
    await waitFor(() => {
      expect(screen.getByText('alice')).toBeInTheDocument()
      expect(screen.getByText('bob')).toBeInTheDocument()
    })
    
    expect(screen.queryByText('[object Object]')).not.toBeInTheDocument()
  })

  test('applies animate-pop class when friend is added successfully', async () => {
    apiUtils.friendsAPI.add.mockResolvedValue({ data: { message: 'Added friend' } })
    
    render(<FriendsPage username="currentUser" />)
    
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Add friend/i })).toBeEnabled()
    })
    
    const input = screen.getByPlaceholderText(/Enter username/i)
    const addButton = screen.getByRole('button', { name: /Add friend/i })
    
    fireEvent.change(input, { target: { value: 'newfriend' } })
    
    await act(async () => {
      fireEvent.click(addButton)
    })
    
    await waitFor(() => {
      expect(screen.getByText(/Added 'newfriend' as friend/i)).toBeInTheDocument()
    })
    
    const successMessage = screen.getByText(/Added 'newfriend' as friend/i)
    expect(successMessage).toHaveClass('animate-pop')
  })
})
