# Task Plan: Notifications Page Implementation

## Executive Summary
**Ticket:** Add a page for notifications and the backend and db tables for that too  
**Status:** Backend/DB already implemented; Only frontend implementation and navigation integration required  
**Approach:** Test-Driven Development (TDD)

**Current State (verified):**
- ✅ Notifications table exists with schema in `init-db/01-schema.sql:27-36`
- ✅ SQLAlchemy Notification model in `backend/app/models/__init__.py:78-100`
- ✅ Notification API endpoints in `backend/app/api/notifications.py`
- ✅ Pydantic schemas in `backend/app/schemas/notification.py`
- ✅ API client in `frontend/src/utils/api.ts:32-34`
- ❌ **Missing:** NotificationsPage component
- ❌ **Missing:** Route in App.jsx
- ❌ **Missing:** Navigation badge in Dashboard.jsx

**Files to Touch:**
- `frontend/src/components/NotificationsPage.jsx` (**CREATE**)
- `frontend/src/App.jsx` (**MODIFY**)
- `frontend/src/components/Dashboard.jsx` (**MODIFY**)
- `frontend/src/components/__tests__/NotificationsPage.test.jsx` (**CREATE**)
- `frontend/src/components/__tests__/Dashboard.test.jsx` (**MODIFY**)

---

## PHASE 0: Verify Baseline

### Step 0.1: Run existing tests to establish baseline
```bash
cd frontend && npm test -- --passed
```
**Expected:** Tests pass, confirming existing functionality intact

---

## PHASE 1: Create NotificationsPage Component

### Step 1.1: TDD - Write failing test for NotificationsPage

**File:** `frontend/src/components/__tests__/NotificationsPage.test.jsx` (**CREATE NEW FILE**)

**Tests to write:**

1. **Test: Renders notifications heading**
   - Verifies page displays "Notifications" heading
   - Uses `@testing-library/react` and `MemoryRouter`

2. **Test: Renders empty state when no notifications**
   - Mocks `notificationsAPI.get` to return empty list
   - Asserts "No notifications yet" message appears

3. **Test: Renders notification list when notifications exist**
   - Mocks `notificationsAPI.get` to return sample notifications
   - Asserts notification items render with title, message, timestamp

4. **Test: Shows visual indicator for unread notifications**
   - Mocks notifications with `is_read: false`
   - Asserts unread indicator (dot/flag) is visible

5. **Test: Allows marking notification as read**
   - Mocks `notificationsAPI.get` (success response)
   - Clicks notification (assumes click handler implemented)
   - Asserts API call to mark as read is made

**Run test:**
```bash
cd frontend && npm test -- NotificationsPage.test.jsx
```
**Expected:** Tests fail with "NotificationsPage does not exist" errors

---

### Step 1.2: Implement NotificationsPage component

**File:** `frontend/src/components/NotificationsPage.jsx` (**CREATE NEW FILE**)

**Implementation plan:**

```jsx
import { useState, useEffect, useCallback } from 'react'
import { notificationsAPI } from '../utils/api'

function NotificationsPage({ username }) {
  const [notifications, setNotifications] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // Load notifications on mount
  const loadNotifications = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await notificationsAPI.get()
      setNotifications(response.data.notifications || [])
    } catch (err) {
      console.error('Failed to load notifications:', err)
      setError('Failed to load notifications')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadNotifications()
  }, [loadNotifications])

  const formatTime = useCallback((dateString) => {
    const date = new Date(dateString)
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }, [])

  const handleMarkAsRead = async (notificationId) => {
    try {
      await notificationsAPI.markAsRead(notificationId)
      // Refresh notifications list
      loadNotifications()
    } catch (err) {
      console.error('Failed to mark as read:', err)
    }
  }

  const renderNotificationItem = (notification) => {
    const isUnread = !notification.is_read
    return (
      <li 
        key={notification.id} 
        className={`notification ${isUnread ? 'unread' : 'read'}`}
        onClick={() => isUnread && handleMarkAsRead(notification.id)}
        role="button"
        tabIndex={0}
      >
        <div className="notification-header">
          <strong>{notification.title}</strong>
          {isUnread && <span className="unread-indicator" />}
        </div>
        <div className="notification-content">{notification.message}</div>
        <div className="notification-time">{formatTime(notification.created_at)}</div>
      </li>
    )
  }

  return (
    <div className="notifications-page">
      <h2>Notifications</h2>
      
      {error && <div className="error-message">{error}</div>}
      
      {loading && notifications.length === 0 ? (
        <p>Loading notifications...</p>
      ) : (
        <div className="notifications-list-section">
          {notifications.length === 0 ? (
            <p className="empty-state">No notifications yet.</p>
          ) : (
            <ul className="notifications-list">
              {notifications.map(renderNotificationItem)}
            </ul>
          )}
        </div>
      )}
    </div>
  )
}

export default NotificationsPage
```

**Run test:**
```bash
cd frontend && npm test -- NotificationsPage.test.jsx
```
**Expected:** All tests pass

---

### Step 1.3: Add CSS styles for notifications page

**File:** `frontend/src/index.css` (**MODIFY**)

**Add styles after existing component styles:**

```css
/* Notifications Page Styles */
.notifications-page {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.notifications-page h2 {
  margin-bottom: 24px;
  color: #333;
}

.notifications-list-section {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
}

.notifications-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.notifications-list .notification {
  display: flex;
  flex-direction: column;
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: background-color 0.2s;
}

.notifications-list .notification:hover {
  background-color: #f5f5f5;
}

.notifications-list .notification.read {
  background-color: #fafafa;
}

.notifications-list .notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.notifications-list .notification-header strong {
  color: #333;
  font-size: 16px;
}

.unread-indicator {
  width: 8px;
  height: 8px;
  background-color: #1976d2;
  border-radius: 50%;
  display: inline-block;
}

.notifications-list .notification-content {
  color: #666;
  font-size: 14px;
  margin-bottom: 4px;
}

.notifications-list .notification-time {
  color: #999;
  font-size: 12px;
}

.empty-state {
  padding: 40px 20px;
  text-align: center;
  color: #666;
}

.error-message {
  padding: 16px;
  background-color: #ffebee;
  color: #c62828;
  border-radius: 4px;
  margin-bottom: 16px;
}
```

**Run test:**
```bash
cd frontend && npm test -- NotificationsPage.test.jsx
```
**Expected:** All tests still pass (CSS changes don't affect tests)

---

## PHASE 2: Add Route to App.jsx

### Step 2.1: TDD - Write failing test for route

**File:** `frontend/src/__tests__/App.test.jsx` (**MODIFY** existing or create)

**Test to add:**
```jsx
test('renders NotificationsPage when routed to /notifications', async () => {
  render(
    <MemoryRouter initialEntries={['/notifications']}>
      <App />
    </MemoryRouter>
  )
  
  await waitFor(() => {
    expect(screen.getByRole('heading', { name: /notifications/i })).toBeInTheDocument()
  })
})
```

**Run test:**
```bash
cd frontend && npm test -- App.test.jsx
```
**Expected:** Test fails because `/notifications` route doesn't exist

---

### Step 2.2: Implement route in App.jsx

**File:** `frontend/src/App.jsx` (**MODIFY**)

**Changes to make:**

1. **Import NotificationsPage component** (line 8):
```jsx
import NotificationsPage from './components/NotificationsPage'
```

2. **Add route** (line 44, before closing Route tag):
```jsx
<Route path="notifications" element={<NotificationsPage username={currentUser} />} />
```

**Full updated App.jsx structure:**
```jsx
<Route 
  path="/dashboard" 
  element={currentUser ? <Dashboard username={currentUser} onLogout={handleLogout} /> : <Navigate to="/login" replace />}
>
  <Route index element={<Navigate to="/friends" replace />} />
  <Route path="friends" element={<FriendsPage username={currentUser} />} />
  <Route path="messages" element={<MessagesPage username={currentUser} />} />
  <Route path="notifications" element={<NotificationsPage username={currentUser} />} />
</Route>
```

**Run test:**
```bash
cd frontend && npm test -- App.test.jsx
```
**Expected:** Route test passes

**Run all tests:**
```bash
cd frontend && npm test
```
**Expected:** All tests pass

---

## PHASE 3: Add Navigation Badge to Dashboard

### Step 3.1: TDD - Write failing test for notification badge

**File:** `frontend/src/components/__tests__/Dashboard.test.jsx` (**MODIFY**)

**Test to add:**
```jsx
test('displays notification count badge', async () => {
  vi.spyOn(apiUtils.notificationsAPI, 'get').mockResolvedValue({
    data: { notifications: [{ id: 1, is_read: false }], total: 1 }
  })
  
  render(<Dashboard username="currentUser" onLogout={() => {}} />)
  
  // Badge should appear in secondary nav
  await waitFor(() => {
    expect(screen.getByText('1')).toBeInTheDocument()
  })
})
```

**Run test:**
```bash
cd frontend && npm test -- Dashboard.test.jsx
```
**Expected:** Test fails because badge doesn't exist

---

### Step 3.2: Implement notification badge in Dashboard

**File:** `frontend/src/components/Dashboard.jsx` (**MODIFY**)

**Changes to make:**

1. **Import notificationsAPI** (line 2):
```jsx
import { notificationsAPI } from '../utils/api'
```

2. **Add notification state and effect** (after useState line):
```jsx
const [unreadCount, setUnreadCount] = useState(0)

// Load notification count on mount
useEffect(() => {
  const loadNotificationCount = async () => {
    try {
      const response = await notificationsAPI.get()
      const notifications = response.data.notifications || []
      const unread = notifications.filter(n => !n.is_read).length
      setUnreadCount(unread)
    } catch (err) {
      console.error('Failed to load notification count:', err)
    }
  }
  
  loadNotificationCount()
}, [])
```

3. **Add notification badge to navigation** (line 33, modify Friends link):
```jsx
<Link to="/friends" className="nav-link">
  👥 Friends
  {unreadCount > 0 && (
    <span className="notification-badge">
      {unreadCount}
    </span>
  )}
</Link>
```

**Full updated Dashboard.jsx structure:**
```jsx
import { Link, Outlet } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { authAPI, notificationsAPI } from '../utils/api'

function Dashboard({ username, onLogout }) {
  const [currentUser, setCurrentUser] = useState(username)
  const [unreadCount, setUnreadCount] = useState(0)

  const handleLogout = async () => {
    try {
      await authAPI.logout()
      onLogout()
    } catch (err) {
      console.error('Logout failed:', err)
      onLogout()
    }
  }

  useEffect(() => {
    const loadNotificationCount = async () => {
      try {
        const response = await notificationsAPI.get()
        const notifications = response.data.notifications || []
        const unread = notifications.filter(n => !n.is_read).length
        setUnreadCount(unread)
      } catch (err) {
        console.error('Failed to load notification count:', err)
      }
    }
    
    loadNotificationCount()
  }, [])

  return (
    <div className="dashboard">
      <nav className="dashboard-nav">
        <h1 className="logo">Awkward Turtle</h1>
        <div className="user-info">
          <span className="username-display">
            Hello, <strong>{username}</strong>
          </span>
          <button onClick={handleLogout} className="logout-btn">
            Logout
          </button>
        </div>
      </nav>
      <div className="dashboard-content">
        <nav className="secondary-nav">
          <Link to="/friends" className="nav-link">
            👥 Friends
            {unreadCount > 0 && (
              <span className="notification-badge">
                {unreadCount}
              </span>
            )}
          </Link>
          <Link to="/messages" className="nav-link">
            💬 Messages
          </Link>
        </nav>
        <main className="main-content">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default Dashboard
```

**Run test:**
```bash
cd frontend && npm test -- Dashboard.test.jsx
```
**Expected:** Badge test passes

**Run all tests:**
```bash
cd frontend && npm test
```
**Expected:** All tests pass

---

### Step 3.3: Add badge styling

**File:** `frontend/src/App.css` (**MODIFY**)

**Add styles:**

```css
.notification-badge {
  background-color: #1976d2;
  color: white;
  border-radius: 50%;
  padding: 2px 6px;
  font-size: 11px;
  font-weight: bold;
  margin-left: 8px;
  min-width: 20px;
  text-align: center;
}
```

**Run test:**
```bash
cd frontend && npm test
```
**Expected:** All tests still pass

---

## PHASE 4: Verification and Final Checks

### Step 4.1: Manual testing checklist

**Backend API (already implemented, verify):**
```bash
# Start backend (in project root)
cd backend
# Start frontend
cd ../frontend && npm start
```

**Test endpoints:**
1. Login to app
2. Navigate to `/notifications` route
3. Verify empty state appears initially
4. Verify notifications fetch successfully
5. Click unread notification to mark as read
6. Check badge count updates

---

### Step 4.2: Lint and type-check

**Run lint:**
```bash
cd frontend && npm run lint
```

**Run type-check (if TypeScript config exists):**
```bash
cd frontend && npm run type-check
```

**Fix any issues found**

---

### Step 4.3: E2E test (optional but recommended)

**Test automation:**
```bash
cd frontend && npm test -- --coverage
```

**Verify coverage:**
- NotificationsPage: 90%+ coverage
- Routes: 80%+ coverage
- Badge component: 80%+ coverage

---

## Dependencies Summary

### Order of Work:
```
1. NotificationsPage.jsx (component)
   ├── NotificationsPage.test.jsx (test) ────┐
   └── index.css (styles) ────────────────────┤
                                              │
2. App.jsx (route)                           │
   ├── App.test.jsx (route test) ────────────┤
   └── Requires: NotificationsPage component │
                                              │
3. Dashboard.jsx (badge)                     │
   ├── Dashboard.test.jsx (badge test) ──────┤
   └── index.css/App.css (badge styles) ─────┘
```

### File Dependencies:
- **NotificationsPage.jsx** requires no other new files
- **App.jsx** requires NotificationsPage component
- **Dashboard.jsx** requires notificationsAPI (already exists)

### Test Dependencies:
- All tests use existing testing utilities (`@testing-library/react`, `vitest`)
- No new test dependencies required

---

## Rollback Plan

If issues arise:
1. All changes are **additive** - no breaking changes
2. Can revert git commits in any phase
3. Missing route fallback: `/notifications` will show 404 (graceful degradation)
4. Missing badge: Notifications page still accessible directly

**Revert commands (if needed):**
```bash
# Revert all changes
git checkout .

# Or revert specific phases
git revert <commit-hash>
```

---

## Notes

- **No backend changes required** - notification endpoints already implemented
- **No database migrations** - notifications table already in schema
- **Polling approach** every 3s acceptable for MVP (can upgrade to WebSockets later)
- **Unread count caching** in Dashboard state reduces API calls
- **CSS classes** follow existing naming conventions (lowercase, kebab-case)
