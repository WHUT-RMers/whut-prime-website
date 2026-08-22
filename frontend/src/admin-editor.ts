import {
  Autoformat,
  BlockQuote,
  Bold,
  ClassicEditor,
  Essentials,
  FontColor,
  Heading,
  Image,
  ImageCaption,
  ImageInsert,
  ImageResize,
  ImageStyle,
  ImageTextAlternative,
  ImageToolbar,
  ImageUpload,
  Italic,
  Link,
  List,
  Paragraph,
  PasteFromOffice,
  Plugin,
  RemoveFormat,
  Strikethrough,
  Underline,
} from 'ckeditor5'
import zhCn from 'ckeditor5/translations/zh-cn.js'
import 'ckeditor5/ckeditor5.css'
import './admin-editor.css'

const csrf = () => document.cookie.split('; ').find((item) => item.startsWith('csrftoken='))?.split('=')[1] || ''

class PrimeUploadAdapter {
  private controller = new AbortController()

  constructor(
    private loader: any,
    private uploadUrl: string,
    private articleId: string,
  ) {}

  upload() {
    return this.loader.file.then(async (file: File) => {
      const body = new FormData()
      body.append('image', file)
      if (this.articleId) body.append('article_id', this.articleId)
      const response = await fetch(this.uploadUrl, {
        method: 'POST',
        credentials: 'same-origin',
        headers: { 'X-CSRFToken': csrf() },
        body,
        signal: this.controller.signal,
      })
      const data = await response.json().catch(() => ({}))
      if (!response.ok) throw new Error(data.error || '图片上传失败，请检查格式、尺寸和文件大小。')
      if (!data.url) throw new Error('服务器没有返回图片地址，请刷新页面后重试。')
      return { default: data.url }
    })
  }

  abort() {
    this.controller.abort()
  }
}

function cleanText(html: string) {
  const box = document.createElement('div')
  box.innerHTML = html
  return (box.textContent || '').replace(/\s+/g, '')
}

type PreviewCover = { id?: string | number; url: string; caption?: string }

function parseSavedCovers(value: string | undefined): PreviewCover[] {
  try {
    const covers = JSON.parse(value || '[]')
    return Array.isArray(covers) ? covers.filter((cover) => typeof cover?.url === 'string' && cover.url) : []
  } catch {
    return []
  }
}

function bootEditor(workbench: HTMLElement) {
  const source = workbench.querySelector<HTMLTextAreaElement>('textarea')
  if (!source) return

  const uploadUrl = workbench.dataset.uploadUrl || ''
  const articleId = workbench.dataset.articleId || ''
  const previewBody = workbench.querySelector<HTMLElement>('[data-preview-body]')
  const previewTitle = workbench.querySelector<HTMLElement>('[data-preview-title]')
  const previewSummary = workbench.querySelector<HTMLElement>('[data-preview-summary]')
  const previewCategory = workbench.querySelector<HTMLElement>('[data-preview-category]')
  const previewDate = workbench.querySelector<HTMLElement>('[data-preview-date]')
  const previewCover = workbench.querySelector<HTMLElement>('[data-preview-cover]')
  const previewCoverStage = workbench.querySelector<HTMLElement>('[data-preview-cover-stage]')
  const previewCoverEmpty = workbench.querySelector<HTMLElement>('[data-preview-cover-empty]')
  const previewCoverControls = workbench.querySelector<HTMLElement>('[data-preview-cover-controls]')
  const previewCoverDots = workbench.querySelector<HTMLElement>('[data-preview-cover-dots]')
  const previewCoverCounter = workbench.querySelector<HTMLElement>('[data-preview-cover-counter]')
  const previewCoverCaption = workbench.querySelector<HTMLElement>('[data-preview-cover-caption]')
  const wordCount = workbench.querySelector<HTMLElement>('[data-word-count]')
  const readTime = workbench.querySelector<HTMLElement>('[data-read-time]')
  const savedCovers = parseSavedCovers(workbench.dataset.coverImages)
  let managedCovers: PreviewCover[] | null = null
  let activeCover = 0
  let coverTimer = 0

  const coverItems = () => managedCovers || savedCovers

  const stopCoverCarousel = () => {
    window.clearInterval(coverTimer)
    coverTimer = 0
  }

  const showCover = (index: number) => {
    const images = previewCoverStage?.querySelectorAll<HTMLElement>('.prime-preview-cover-image') || []
    const dots = previewCoverDots?.querySelectorAll<HTMLButtonElement>('button') || []
    if (!images.length) return
    activeCover = (index + images.length) % images.length
    images.forEach((image, imageIndex) => image.classList.toggle('is-active', imageIndex === activeCover))
    dots.forEach((dot, dotIndex) => {
      dot.classList.toggle('is-active', dotIndex === activeCover)
      dot.setAttribute('aria-current', dotIndex === activeCover ? 'true' : 'false')
    })
    if (previewCoverCounter) previewCoverCounter.textContent = `${String(activeCover + 1).padStart(2, '0')} / ${String(images.length).padStart(2, '0')}`
    const caption = coverItems()[activeCover]?.caption?.trim() || ''
    if (previewCoverCaption) {
      previewCoverCaption.textContent = caption
      previewCoverCaption.hidden = !caption
    }
  }

  const startCoverCarousel = () => {
    stopCoverCarousel()
    const covers = coverItems()
    if (covers.length < 2 || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
    coverTimer = window.setInterval(() => showCover(activeCover + 1), 5000)
  }

  const renderCoverPreview = () => {
    if (!previewCover || !previewCoverStage || !previewCoverDots || !previewCoverControls) return
    const covers = coverItems()
    stopCoverCarousel()
    previewCoverStage.replaceChildren()
    previewCoverDots.replaceChildren()
    previewCover.classList.toggle('is-empty', covers.length === 0)
    if (previewCoverEmpty) previewCoverEmpty.hidden = covers.length > 0
    previewCoverControls.hidden = covers.length < 2
    if (!covers.length && previewCoverCaption) previewCoverCaption.hidden = true
    activeCover = Math.min(activeCover, Math.max(0, covers.length - 1))

    covers.forEach((cover, index) => {
      const image = document.createElement('img')
      image.className = 'prime-preview-cover-image'
      image.src = cover.url
      image.alt = cover.caption || (index === 0 ? '文章封面预览' : `文章轮播封面 ${index + 1}`)
      previewCoverStage.append(image)

      const dot = document.createElement('button')
      dot.type = 'button'
      dot.setAttribute('aria-label', `查看第 ${index + 1} 张封面`)
      dot.addEventListener('click', () => {
        showCover(index)
        startCoverCarousel()
      })
      previewCoverDots.append(dot)
    })
    showCover(activeCover)
    startCoverCarousel()
  }

  const carouselChange = (event: Event) => {
    const detail = (event as CustomEvent<{ images?: PreviewCover[] }>).detail
    managedCovers = Array.isArray(detail?.images) ? detail.images : null
    renderCoverPreview()
  }
  document.addEventListener('prime:carousel-change', carouselChange)
  previewCover?.addEventListener('mouseenter', stopCoverCarousel)
  previewCover?.addEventListener('mouseleave', startCoverCarousel)
  previewCover?.addEventListener('focusin', stopCoverCarousel)
  previewCover?.addEventListener('focusout', startCoverCarousel)
  renderCoverPreview()
  class PrimeUploadAdapterPlugin extends Plugin {
    static get pluginName() {
      return 'PrimeUploadAdapterPlugin' as const
    }

    init() {
      this.editor.plugins.get('FileRepository').createUploadAdapter = (loader: any) => (
        new PrimeUploadAdapter(loader, uploadUrl, articleId)
      )
    }
  }

  ClassicEditor.create(source, {
    licenseKey: 'GPL',
    extraPlugins: [PrimeUploadAdapterPlugin],
    plugins: [
      Essentials, Autoformat, Paragraph, Heading, Bold, Italic, Underline, Strikethrough, FontColor,
      RemoveFormat, List, BlockQuote, Link, Image, ImageUpload, ImageInsert, ImageCaption,
      ImageResize, ImageStyle, ImageToolbar, ImageTextAlternative, PasteFromOffice,
    ],
    toolbar: {
      items: [
        'undo', 'redo', '|', 'heading', '|', 'bold', 'italic', 'underline', 'strikethrough',
        'fontColor', 'removeFormat', '|', 'bulletedList', 'numberedList', 'blockQuote', 'link', '|', 'insertImage',
      ],
      shouldNotGroupWhenFull: false,
    },
    heading: {
      options: [
        { model: 'paragraph', title: '正文', class: 'ck-heading_paragraph' },
        { model: 'heading2', view: 'h2', title: '一级小标题', class: 'ck-heading_heading2' },
        { model: 'heading3', view: 'h3', title: '二级小标题', class: 'ck-heading_heading3' },
      ],
    },
    fontColor: {
      columns: 5,
      documentColors: 0,
      colors: [
        { color: '#b6c0cf', label: '正文灰' },
        { color: '#2de2a6', label: '强调青绿' },
        { color: '#4da3ff', label: '辅助蓝' },
        { color: '#ffb45e', label: '提醒橙' },
        { color: '#ff6b6b', label: '警示红' },
      ],
    },
    image: {
      insert: { type: 'block', integrations: ['upload'] },
      upload: { types: ['jpeg', 'png', 'webp'] },
      resizeUnit: '%',
      resizeOptions: [
        { name: 'resizeImage:60', value: '60', label: '中图（正文宽度 60%）' },
        { name: 'resizeImage:100', value: '100', label: '通栏（正文宽度 100%）' },
        { name: 'resizeImage:original', value: null, label: '恢复原始比例' },
      ],
      toolbar: [
        'resizeImage', '|',
        'toggleImageCaption', 'imageTextAlternative',
      ],
    },
    link: {
      addTargetToExternalLinks: true,
      defaultProtocol: 'https://',
    },
    placeholder: '从这里开始写正文。可直接粘贴文字，也可以拖入或粘贴图片。',
    language: 'zh-cn',
    translations: [zhCn],
  }).then((editor: any) => {
    const titleInput = document.querySelector<HTMLInputElement>('#id_title')
    const summaryInput = document.querySelector<HTMLInputElement | HTMLTextAreaElement>('#id_summary')
    const categoryInput = document.querySelector<HTMLInputElement>('#id_category')
    const dateInput = document.querySelector<HTMLInputElement>('#id_published_at')

    const updatePreview = () => {
      const html = editor.getData()
      if (previewBody) previewBody.innerHTML = html || '<p class="prime-preview-empty">正文内容会实时显示在这里。</p>'
      if (previewTitle) previewTitle.textContent = titleInput?.value.trim() || '文章标题'
      if (previewSummary) previewSummary.textContent = summaryInput?.value.trim() || '文章摘要会显示在这里。'
      if (previewCategory) previewCategory.textContent = categoryInput?.value.trim() || '战队资讯'
      if (previewDate) previewDate.textContent = dateInput?.value ? dateInput.value.slice(0, 10).replaceAll('-', '.') : '预览状态'
      const length = cleanText(html).length
      if (wordCount) wordCount.textContent = `${length} 字`
      if (readTime) readTime.textContent = `约 ${Math.max(1, Math.ceil(length / 400))} 分钟`
    }

    let previewFrame = 0
    const schedulePreviewUpdate = () => {
      window.cancelAnimationFrame(previewFrame)
      previewFrame = window.requestAnimationFrame(updatePreview)
    }

    // CKEditor fires uploadComplete before its normal change:data cycle has
    // necessarily rendered the final image URL. Listen after the built-in low
    // priority handler, which is the point where `src` is guaranteed to exist.
    editor.plugins.get('ImageUploadEditing').on('uploadComplete', () => {
      schedulePreviewUpdate()
      window.setTimeout(updatePreview, 50)
    }, { priority: 'lowest' })

    editor.model.document.on('change:data', schedulePreviewUpdate)
    ;[titleInput, summaryInput, categoryInput, dateInput].forEach((input) => input?.addEventListener('input', updatePreview))
    source.form?.addEventListener('submit', () => editor.updateSourceElement())
    updatePreview()
  }).catch((error) => {
    console.error(error)
    workbench.classList.add('prime-editor-failed')
    window.alert('正文编辑器加载失败，请刷新页面后重试。')
  })

  const toggle = workbench.querySelector<HTMLButtonElement>('[data-preview-toggle]')
  toggle?.addEventListener('click', () => {
    const hidden = workbench.classList.toggle('preview-hidden')
    toggle.textContent = hidden ? '展开预览' : '收起预览'
  })
}

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll<HTMLElement>('.prime-editor-workbench').forEach(bootEditor)
})
