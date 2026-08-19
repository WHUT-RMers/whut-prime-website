document.addEventListener('DOMContentLoaded', () => {
  const addPreview = (input) => {
    if (input.dataset.previewReady) return
    input.dataset.previewReady = '1'
    const preview = document.createElement('img')
    preview.className = 'portal-upload-preview'
    preview.alt = '所选图片预览'
    input.insertAdjacentElement('afterend', preview)
    input.addEventListener('change', () => {
      const file = input.files && input.files[0]
      if (!file) return
      preview.src = URL.createObjectURL(file)
      preview.style.display = 'block'
    })
  }
  document.querySelectorAll('input[type="file"][accept*="image"], input[type="file"]')
    .forEach((input) => { if (!input.accept || input.accept.includes('image')) addPreview(input) })
})
