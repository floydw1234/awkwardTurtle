import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/test/setup.ts',
    css: true,
    environmentOptions: {
      jsdom: {
        customExportConditions: ['node', 'node-addons'],
      },
    },
  },
  server: {
    port: 3010,
    proxy: {
      '/api': {
        target: 'http://localhost:8050',
        changeOrigin: true,
      },
    },
  },
})
