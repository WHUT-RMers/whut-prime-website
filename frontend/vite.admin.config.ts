import { defineConfig } from 'vite'

export default defineConfig({
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
