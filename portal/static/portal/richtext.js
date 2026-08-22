document.addEventListener('DOMContentLoaded', () => {
  const csrf = () => document.cookie.split('; ').find((item) => item.startsWith('csrftoken='))?.split('=')[1] || ''
  document.querySelectorAll('.prime-richtext').forEach((wrapper) => {
    const textarea = document.querySelector(wrapper.dataset.target)
    const editor = wrapper.querySelector('.prime-richtext-editor')
    let savedRange = null
    const sync = () => { textarea.value = editor.innerHTML }
    const rememberSelection = () => {
      const selection = window.getSelection()
      if (selection && selection.rangeCount && editor.contains(selection.anchorNode)) savedRange = selection.getRangeAt(0).cloneRange()
    }
    const restoreSelection = () => {
      if (!savedRange) return
      const selection = window.getSelection()
      selection.removeAllRanges(); selection.addRange(savedRange)
    }
    editor.addEventListener('input', sync)
    editor.addEventListener('keyup', rememberSelection)
    editor.addEventListener('mouseup', rememberSelection)
    editor.addEventListener('focus', rememberSelection)
    wrapper.querySelectorAll('button[data-command]').forEach((button) => {
      button.addEventListener('click', () => {
        editor.focus()
        restoreSelection()
        document.execCommand(button.dataset.command, false, button.dataset.value || null)
        sync()
        rememberSelection()
      })
    })
    const imageButton = wrapper.querySelector('.prime-richtext-image')
    const fileInput = wrapper.querySelector('.prime-richtext-file')
    imageButton.addEventListener('click', () => {
      rememberSelection()
      if (!imageButton.dataset.uploadUrl) { window.alert('请先保存这篇资讯，再把图片插入正文。'); return }
      fileInput.click()
    })
    fileInput.addEventListener('change', async () => {
      const files = Array.from(fileInput.files || [])
      if (!files.length) return
      imageButton.disabled = true
      const originalLabel = imageButton.textContent
      try {
        for (const file of files) {
          const formData = new FormData(); formData.append('image', file)
          const caption = window.prompt('图片说明（可留空）', '')
          if (caption) formData.append('caption', caption)
          const response = await fetch(imageButton.dataset.uploadUrl, { method: 'POST', credentials: 'same-origin', headers: { 'X-CSRFToken': csrf() }, body: formData })
          const data = await response.json().catch(() => ({}))
          if (!response.ok) throw new Error(data.error || '图片上传失败，请重试。')
          editor.focus(); restoreSelection()
          document.execCommand('insertHTML', false, data.html)
          editor.insertAdjacentHTML('beforeend', '<p><br></p>')
          sync(); rememberSelection()
        }
      } catch (error) { window.alert(error.message || '图片上传失败，请重试。') }
      finally { imageButton.disabled = false; imageButton.textContent = originalLabel; fileInput.value = '' }
    })
  })
})
