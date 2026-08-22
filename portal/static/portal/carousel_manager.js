document.addEventListener('DOMContentLoaded', () => {
  const sourceInput = document.querySelector('.portal-carousel-input')
  if (!sourceInput) return

  const row = sourceInput.closest('.form-row')
  const help = row.querySelector('.help')
  sourceInput.style.display = 'none'

  const manager = document.createElement('div')
  manager.className = 'portal-carousel-manager'
  manager.innerHTML = '<div class="portal-carousel-slots" aria-label="轮播图片列表"></div><p class="portal-carousel-hint">每张图片都可以填写说明，留空则前台不显示图注。</p>'
  sourceInput.insertAdjacentElement('afterend', manager)
  if (help) help.style.display = 'none'
  const slots = manager.querySelector('.portal-carousel-slots')

  const parseSavedCovers = () => {
    try {
      const covers = JSON.parse(sourceInput.dataset.savedCovers || '[]')
      return Array.isArray(covers) ? covers : []
    } catch {
      return []
    }
  }

  const emitChange = () => {
    const images = Array.from(slots.querySelectorAll('.portal-carousel-upload-card')).map((card) => ({
      url: card.querySelector('img')?.src || '',
      caption: card.querySelector('.portal-carousel-caption')?.value.trim() || '',
    })).filter((image) => image.url)
    document.dispatchEvent(new CustomEvent('prime:carousel-change', { detail: { images } }))
  }

  const renumber = () => {
    slots.querySelectorAll('.portal-carousel-upload-card').forEach((card, index) => {
      const number = card.querySelector('.portal-carousel-number')
      if (number) number.textContent = `图片 ${String(index + 1).padStart(2, '0')}`
    })
  }

  const makeCaptionInput = (name, value = '') => {
    const input = document.createElement('input')
    input.type = 'text'
    input.className = 'portal-carousel-caption'
    input.name = name
    input.value = value
    input.maxLength = 160
    input.placeholder = '填写图片说明（选填）'
    input.setAttribute('aria-label', '图片说明')
    input.addEventListener('input', emitChange)
    return input
  }

  const makeCard = ({ url, caption = '', captionName, pending = false, fileInput = null }) => {
    const card = document.createElement('figure')
    card.className = 'portal-carousel-upload-card'
    card.dataset.pending = pending ? 'true' : 'false'

    const preview = document.createElement('img')
    preview.src = url
    preview.alt = '轮播图片预览'

    const details = document.createElement('figcaption')
    const number = document.createElement('span')
    number.className = 'portal-carousel-number'
    details.append(number, makeCaptionInput(captionName, caption))
    card.append(preview, details)

    if (pending && fileInput) {
      const remove = document.createElement('button')
      remove.type = 'button'
      remove.className = 'portal-carousel-remove'
      remove.title = '移除这张待上传图片'
      remove.setAttribute('aria-label', '移除这张待上传图片')
      remove.textContent = '×'
      remove.addEventListener('click', () => {
        URL.revokeObjectURL(url)
        fileInput.remove()
        card.remove()
        renumber()
        emitChange()
      })
      card.append(remove)
    }
    return card
  }

  const makeInput = () => {
    const input = sourceInput.cloneNode(false)
    input.value = ''
    input.removeAttribute('id')
    input.removeAttribute('aria-describedby')
    input.removeAttribute('data-saved-covers')
    input.multiple = false
    input.style.display = 'none'
    return input
  }

  const makeAddSlot = (input) => {
    const slot = document.createElement('button')
    slot.type = 'button'
    slot.className = 'portal-carousel-add'
    slot.setAttribute('aria-label', '添加一张轮播图片')
    slot.innerHTML = '<span>＋</span><small>添加图片</small>'
    slot.addEventListener('click', () => input.click())
    input.addEventListener('change', () => {
      const file = input.files && input.files[0]
      if (!file) return
      const objectUrl = URL.createObjectURL(file)
      const card = makeCard({
        url: objectUrl,
        captionName: 'carousel_upload_captions',
        pending: true,
        fileInput: input,
      })
      slot.replaceWith(card)
      slots.append(input)
      addEmptySlot()
      renumber()
      emitChange()
    }, { once: true })
    slots.append(slot)
  }

  const addEmptySlot = () => makeAddSlot(makeInput())

  parseSavedCovers().forEach((cover) => {
    const captionName = cover.id === 'cover'
      ? 'carousel_saved_caption_cover'
      : `carousel_saved_caption_${String(cover.id).replace('-', '_')}`
    slots.append(makeCard({ url: cover.url, caption: cover.caption || '', captionName }))
  })

  // The original Django field becomes the first hidden upload field. Every later
  // plus card uses another input with the same name, so Django receives all files.
  sourceInput.multiple = false
  makeAddSlot(sourceInput)
  renumber()
  emitChange()
})
