import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import { vi } from 'vitest'
import ChatInterface from '../ChatInterface'
import * as apiUtils from '../../utils/api'

describe('ChatInterface', () => {
  const mockFriend = { username: 'friend1', id: 1 }
  const mockMessages = [
    {
      id: 1,
      content: 'Hello!',
      sender_id: 1,
      receiver_id: 2,
      created_at: '2024-01-01T12:00:00Z',
      is_read: true,
    },
    {
      id: 2,
      content: 'How are you?',
      sender_id: 1,
      receiver_id: 2,
      created_at: '2024-01-01T12:05:00Z',
      is_read: false,
    },
  ]

  const mockCurrentUser = { username: 'currentUser', id: 2 }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  test('renders chat interface with friend name', () => {
    render(<ChatInterface friend={mockFriend} currentUser={mockCurrentUser} />)
    
    expect(screen.getByText(/Chat with friend1/i)).toBeInTheDocument()
  })

  test('renders message list', () => {
    render(
      <ChatInterface 
        friend={mockFriend} 
        currentUser={mockCurrentUser} 
        messages={mockMessages} 
      />
    )
    
    expect(screen.getByText('Hello!')).toBeInTheDocument()
    expect(screen.getByText('How are you?')).toBeInTheDocument()
  })

  test('renders empty message list when no messages', () => {
    render(<ChatInterface friend={mockFriend} currentUser={mockCurrentUser} messages={[]} />)
    
    expect(screen.getByText(/No messages yet/i)).toBeInTheDocument()
  })

  test('allows typing and sending messages', async () => {
    vi.spyOn(apiUtils.messagesAPI, 'send').mockResolvedValue({ 
      data: { id: 3, content: 'New message' } 
    })
    
    render(<ChatInterface friend={mockFriend} currentUser={mockCurrentUser} />)
    
    const input = screen.getByPlaceholderText(/Type a message/i)
    const sendButton = screen.getByRole('button', { name: /Send/i })
    
    fireEvent.change(input, { target: { value: 'New message' } })
    fireEvent.click(sendButton)
    
    await waitFor(() => {
      expect(apiUtils.messagesAPI.send).toHaveBeenCalled()
    })
  })

  test('shows errors when message fails to send', async () => {
    const errorResponse = {
      response: {
        data: { detail: 'Failed to send' },
        status: 500
      }
    }
    vi.spyOn(apiUtils.messagesAPI, 'send').mockRejectedValue(errorResponse)
    
    render(<ChatInterface friend={mockFriend} currentUser={mockCurrentUser} />)
    
    const input = screen.getByPlaceholderText(/Type a message/i)
    const sendButton = screen.getByRole('button', { name: /Send/i })
    
    fireEvent.change(input, { target: { value: 'Test' } })
    fireEvent.click(sendButton)
    
    await waitFor(() => {
      expect(screen.getByText(/Failed to send/i)).toBeInTheDocument()
    })
  })

  test('clears input after successful send', async () => {
    vi.spyOn(apiUtils.messagesAPI, 'send').mockResolvedValue({ 
      data: { id: 3, content: 'New message' } 
    })
    
    render(<ChatInterface friend={mockFriend} currentUser={mockCurrentUser} />)
    
    const input = screen.getByPlaceholderText(/Type a message/i)
    const sendButton = screen.getByRole('button', { name: /Send/i })
    
    fireEvent.change(input, { target: { value: 'Test message' } })
    fireEvent.click(sendButton)
    
    await waitFor(() => {
      expect(input).toHaveValue('')
    })
  })

  test('displays messages with proper alignment based on sender', () => {
    render(
      <ChatInterface 
        friend={mockFriend} 
        currentUser={mockCurrentUser} 
        messages={mockMessages} 
      />
    )
    
    expect(screen.getByText('Hello!')).toBeInTheDocument()
    expect(screen.getByText('How are you?')).toBeInTheDocument()
  })
})
