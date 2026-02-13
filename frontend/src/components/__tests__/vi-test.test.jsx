import { describe, test, vi } from 'vitest'; describe('test', () => { test('vi is defined', () => { expect(typeof vi.fn).toBe('function'); }); });
