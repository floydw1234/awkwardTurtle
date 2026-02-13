import { describe, it, expect } from 'vitest'

describe('API Configuration', () => {
  it('should be configured to use the correct backend port 8050', async () => {
    const expectedBaseURL = 'http://localhost:8050/api/v1'
    
    expect(import.meta.env.VITE_API_URL).toBeUndefined()
    
    const api = await import('./api')
    expect(api.default.defaults.baseURL).toBe(expectedBaseURL)
  })
})
