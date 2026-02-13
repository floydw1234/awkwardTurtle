import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import { vi } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import MessagesPage from '../MessagesPage'
import * as apiUtils from '../../utils/api'

describe('MessagesPage', () => {
  const mockFriends = [
    { username: 'friend1', id: 1 },
    { username: 'friend2', id: 2 },
  ]

  beforeEach(() => {
    vi.clearAllMocks()
  })

  test('renders messages page with friends list', async () => {
    vi.spyOn(apiUtils.friendsAPI, 'get').mockResolvedValue({ data: { friends: mockFriends } })
    
    render(
      <MemoryRouter>
        <MessagesPage username="currentUser" />
      </MemoryRouter>
    )
    
    await waitFor(() => {
      expect(screen.getByText(/Messages/i)).toBeInTheDocument()
    })
  })

  test('renders empty state when no friends', async () => {
    vi.spyOn(apiUtils.friendsAPI, 'get').mockResolvedValue({ data: { friends: [] } })
    
    render(
      <MemoryRouter>
        <MessagesPage username="currentUser" />
      </MemoryRouter>
    )
    
    await waitFor(() => {
      expect(screen.getByText(/No friends yet/i)).toBeInTheDocument()
    })
  })

  test('allows selecting a friend to start messaging', async () => {
    vi.spyOn(apiUtils.friendsAPI, 'get').mockResolvedValue({ data: { friends: mockFriends } })
    
    render(
      <MemoryRouter>
        <MessagesPage username="currentUser" />
      </MemoryRouter>
    )
    
    await waitFor(() => {
      expect(screen.getByText('friend1')).toBeInTheDocument()
      expect(screen.getByText('friend2')).toBeInTheDocument()
    })
  })

  test('calls API to send message when form submitted', async () => {
    vi.spyOn(apiUtils.friendsAPI, 'get').mockResolvedValue({ data: { friends: mockFriends } })
    vi.spyOn(apiUtils.messagesAPI, 'inbox').mockResolvedValue({ data: { messages: [] } })
    vi.spyOn(apiUtils.messagesAPI, 'send').mockResolvedValue({ data: { id: 3, content: 'Test message' } })
    
    render(
      <MemoryRouter>
        <MessagesPage username="currentUser" />
      </MemoryRouter>
    )
    
    await waitFor(() => {
      expect(screen.getByText('friend1')).toBeInTheDocument()
    })
    
    const friendElement = screen.getByText('friend1')
    
    await act(async () => {
      friendElement.click()
    })
    
    const input = screen.getByPlaceholderText(/Type a message/i)
    const sendButton = screen.getByRole('button', { name: /Send/i })
    
    fireEvent.change(input, { target: { value: 'Test message' } })
    fireEvent.click(sendButton)
    
    await waitFor(() => {
      expect(apiUtils.messagesAPI.send).toHaveBeenCalled()
    })
  })

  test('shows error message when send message fails', async () => {
    const errorResponse = {
      response: {
        data: { detail: 'User not found' },
        status: 404
      }
    }
    vi.spyOn(apiUtils.friendsAPI, 'get').mockResolvedValue({ data: { friends: mockFriends } })
    vi.spyOn(apiUtils.messagesAPI, 'inbox').mockResolvedValue({ data: { messages: [] } })
    vi.spyOn(apiUtils.messagesAPI, 'send').mockRejectedValue(errorResponse)
    
    render(
      <MemoryRouter>
        <MessagesPage username="currentUser" />
      </MemoryRouter>
    )
    
    await waitFor(() => {
      expect(screen.getByText('friend1')).toBeInTheDocument()
    })
    
    const friendElement = screen.getByText('friend1')
    
    await act(async () => {
      friendElement.click()
    })
    
    const input = screen.getByPlaceholderText(/Type a message/i)
    const sendButton = screen.getByRole('button', { name: /Send/i })
    
    fireEvent.change(input, { target: { value: 'Test message' } })
    fireEvent.click(sendButton)
    
    await waitFor(() => {
      expect(screen.getByText(/not found/i)).toBeInTheDocument()
    })
  })

  test('clears input after successful message send', async () => {
    vi.spyOn(apiUtils.friendsAPI, 'get').mockResolvedValue({ data: { friends: mockFriends } })
    vi.spyOn(apiUtils.messagesAPI, 'inbox').mockResolvedValue({ data: { messages: [] } })
    vi.spyOn(apiUtils.messagesAPI, 'send').mockResolvedValue({ data: { id: 3, content: 'Test message' } })
    
    render(
      <MemoryRouter>
        <MessagesPage username="currentUser" />
      </MemoryRouter>
    )
    
    await waitFor(() => {
      expect(screen.getByText('friend1')).toBeInTheDocument()
    })
    
    const friendElement = screen.getByText('friend1')
    
    await act(async () => {
      friendElement.click()
    })
    
    const input = screen.getByPlaceholderText(/Type a message/i)
    const sendButton = screen.getByRole('button', { name: /Send/i })
    
    fireEvent.change(input, { target: { value: 'Test message' } })
    fireEvent.click(sendButton)
    
    await waitFor(() => {
      expect(input).toHaveValue('')
    })
  })
})
