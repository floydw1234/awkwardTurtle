import { describe, test, expect, vi } from 'vitest'

describe('jest', () => {
  test('is defined', () => {
    expect(typeof vi.fn).toBe('function')
  })
})
