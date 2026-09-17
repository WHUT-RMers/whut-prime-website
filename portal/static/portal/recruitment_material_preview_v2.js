(function () {
  'use strict';

  function fileKind(name) {
    var extension = (name.split('.').pop() || '').toLowerCase();
    if (extension === 'pdf') return 'pdf';
    if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'].indexOf(extension) !== -1) return 'image';
    if (['mp4', 'mov', 'webm'].indexOf(extension) !== -1) return 'video';
    if (['mp3', 'wav', 'm4a'].indexOf(extension) !== -1) return 'audio';
    if (['txt', 'md', 'csv', 'json', 'log', 'xml', 'html', 'css', 'js', 'ts'].indexOf(extension) !== -1) return 'text';
    if (['docx', 'xlsx', 'pptx', 'zip'].indexOf(extension) !== -1) return 'structured';
    return 'other';
  }

  function formatBytes(value) {
    var size = Number(value || 0);
    if (!size) return '—';
    if (size < 1024) return size + ' B';
    if (size < 1024 * 1024) return (size / 1024).toFixed(1) + ' KB';
    return (size / (1024 * 1024)).toFixed(1) + ' MB';
  }

  function addDownload(container, item) {
    if (!item.download) return;
    var download = document.createElement('a');
    download.className = 'recruitment-preview-download';
    download.href = item.download;
    download.textContent = '下载此文件';
    download.setAttribute('download', '');
    container.appendChild(download);
  }

  function renderUnsupported(stage, item, message) {
    var empty = document.createElement('div');
    empty.className = 'recruitment-preview-empty';
    var badge = document.createElement('span'); badge.textContent = 'FILE'; empty.appendChild(badge);
    var title = document.createElement('strong'); title.textContent = item.name; empty.appendChild(title);
    var note = document.createElement('p'); note.textContent = message || '此文件暂不支持在线预览，请下载后查看。'; empty.appendChild(note);
    addDownload(empty, item);
    stage.appendChild(empty);
  }

  function renderTable(wrapper, rows) {
    var tableWrap = document.createElement('div'); tableWrap.className = 'recruitment-sheet-scroll';
    var table = document.createElement('table');
    (rows || []).forEach(function (row, index) {
      var tr = document.createElement('tr');
      (row || []).forEach(function (value) {
        var cell = document.createElement(index === 0 ? 'th' : 'td');
        cell.textContent = value;
        tr.appendChild(cell);
      });
      table.appendChild(tr);
    });
    tableWrap.appendChild(table); wrapper.appendChild(tableWrap);
  }

  function renderStructuredPreview(stage, item, data, openEntry) {
    var wrapper = document.createElement('div');
    wrapper.className = 'recruitment-structured-preview';
    var title = document.createElement('h3'); title.textContent = data.title || item.name; wrapper.appendChild(title);
    if (data.kind === 'document') {
      var documentText = document.createElement('article'); documentText.className = 'recruitment-document-text';
      (data.paragraphs || []).forEach(function (paragraph) { var p = document.createElement('p'); p.textContent = paragraph; documentText.appendChild(p); });
      (data.tables || []).forEach(function (table) { renderTable(documentText, table.rows); });
      if (data.images && data.images.length) {
        var imageList = document.createElement('div'); imageList.className = 'recruitment-document-images';
        data.images.forEach(function (image) {
          var figure = document.createElement('figure');
          var preview = document.createElement('img'); preview.src = image.src; preview.alt = image.name || '文档图片'; figure.appendChild(preview);
          if (image.name) { var caption = document.createElement('figcaption'); caption.textContent = image.name; figure.appendChild(caption); }
          imageList.appendChild(figure);
        });
        documentText.appendChild(imageList);
      }
      if (!documentText.children.length) { var empty = document.createElement('p'); empty.textContent = '文档没有可读取的正文文本。'; documentText.appendChild(empty); }
      wrapper.appendChild(documentText);
    } else if (data.kind === 'spreadsheet') {
      (data.sheets || []).forEach(function (sheet) {
        var section = document.createElement('section');
        var heading = document.createElement('h4'); heading.textContent = sheet.name; section.appendChild(heading);
        renderTable(section, sheet.rows); wrapper.appendChild(section);
      });
    } else if (data.kind === 'presentation') {
      (data.slides || []).forEach(function (slide) {
        var card = document.createElement('section'); card.className = 'recruitment-slide-outline';
        var heading = document.createElement('h4'); heading.textContent = '第 ' + slide.number + ' 页'; card.appendChild(heading);
        (slide.text || []).forEach(function (line) { var p = document.createElement('p'); p.textContent = line; card.appendChild(p); });
        wrapper.appendChild(card);
      });
      if (!data.slides || !data.slides.length) { var noSlides = document.createElement('p'); noSlides.textContent = '演示文稿没有可读取的文字内容。'; wrapper.appendChild(noSlides); }
    } else if (data.kind === 'archive') {
      renderArchivePreview(wrapper, item, data, openEntry);
    } else {
      renderUnsupported(stage, item, data.message); return;
    }
    addDownload(wrapper, item);
    stage.appendChild(wrapper);
  }

  function renderArchivePreview(wrapper, archiveItem, data, openEntry) {
    var header = document.createElement('div'); header.className = 'recruitment-archive-header';
    var note = document.createElement('p'); note.textContent = '压缩包内共 ' + (data.total || 0) + ' 个文件，点击任意条目进入内容预览。'; header.appendChild(note);
    var hint = document.createElement('span'); hint.textContent = '支持 PDF、图片、音视频、文本及 Office 文件'; header.appendChild(hint);
    wrapper.appendChild(header);
    var list = document.createElement('div'); list.className = 'recruitment-archive-list';
    (data.files || []).forEach(function (file) {
      var button = document.createElement('button'); button.type = 'button'; button.className = 'recruitment-archive-entry';
      var icon = document.createElement('span'); icon.className = 'recruitment-file-icon'; icon.textContent = (file.kind || 'file').toUpperCase().slice(0, 4); button.appendChild(icon);
      var name = document.createElement('span'); name.className = 'recruitment-file-name'; name.textContent = file.path || file.name; button.appendChild(name);
      var size = document.createElement('small'); size.textContent = formatBytes(file.size); button.appendChild(size);
      button.addEventListener('click', function () { openEntry(file); });
      list.appendChild(button);
    });
    if (!data.files || !data.files.length) { var empty = document.createElement('p'); empty.textContent = '压缩包内没有可读取的文件。'; list.appendChild(empty); }
    wrapper.appendChild(list);
  }

  function showArchiveEntry(stage, archiveItem, file, renderFile) {
    stage.innerHTML = '';
    var back = document.createElement('button'); back.type = 'button'; back.className = 'recruitment-preview-back'; back.textContent = '← 返回压缩包目录';
    back.addEventListener('click', function () { renderFile(stage, archiveItem); });
    stage.appendChild(back);
    var content = document.createElement('div'); content.className = 'recruitment-preview-entry-stage'; stage.appendChild(content);
    renderFile(content, { name: file.path || file.name, preview: file.preview, dataPreview: file.dataPreview, download: file.download }, true);
  }

  function createModal() {
    var overlay = document.createElement('div');
    overlay.className = 'recruitment-preview-modal';
    overlay.setAttribute('role', 'dialog'); overlay.setAttribute('aria-modal', 'true'); overlay.setAttribute('aria-labelledby', 'recruitment-preview-title'); overlay.tabIndex = -1;
    overlay.innerHTML =
      '<div class="recruitment-preview-panel">' +
        '<header><div><span class="recruitment-preview-kicker">PRIME · MATERIAL REVIEW</span><h2 id="recruitment-preview-title">报名材料预览</h2><p class="recruitment-preview-subtitle">选择左侧文件，右侧即时查看内容</p></div>' +
        '<button type="button" class="recruitment-preview-close" aria-label="关闭预览">×</button></header>' +
        '<div class="recruitment-preview-content"><aside class="recruitment-preview-list" aria-label="报名材料列表"></aside><section class="recruitment-preview-stage" aria-live="polite"></section></div>' +
      '</div>';
    document.body.appendChild(overlay);
    document.body.classList.add('recruitment-preview-open');
    var close = function () { overlay.remove(); document.body.classList.remove('recruitment-preview-open'); document.removeEventListener('keydown', onKeyDown); };
    var onKeyDown = function (event) { if (event.key === 'Escape') close(); };
    overlay.addEventListener('click', function (event) {
      var target = event.target instanceof Element ? event.target : null;
      if (event.target === overlay || target && target.closest('.recruitment-preview-close')) close();
    });
    document.addEventListener('keydown', onKeyDown);
    overlay._close = close;
    return overlay;
  }

  function showMaterial(modal, materials, activeIndex) {
    var list = modal.querySelector('.recruitment-preview-list');
    var stage = modal.querySelector('.recruitment-preview-stage');
    var item = materials[activeIndex];
    if (!item) return;
    list.innerHTML = '';
    materials.forEach(function (material, index) {
      var button = document.createElement('button'); button.type = 'button'; button.className = index === activeIndex ? 'is-active' : '';
      button.setAttribute('aria-current', index === activeIndex ? 'true' : 'false');
      var name = document.createElement('strong'); name.textContent = material.name; button.appendChild(name);
      var meta = document.createElement('small'); meta.textContent = fileKind(material.name).toUpperCase(); button.appendChild(meta);
      button.addEventListener('click', function () { showMaterial(modal, materials, index); }); list.appendChild(button);
    });

    function renderFile(target, current, fromArchive) {
      target.innerHTML = '';
      var kind = fileKind(current.name);
      if (kind === 'pdf') {
        var frame = document.createElement('iframe'); frame.src = current.preview; frame.title = current.name; target.appendChild(frame);
      } else if (kind === 'image') {
        var image = document.createElement('img'); image.src = current.preview; image.alt = current.name; target.appendChild(image);
      } else if (kind === 'video') {
        var video = document.createElement('video'); video.src = current.preview; video.controls = true; video.preload = 'metadata'; target.appendChild(video);
      } else if (kind === 'audio') {
        var audio = document.createElement('audio'); audio.src = current.preview; audio.controls = true; target.appendChild(audio);
      } else if (kind === 'text') {
        var textPreview = document.createElement('pre'); textPreview.className = 'recruitment-text-preview'; textPreview.textContent = '正在读取文件…'; target.appendChild(textPreview);
        fetch(current.preview).then(function (response) { if (!response.ok) throw new Error('preview'); return response.text(); }).then(function (content) { textPreview.textContent = content.length > 1000000 ? content.slice(0, 1000000) + '\n\n… 已截取前 1 MB 内容 …' : content; }).catch(function () { textPreview.textContent = '文件读取失败，请下载后查看。'; });
      } else if (kind === 'structured' && current.dataPreview) {
        var loading = document.createElement('div'); loading.className = 'recruitment-preview-loading'; loading.textContent = '正在生成预览…'; target.appendChild(loading);
        fetch(current.dataPreview).then(function (response) { if (!response.ok) throw new Error('preview'); return response.json(); }).then(function (data) { loading.remove(); renderStructuredPreview(target, current, data, function (file) { showArchiveEntry(target, current, file, renderFile); }); }).catch(function () { loading.remove(); renderUnsupported(target, current, '预览生成失败，请下载后查看。'); });
      } else {
        renderUnsupported(target, current);
      }
      if (fromArchive && kind !== 'structured') addDownload(target, current);
    }

    renderFile(stage, item, false);
  }

  document.addEventListener('click', function (event) {
    var target = event.target instanceof Element ? event.target : null;
    var trigger = target && target.closest('.recruitment-preview-trigger');
    if (!trigger) return;
    event.preventDefault();
    try {
      var materials = JSON.parse(trigger.getAttribute('data-materials') || '[]');
      if (!materials.length) return;
      var modal = createModal(); showMaterial(modal, materials, 0);
      modal.querySelector('.recruitment-preview-close').focus();
    } catch (error) {
      window.alert('附件信息读取失败，请刷新页面后重试。');
    }
  });
}());


