import { defineConfig } from 'vite'

export default defineConfig({
  publicDir: false, // 库构建不要复制 public/（避免 favicon 等误入编辑器目录）
  build: {
    outDir: '../portal/static/portal/editor',
    emptyOutDir: true,
    cssCodeSplit: false,
    lib: {
      entry: 'src/admin-editor.ts',
      name: 'PrimeNewsEditor',
      formats: ['iife'],
      fileName: () => 'prime-editor.js',
    },
    rollupOptions: {
      output: {
        assetFileNames: (asset) => asset.name?.endsWith('.css') ? 'prime-editor.css' : '[name][extname]',
      },
    },
  },
})
