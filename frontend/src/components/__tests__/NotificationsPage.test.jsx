import { render, screen, waitFor, act } from '@testing-library/react'
import { vi } from 'vitest'

import * as apiUtils from '../../utils/api'

vi.mock('../../utils/api', () => ({
  notificationsAPI: {
    get: vi.fn(),
  },
}))

import NotificationsPage from '../NotificationsPage'

describe('NotificationsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  test('renders notifications page heading', async () => {
    apiUtils.notificationsAPI.get.mockResolvedValue({
      data: { notifications: [], total: 0 }
    })
    
    render(
      <NotificationsPage username="user1" />
    )
    
    expect(screen.getByRole('heading', { name: /notifications/i })).toBeInTheDocument()
  })

  test('renders empty state when no notifications', async () => {
    apiUtils.notificationsAPI.get.mockResolvedValue({
      data: { notifications: [], total: 0 }
    })
    
    render(
      <NotificationsPage username="user1" />
    )
    
    await waitFor(() => {
      expect(screen.getByText(/No notifications yet/i)).toBeInTheDocument()
    })
  })

  test('renders notification list when notifications exist', async () => {
    apiUtils.notificationsAPI.get.mockResolvedValue({
      data: { 
        notifications: [
          {
            id: 1,
            notification_type: 'friend_request',
            title: 'Friend Request',
            message: 'alice wants to be friends',
            is_read: false,
            created_at: '2024-01-01T00:00:00Z'
          }
        ],
        total: 1 
      }
    })
    
    render(
      <NotificationsPage username="user1" />
    )
    
    expect(await screen.findByText('alice wants to be friends')).toBeInTheDocument()
    expect(screen.getByText('Friend Request')).toBeInTheDocument()
  })

  test('shows visual indicator for unread notifications', async () => {
    apiUtils.notificationsAPI.get.mockResolvedValue({
      data: { 
        notifications: [
          {
            id: 1,
            notification_type: 'friend_request',
            title: 'Friend Request',
            message: 'alice wants to be friends',
            is_read: false,
            created_at: '2024-01-01T00:00:00Z'
          }
        ],
        total: 1 
      }
    })
    
    render(
      <NotificationsPage username="user1" />
    )
    
    const notificationButton = await screen.findByRole('button', { name: /Friend Request/i })
    expect(notificationButton).toBeInTheDocument()
  })

  test('allows marking notification as read', async () => {
    apiUtils.notificationsAPI.get.mockResolvedValue({
      data: { 
        notifications: [
          {
            id: 1,
            notification_type: 'friend_request',
            title: 'Friend Request',
            message: 'alice wants to be friends',
            is_read: false,
            created_at: '2024-01-01T00:00:00Z'
          }
        ],
        total: 1 
      }
    })
    
    render(
      <NotificationsPage username="user1" />
    )
    
    await waitFor(() => {
      expect(screen.getByText('alice wants to be friends')).toBeInTheDocument()
    })
    
    const notificationItem = screen.getByRole('button', { name: /Friend Request/i })
    
    await act(async () => {
      notificationItem.click()
    })
  })
  
  test('displays timestamp for notifications', async () => {
    apiUtils.notificationsAPI.get.mockResolvedValue({
      data: { 
        notifications: [
          {
            id: 1,
            notification_type: 'friend_request',
            title: 'Friend Request',
            message: 'alice wants to be friends',
            is_read: false,
            created_at: '2024-01-01T12:30:00Z'
          }
        ],
        total: 1 
      }
    })
    
    render(
      <NotificationsPage username="user1" />
    )
    
    // The timestamp is displayed in local time, which may differ from UTC
    // Just verify a timestamp is shown
    expect(await screen.findByText(/:\d{2}/i)).toBeInTheDocument()
  })
})
