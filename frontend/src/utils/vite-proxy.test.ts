import { describe, it, expect } from 'vitest'
import { readFileSync } from 'fs'

describe('Vite Configuration', () => {
  it('should proxy /api requests to the correct backend port 8050', () => {
    const viteConfigPath = './vite.config.js'
    const configContent = readFileSync(viteConfigPath, 'utf-8')
    
    expect(configContent).toContain('target:')
    expect(configContent).toContain('http://localhost:8050')
    expect(configContent).not.toContain('http://localhost:8000')
  })
})
