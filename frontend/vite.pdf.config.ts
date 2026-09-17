import { defineConfig } from 'vite'

export default defineConfig({
  base: '/static/portal/',
  publicDir: false,
  build: {
    outDir: '../portal/static/portal',
    emptyOutDir: false,
    // Keep PDF.js' worker as a real static module. Some browsers reject the
    // data URL produced by the default library build before PDF loading starts.
    assetsInlineLimit: 0,
    lib: {
      entry: 'src/recruitment-pdf-viewer.ts',
      name: 'PrimePdfViewer',
      formats: ['iife'],
      fileName: () => 'recruitment_pdf_viewer.js',
    },
  },
})
