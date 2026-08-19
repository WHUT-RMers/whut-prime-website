document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.prime-richtext').forEach((wrapper) => {
    const textarea = document.querySelector(wrapper.dataset.target)
    const editor = wrapper.querySelector('.prime-richtext-editor')
    const sync = () => { textarea.value = editor.innerHTML }
    editor.addEventListener('input', sync)
    wrapper.querySelectorAll('button[data-command]').forEach((button) => {
      button.addEventListener('click', () => {
        editor.focus()
        document.execCommand(button.dataset.command, false, button.dataset.value || null)
        sync()
      })
    })
  })
})
