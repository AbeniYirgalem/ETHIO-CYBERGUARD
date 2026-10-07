import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  base: './', // Ensures assets load correctly on GitHub Pages and local builds
  build: {
    rollupOptions: {
      output: {
        manualChunks(id: string) {
          if (id.includes('node_modules')) {
            if (id.includes('lucide-react')) {
              return 'lucide'
            }
            if (id.includes('react') || id.includes('react-dom')) {
              return 'vendor'
            }
          }
        },
      },
    },
  },
})

