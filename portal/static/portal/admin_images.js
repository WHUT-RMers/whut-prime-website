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
  const shortenedName = (value) => value.length > 22 ? `${value.slice(0, 19)}…` : value
  const setupCarouselPicker = (input) => {
    if (input.dataset.carouselReady) return
    input.dataset.carouselReady = '1'
    const picker = document.createElement('div')
    picker.className = 'portal-carousel-picker'
    picker.innerHTML = '<p>一次可选择多张图片；在文件选择窗口按住 Ctrl 可多选。所有图片都是同一级别，保存后按这里的选择顺序依次轮播。</p><button type="button">一次选择多张图片</button><div class="portal-carousel-selection" aria-live="polite"></div>'
    input.insertAdjacentElement('afterend', picker)
    picker.querySelector('button').addEventListener('click', () => input.click())
    input.addEventListener('change', () => {
      const selection = picker.querySelector('.portal-carousel-selection')
      selection.innerHTML = ''
      Array.from(input.files || []).forEach((file, index) => {
        const card = document.createElement('figure')
        card.className = 'portal-carousel-card'
        const image = document.createElement('img')
        image.alt = `待上传轮播图 ${index + 1}`
        image.src = URL.createObjectURL(file)
        const caption = document.createElement('figcaption')
        caption.textContent = `图片 ${String(index + 1).padStart(2, '0')}  ${shortenedName(file.name)}`
        card.append(image, caption)
        selection.append(card)
      })
    })
  }
  document.querySelectorAll('.portal-carousel-input').forEach(setupCarouselPicker)
  document.querySelectorAll('input[type="file"][accept*="image"], input[type="file"]')
    .forEach((input) => {
      if (!input.classList.contains('portal-carousel-input') && (!input.accept || input.accept.includes('image'))) addPreview(input)
    })
})
