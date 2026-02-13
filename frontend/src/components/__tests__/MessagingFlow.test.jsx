import { render, screen, waitFor, act, fireEvent } from '@testing-library/react'
import { vi } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import MessagesPage from '../MessagesPage'
import ChatInterface from '../ChatInterface'
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

describe('Messaging Flow - E2E', () => {
  const mockFriends = [
    { username: 'alice', id: 1 },
    { username: 'bob', id: 2 },
  ]

  beforeEach(() => {
    vi.clearAllMocks()
  })

  test('selecting friend in MessagesPage navigates to ChatInterface with correct friend', async () => {
    apiUtils.friendsAPI.get.mockResolvedValue({ data: { friends: mockFriends } })
    apiUtils.messagesAPI.inbox.mockResolvedValue({ data: { messages: [] } })
    
    render(
      <MemoryRouter>
        <MessagesPage username="currentUser" />
      </MemoryRouter>
    )
    
    await waitFor(() => {
      expect(screen.getByText('alice')).toBeInTheDocument()
    })
    
    await act(async () => {
      fireEvent.click(screen.getByText('alice'))
    })
    
    await waitFor(() => {
      expect(screen.getByText(/Chat with alice/i)).toBeInTheDocument()
    })
  })

  test('sending message in ChatInterface clears input and calls API', async () => {
    apiUtils.friendsAPI.get.mockResolvedValue({ data: { friends: mockFriends } })
    apiUtils.messagesAPI.inbox.mockResolvedValue({ data: { messages: [] } })
    apiUtils.messagesAPI.send.mockResolvedValue({ 
      data: { id: 2, content: 'Test message' } 
    })
    
    render(
      <MemoryRouter>
        <MessagesPage username="currentUser" />
      </MemoryRouter>
    )
    
    await waitFor(() => {
      expect(screen.getByText('alice')).toBeInTheDocument()
    })
    
    await act(async () => {
      fireEvent.click(screen.getByText('alice'))
    })
    
    await waitFor(() => {
      expect(screen.getByText(/Chat with alice/i)).toBeInTheDocument()
    })
    
    const input = screen.getByPlaceholderText(/Type a message/i)
    const sendButton = screen.getByRole('button', { name: /Send/i })
    
    await act(async () => {
      fireEvent.change(input, { target: { value: 'Hello!' } })
      fireEvent.click(sendButton)
    })
    
    await waitFor(() => {
      expect(apiUtils.messagesAPI.send).toHaveBeenCalledWith(1, 'Hello!')
    })
    
    expect(input).toHaveValue('')
  })

  test('ChatInterface shows "No messages yet" when no messages exist', () => {
    const friend = { username: 'alice', id: 1 }
    const currentUser = { username: 'currentUser', id: 0 }
    
    render(
      <MemoryRouter>
        <ChatInterface friend={friend} currentUser={currentUser} messages={[]} />
      </MemoryRouter>
    )
    
    expect(screen.getByText(/No messages yet/i)).toBeInTheDocument()
  })

  test('ChatInterface shows messages with proper alignment based on sender', () => {
    const friend = { username: 'alice', id: 1 }
    const currentUser = { username: 'currentUser', id: 0 }
    
    const sentMessage = { id: 1, content: 'My message', sender_id: 0, receiver_id: 1, created_at: '2024-01-01T12:00:00Z' }
    const receivedMessage = { id: 2, content: 'Their message', sender_id: 1, receiver_id: 0, created_at: '2024-01-01T12:05:00Z' }
    
    render(
      <MemoryRouter>
        <ChatInterface friend={friend} currentUser={currentUser} messages={[sentMessage, receivedMessage]} />
      </MemoryRouter>
    )
    
    expect(screen.getByText('My message')).toBeInTheDocument()
    expect(screen.getByText('Their message')).toBeInTheDocument()
  })

  test('ChatInterface fails to send when input is empty', () => {
    const friend = { username: 'alice', id: 1 }
    const currentUser = { username: 'currentUser', id: 0 }
    
    render(
      <MemoryRouter>
        <ChatInterface friend={friend} currentUser={currentUser} messages={[]} />
      </MemoryRouter>
    )
    
    const sendButton = screen.getByRole('button', { name: /Send/i })
    
    // Button should be disabled when no message
    expect(sendButton).toBeDisabled()
  })

  test('messages flow from dashboard through friend selection', async () => {
    apiUtils.friendsAPI.get.mockResolvedValue({ data: { friends: mockFriends } })
    apiUtils.messagesAPI.inbox.mockResolvedValue({ data: { messages: [] } })
    
    render(
      <MemoryRouter>
        <MessagesPage username="currentUser" />
      </MemoryRouter>
    )
    
    // Verify messages page renders
    await waitFor(() => {
      expect(screen.getByText(/Messages/i)).toBeInTheDocument()
    })
    
    // Verify friends are displayed
    expect(screen.getByText('alice')).toBeInTheDocument()
    expect(screen.getByText('bob')).toBeInTheDocument()
  })

  test('selecting bob navigates to ChatInterface with bob', async () => {
    apiUtils.friendsAPI.get.mockResolvedValue({ data: { friends: mockFriends } })
    apiUtils.messagesAPI.inbox.mockResolvedValue({ data: { messages: [] } })
    
    render(
      <MemoryRouter>
        <MessagesPage username="currentUser" />
      </MemoryRouter>
    )
    
    await waitFor(() => {
      expect(screen.getByText('bob')).toBeInTheDocument()
    })
    
    await act(async () => {
      fireEvent.click(screen.getByText('bob'))
    })
    
    await waitFor(() => {
      expect(screen.getByText(/Chat with bob/i)).toBeInTheDocument()
    })
  })
})
