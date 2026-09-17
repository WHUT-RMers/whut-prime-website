import * as pdfjsLib from 'pdfjs-dist'
import workerSrc from 'pdfjs-dist/build/pdf.worker.mjs?url&no-inline'

pdfjsLib.GlobalWorkerOptions.workerSrc = workerSrc

declare global {
  interface Window {
    PrimePdfViewer?: {
      render: (container: HTMLElement, source: string, options?: ViewerOptions) => Promise<void>
    }
  }
}

type ViewerOptions = {
  title?: string
  download?: string
}

type IconName = 'sidebar' | 'previous' | 'next' | 'minus' | 'plus' | 'fit' | 'pen' | 'eraser' | 'print' | 'download'

type InkPoint = { x: number; y: number }
type InkStroke = { points: InkPoint[] }

const iconPaths: Record<IconName, string> = {
  sidebar: '<path d="M4 5h16M4 12h16M4 19h16" />',
  previous: '<path d="m15 18-6-6 6-6" />',
  next: '<path d="m9 18 6-6-6-6" />',
  minus: '<path d="M5 12h14" />',
  plus: '<path d="M12 5v14M5 12h14" />',
  fit: '<path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5" />',
  pen: '<path d="m4 20 4.2-1 9.9-9.9a2.1 2.1 0 0 0-3-3L5.2 16 4 20Z" /><path d="m13.8 7.2 3 3" />',
  eraser: '<path d="m7 19 9.8-9.8a2.1 2.1 0 0 0-3-3L4.8 15.2a2.1 2.1 0 0 0 0 3L7 20.4h9" />',
  print: '<path d="M6 9V4h12v5M6 17H4a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2h-2" /><path d="M6 14h12v7H6z" />',
  download: '<path d="M12 3v12m0 0 4-4m-4 4-4-4M5 21h14" />',
}

function svgIcon(name: IconName) {
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg')
  svg.classList.add('recruitment-pdf-icon')
  svg.setAttribute('viewBox', '0 0 24 24')
  svg.setAttribute('fill', 'none')
  svg.setAttribute('stroke', 'currentColor')
  svg.setAttribute('stroke-width', '1.8')
  svg.setAttribute('stroke-linecap', 'round')
  svg.setAttribute('stroke-linejoin', 'round')
  svg.setAttribute('aria-hidden', 'true')
  svg.innerHTML = iconPaths[name]
  return svg
}

function button(label: string, text: string, icon?: IconName) {
  const item = document.createElement('button')
  item.type = 'button'
  item.className = 'recruitment-pdf-control'
  item.setAttribute('aria-label', label)
  item.title = label
  if (icon) item.appendChild(svgIcon(icon))
  if (text) {
    const labelText = document.createElement('span')
    labelText.className = 'recruitment-pdf-control-text'
    labelText.textContent = text
    item.appendChild(labelText)
  }
  if (icon && !text) item.classList.add('is-icon-only')
  return item
}

function toolbarDivider() {
  const divider = document.createElement('span')
  divider.className = 'recruitment-pdf-divider'
  divider.setAttribute('aria-hidden', 'true')
  return divider
}

async function renderPage(
  page: pdfjsLib.PDFPageProxy,
  canvas: HTMLCanvasElement,
  targetWidth: number,
) {
  const baseViewport = page.getViewport({ scale: 1 })
  const scale = Math.max(0.12, targetWidth / baseViewport.width)
  const viewport = page.getViewport({ scale })
  const ratio = window.devicePixelRatio || 1
  const context = canvas.getContext('2d')
  if (!context) throw new Error('canvas is unavailable')
  canvas.width = Math.floor(viewport.width * ratio)
  canvas.height = Math.floor(viewport.height * ratio)
  canvas.style.width = `${Math.floor(viewport.width)}px`
  canvas.style.height = `${Math.floor(viewport.height)}px`
  context.setTransform(ratio, 0, 0, ratio, 0, 0)
  await page.render({ canvas, canvasContext: context, viewport }).promise
}

async function render(container: HTMLElement, source: string, options: ViewerOptions = {}) {
  container.innerHTML = ''
  const viewer = document.createElement('div')
  viewer.className = 'recruitment-pdf-viewer'
  const toolbar = document.createElement('div')
  toolbar.className = 'recruitment-pdf-toolbar'
  const title = document.createElement('strong')
  title.className = 'recruitment-pdf-title'
  title.textContent = options.title || 'PDF 文档'
  const pageInput = document.createElement('input')
  pageInput.className = 'recruitment-pdf-page-input'
  pageInput.type = 'number'
  pageInput.min = '1'
  pageInput.inputMode = 'numeric'
  pageInput.setAttribute('aria-label', '当前页码')
  const pageLabel = document.createElement('span')
  pageLabel.className = 'recruitment-pdf-page-label'
  const previous = button('上一页', '', 'previous')
  const next = button('下一页', '', 'next')
  const zoomOut = button('缩小', '', 'minus')
  const zoomIn = button('放大', '', 'plus')
  const fit = button('适合宽度', '', 'fit')
  const zoomLabel = document.createElement('span')
  zoomLabel.className = 'recruitment-pdf-zoom-label'
  zoomLabel.textContent = '100%'
  const thumbToggle = button('显示或隐藏缩略图', '', 'sidebar')
  thumbToggle.classList.add('recruitment-pdf-thumb-toggle')
  const annotateToggle = button('开启勾画', '', 'pen')
  annotateToggle.setAttribute('aria-pressed', 'false')
  const clearInk = button('清除勾画', '', 'eraser')
  clearInk.disabled = true
  const print = button('打印', '', 'print')
  toolbar.append(
    title,
    previous,
    pageInput,
    pageLabel,
    next,
    toolbarDivider(),
    zoomOut,
    zoomLabel,
    zoomIn,
    fit,
    toolbarDivider(),
    annotateToggle,
    clearInk,
    print,
  )
  toolbar.insertBefore(thumbToggle, title)
  if (options.download) {
    const download = document.createElement('a')
    download.className = 'recruitment-pdf-download'
    download.href = options.download
    download.setAttribute('aria-label', '下载')
    download.title = '下载'
    download.setAttribute('download', '')
    download.appendChild(svgIcon('download'))
    toolbar.appendChild(download)
  }
  const workspace = document.createElement('div')
  workspace.className = 'recruitment-pdf-workspace'
  const thumbnails = document.createElement('aside')
  thumbnails.className = 'recruitment-pdf-thumbnails'
  thumbnails.setAttribute('aria-label', '页面缩略图')
  const thumbnailList = document.createElement('div')
  thumbnailList.className = 'recruitment-pdf-thumbnail-list'
  thumbnails.appendChild(thumbnailList)
  const pageWrap = document.createElement('div')
  pageWrap.className = 'recruitment-pdf-page-wrap'
  const pageStack = document.createElement('div')
  pageStack.className = 'recruitment-pdf-pages'
  pageWrap.appendChild(pageStack)
  workspace.append(thumbnails, pageWrap)
  viewer.append(toolbar, workspace)
  container.appendChild(viewer)

  const loading = document.createElement('p')
  loading.className = 'recruitment-pdf-loading'
  loading.textContent = '正在打开排版预览…'
  pageWrap.appendChild(loading)

  const pdf = await pdfjsLib.getDocument({ url: source, withCredentials: true }).promise
  type PageView = {
    number: number
    page: pdfjsLib.PDFPageProxy
    frame: HTMLElement
    canvas: HTMLCanvasElement
    ink: HTMLCanvasElement
    strokes: InkStroke[]
    thumbnail: HTMLButtonElement
    thumbnailCanvas: HTMLCanvasElement
  }
  const pages: PageView[] = []
  let annotating = false
  let activeStroke: { view: PageView; stroke: InkStroke } | null = null
  for (let number = 1; number <= pdf.numPages; number += 1) {
    const page = await pdf.getPage(number)
    const baseViewport = page.getViewport({ scale: 1 })

    const thumbnail = document.createElement('button')
    thumbnail.type = 'button'
    thumbnail.className = 'recruitment-pdf-thumbnail'
    thumbnail.setAttribute('aria-label', `第 ${number} 页`)
    thumbnail.dataset.page = String(number)
    const thumbnailCanvas = document.createElement('canvas')
    thumbnailCanvas.className = 'recruitment-pdf-thumbnail-canvas'
    const thumbnailNumber = document.createElement('span')
    thumbnailNumber.className = 'recruitment-pdf-thumbnail-number'
    thumbnailNumber.textContent = String(number)
    thumbnail.append(thumbnailCanvas, thumbnailNumber)
    thumbnailList.appendChild(thumbnail)

    const frame = document.createElement('section')
    frame.className = 'recruitment-pdf-page'
    frame.dataset.page = String(number)
    frame.style.aspectRatio = `${baseViewport.width} / ${baseViewport.height}`
    const canvas = document.createElement('canvas')
    canvas.className = 'recruitment-pdf-canvas'
    const ink = document.createElement('canvas')
    ink.className = 'recruitment-pdf-ink'
    ink.setAttribute('aria-hidden', 'true')
    const placeholder = document.createElement('span')
    placeholder.className = 'recruitment-pdf-page-placeholder'
    placeholder.textContent = `正在加载第 ${number} 页…`
    frame.append(canvas, ink, placeholder)
    pageStack.appendChild(frame)

    pages.push({ number, page, frame, canvas, ink, strokes: [], thumbnail, thumbnailCanvas })
  }

  let currentPage = 1
  let zoom = 1
  pageInput.max = String(pdf.numPages)
  pageInput.value = '1'
  pageLabel.textContent = `/ ${pdf.numPages}`
  let paintToken = 0

  const resizeInk = (view: PageView) => {
    view.ink.width = view.canvas.width
    view.ink.height = view.canvas.height
    view.ink.style.width = view.canvas.style.width
    view.ink.style.height = view.canvas.style.height
  }

  const redrawInk = (view: PageView) => {
    const context = view.ink.getContext('2d')
    if (!context) return
    context.clearRect(0, 0, view.ink.width, view.ink.height)
    if (!view.strokes.length || !view.ink.width || !view.ink.height) return
    const lineWidth = Math.max(2, view.ink.width / Math.max(view.ink.clientWidth, 1) * 2.6)
    context.strokeStyle = '#e04444'
    context.lineWidth = lineWidth
    context.lineCap = 'round'
    context.lineJoin = 'round'
    view.strokes.forEach((stroke) => {
      if (!stroke.points.length) return
      context.beginPath()
      stroke.points.forEach((point, index) => {
        const x = point.x * view.ink.width
        const y = point.y * view.ink.height
        if (index === 0) context.moveTo(x, y)
        else context.lineTo(x, y)
      })
      context.stroke()
    })
  }

  const pointFromEvent = (event: PointerEvent, view: PageView): InkPoint => {
    const bounds = view.ink.getBoundingClientRect()
    return {
      x: Math.min(1, Math.max(0, (event.clientX - bounds.left) / Math.max(bounds.width, 1))),
      y: Math.min(1, Math.max(0, (event.clientY - bounds.top) / Math.max(bounds.height, 1))),
    }
  }

  const hasInk = () => pages.some((view) => view.strokes.length > 0)
  const updateInkControls = () => { clearInk.disabled = !hasInk() }

  const updateCurrentPage = (number: number) => {
    currentPage = Math.min(Math.max(number, 1), pdf.numPages)
    pageInput.value = String(currentPage)
    previous.disabled = currentPage <= 1
    next.disabled = currentPage >= pdf.numPages
    pages.forEach((view) => {
      const active = view.number === currentPage
      view.thumbnail.classList.toggle('is-active', active)
      view.thumbnail.setAttribute('aria-current', active ? 'page' : 'false')
    })
  }

  const scrollToPage = (number: number) => {
    const view = pages[number - 1]
    if (!view) return
    view.frame.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  pages.forEach((view) => {
    view.thumbnail.addEventListener('click', () => scrollToPage(view.number))
    view.ink.addEventListener('pointerdown', (event) => {
      if (!annotating) return
      event.preventDefault()
      view.ink.setPointerCapture(event.pointerId)
      const stroke: InkStroke = { points: [pointFromEvent(event, view)] }
      activeStroke = { view, stroke }
      view.strokes.push(stroke)
      redrawInk(view)
      updateInkControls()
    })
    view.ink.addEventListener('pointermove', (event) => {
      if (!annotating || !activeStroke || activeStroke.view !== view) return
      event.preventDefault()
      activeStroke.stroke.points.push(pointFromEvent(event, view))
      redrawInk(view)
    })
    const finishStroke = () => { activeStroke = null }
    view.ink.addEventListener('pointerup', finishStroke)
    view.ink.addEventListener('pointercancel', finishStroke)
    view.ink.addEventListener('lostpointercapture', finishStroke)
  })

  let scrollFrame = 0
  pageWrap.addEventListener('scroll', () => {
    if (scrollFrame) return
    scrollFrame = window.requestAnimationFrame(() => {
      scrollFrame = 0
      const target = pageWrap.getBoundingClientRect().top + 28
      let closest = pages[0]
      let distance = Number.POSITIVE_INFINITY
      pages.forEach((view) => {
        const nextDistance = Math.abs(view.frame.getBoundingClientRect().top - target)
        if (nextDistance < distance) {
          distance = nextDistance
          closest = view
        }
      })
      if (closest) updateCurrentPage(closest.number)
    })
  })

  const paint = async (only?: PageView) => {
    const token = ++paintToken
    const availableWidth = Math.max(pageWrap.clientWidth - 54, 320)
    const targetWidth = availableWidth * zoom
    const visiblePages = only ? [only] : pages
    for (const view of visiblePages) {
      if (token !== paintToken || !viewer.isConnected) return
      const placeholder = view.frame.querySelector<HTMLElement>('.recruitment-pdf-page-placeholder')
      if (placeholder) placeholder.hidden = false
      await renderPage(view.page, view.canvas, targetWidth)
      resizeInk(view)
      redrawInk(view)
      view.canvas.dataset.ready = 'true'
      if (placeholder) placeholder.hidden = true
    }
    updateCurrentPage(currentPage)
  }

  const paintThumbnails = async () => {
    const thumbWidth = Math.max(106, Math.min(148, thumbnails.clientWidth - 28))
    for (const view of pages) {
      if (!viewer.isConnected) return
      await renderPage(view.page, view.thumbnailCanvas, thumbWidth)
      view.thumbnailCanvas.dataset.ready = 'true'
    }
  }

  const printDocument = async () => {
    await paint()
    const printWindow = window.open('', '_blank')
    if (!printWindow) {
      window.print()
      return
    }
    const pageMarkup = pages.map((view) => {
      const image = view.canvas.toDataURL('image/png')
      const ink = view.strokes.length ? `<img src="${view.ink.toDataURL('image/png')}" alt="" />` : ''
      return `<section class="print-page"><img src="${image}" alt="" />${ink}</section>`
    }).join('')
    let printed = false
    const printNow = () => {
      if (printed) return
      printed = true
      printWindow.focus()
      printWindow.print()
      printWindow.close()
    }
    printWindow.document.open()
    printWindow.document.write(`<!doctype html><html><head><title>${options.title || 'PDF 文档'}</title><style>html,body{margin:0;background:#fff}.print-page{position:relative;display:block;width:100%;break-after:page}.print-page:last-child{break-after:auto}.print-page>img{display:block;width:100%;height:auto}.print-page>img+img{position:absolute;inset:0}</style></head><body>${pageMarkup}</body></html>`)
    printWindow.document.close()
    printWindow.addEventListener('load', printNow, { once: true })
    window.setTimeout(printNow, 300)
  }

  thumbToggle.addEventListener('click', () => {
    const hidden = viewer.classList.toggle('recruitment-pdf-thumbnails-hidden')
    thumbToggle.setAttribute('aria-expanded', hidden ? 'false' : 'true')
  })

  previous.addEventListener('click', () => { if (currentPage > 1) scrollToPage(currentPage - 1) })
  next.addEventListener('click', () => { if (currentPage < pdf.numPages) scrollToPage(currentPage + 1) })
  pageInput.addEventListener('change', () => {
    const value = Number(pageInput.value)
    if (Number.isFinite(value) && value >= 1 && value <= pdf.numPages) scrollToPage(value)
    else pageInput.value = String(currentPage)
  })
  annotateToggle.addEventListener('click', () => {
    annotating = !annotating
    viewer.classList.toggle('is-annotating', annotating)
    annotateToggle.setAttribute('aria-pressed', String(annotating))
    annotateToggle.setAttribute('aria-label', annotating ? '关闭勾画' : '开启勾画')
    annotateToggle.title = annotating ? '关闭勾画' : '开启勾画'
  })
  clearInk.addEventListener('click', () => {
    pages.forEach((view) => { view.strokes = []; redrawInk(view) })
    updateInkControls()
  })
  print.addEventListener('click', () => { void printDocument() })
  zoomOut.addEventListener('click', () => { zoom = Math.max(0.7, zoom - 0.1); zoomLabel.textContent = `${Math.round(zoom * 100)}%`; void paint() })
  zoomIn.addEventListener('click', () => { zoom = Math.min(1.8, zoom + 0.1); zoomLabel.textContent = `${Math.round(zoom * 100)}%`; void paint() })
  fit.addEventListener('click', () => { zoom = 1; zoomLabel.textContent = '100%'; void paint() })

  loading.hidden = false
  await paint(pages[0])
  loading.hidden = true
  updateCurrentPage(1)
  void paintThumbnails()
  void paint()
}

window.PrimePdfViewer = { render }
