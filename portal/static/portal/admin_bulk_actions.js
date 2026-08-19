document.addEventListener('DOMContentLoaded', () => {
  const csrf = () => document.cookie.split('; ').find((v) => v.startsWith('csrftoken='))?.split('=')[1] || ''
  document.querySelectorAll('.portal-toolbar-button[data-url]').forEach((button) => {
    button.addEventListener('click', async () => {
      const ids = [...document.querySelectorAll('input.action-select:checked')].map((input) => input.value)
      if (!ids.length) { window.alert('请先勾选至少一篇资讯。'); return }
      if (!window.confirm(button.dataset.confirm || '确定执行此操作？')) return
      const data = new FormData(); ids.forEach((id) => data.append('ids', id))
      const result = await fetch(button.dataset.url, { method: 'POST', body: data, headers: { 'X-CSRFToken': csrf() } })
      if (result.redirected) window.location.assign(result.url)
      else window.location.reload()
    })
  })
  document.querySelectorAll('.portal-row-action').forEach((button) => {
    button.addEventListener('click', async () => {
      if (!window.confirm(button.dataset.confirm || '确定移入回收站？')) return
      const result = await fetch(button.dataset.url, { method: 'POST', headers: { 'X-CSRFToken': csrf() } })
      if (result.redirected) window.location.assign(result.url)
      else window.location.reload()
    })
  })
})
