import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// base '/static/'：构建产物由 Django staticfiles 在 /static/ 下托管
export default defineConfig({
  plugins: [vue()],
  base: '/static/',
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
  server: {
    port: 5173,
  },
})
