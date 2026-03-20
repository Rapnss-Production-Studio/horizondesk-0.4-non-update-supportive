import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: './',  // relative paths for pywebview file:// loading
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
  }
})
