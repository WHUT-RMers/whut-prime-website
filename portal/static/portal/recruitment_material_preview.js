(function () {
  'use strict';

  function fileKind(name) {
    var extension = (name.split('.').pop() || '').toLowerCase();
    if (extension === 'pdf') return 'pdf';
    if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'].indexOf(extension) !== -1) return 'image';
    if (['mp4', 'mov', 'webm'].indexOf(extension) !== -1) return 'video';
    if (['mp3', 'wav', 'm4a'].indexOf(extension) !== -1) return 'audio';
    if (['txt', 'md', 'csv', 'json'].indexOf(extension) !== -1) return 'text';
    if (['docx', 'xlsx', 'pptx', 'zip'].indexOf(extension) !== -1) return 'structured';
    return 'other';
  }

  function addDownload(container, item) {
    var download = document.createElement('a');
    download.className = 'recruitment-preview-download';
    download.href = item.download;
    download.textContent = '下载此附件';
    container.appendChild(download);
  }

  function renderUnsupported(stage, item, message) {
    var empty = document.createElement('div');
    empty.className = 'recruitment-preview-empty';
    empty.innerHTML = '<span>FILE</span><strong></strong><p></p>';
    empty.querySelector('strong').textContent = item.name;
    empty.querySelector('p').textContent = message || '此文件暂不支持在线预览，请下载后查看。';
    addDownload(empty, item);
    stage.appendChild(empty);
  }

  function renderStructuredPreview(stage, item, data) {
    var wrapper = document.createElement('div');
    wrapper.className = 'recruitment-structured-preview';
    var title = document.createElement('h3');
    title.textContent = data.title || item.name;
    wrapper.appendChild(title);
    if (data.kind === 'document') {
      var documentText = document.createElement('article');
      documentText.className = 'recruitment-document-text';
      (data.paragraphs || []).forEach(function (paragraph) { var p = document.createElement('p'); p.textContent = paragraph; documentText.appendChild(p); });
      wrapper.appendChild(documentText);
    } else if (data.kind === 'spreadsheet') {
      (data.sheets || []).forEach(function (sheet) {
        var section = document.createElement('section');
        var heading = document.createElement('h4'); heading.textContent = sheet.name; section.appendChild(heading);
        var tableWrap = document.createElement('div'); tableWrap.className = 'recruitment-sheet-scroll';
        var table = document.createElement('table');
        (sheet.rows || []).forEach(function (row, index) { var tr = document.createElement('tr'); row.forEach(function (value) { var cell = document.createElement(index === 0 ? 'th' : 'td'); cell.textContent = value; tr.appendChild(cell); }); table.appendChild(tr); });
        tableWrap.appendChild(table); section.appendChild(tableWrap); wrapper.appendChild(section);
      });
    } else if (data.kind === 'presentation') {
      (data.slides || []).forEach(function (slide) { var card = document.createElement('section'); card.className = 'recruitment-slide-outline'; var heading = document.createElement('h4'); heading.textContent = '第 ' + slide.number + ' 页'; card.appendChild(heading); (slide.text || []).forEach(function (line) { var p = document.createElement('p'); p.textContent = line; card.appendChild(p); }); wrapper.appendChild(card); });
    } else if (data.kind === 'archive') {
      var note = document.createElement('p'); note.textContent = '压缩包内共 ' + (data.total || 0) + ' 个文件，以下展示前 300 个：'; wrapper.appendChild(note);
      var list = document.createElement('ul'); list.className = 'recruitment-archive-list'; (data.files || []).forEach(function (file) { var li = document.createElement('li'); li.textContent = file; list.appendChild(li); }); wrapper.appendChild(list);
    } else {
      renderUnsupported(stage, item, data.message); return;
    }
    addDownload(wrapper, item);
    stage.appendChild(wrapper);
  }

  function createModal() {
    var overlay = document.createElement('div');
    overlay.className = 'recruitment-preview-modal';
    overlay.setAttribute('role', 'dialog');
    overlay.setAttribute('aria-modal', 'true');
    overlay.setAttribute('aria-label', '报名材料预览');
    overlay.innerHTML =
      '<div class="recruitment-preview-panel">' +
        '<header><div><span class="recruitment-preview-kicker">报名材料</span><h2>附件预览</h2></div>' +
        '<button type="button" class="recruitment-preview-close" aria-label="关闭预览">×</button></header>' +
        '<div class="recruitment-preview-content"><aside class="recruitment-preview-list"></aside>' +
        '<section class="recruitment-preview-stage"></section></div>' +
      '</div>';
    document.body.appendChild(overlay);
    overlay.addEventListener('click', function (event) {
      if (event.target === overlay || event.target.closest('.recruitment-preview-close')) overlay.remove();
    });
    return overlay;
  }

  function showMaterial(modal, materials, activeIndex) {
    var list = modal.querySelector('.recruitment-preview-list');
    var stage = modal.querySelector('.recruitment-preview-stage');
    var item = materials[activeIndex];
    list.innerHTML = '';
    materials.forEach(function (material, index) {
      var button = document.createElement('button');
      button.type = 'button';
      button.className = index === activeIndex ? 'is-active' : '';
      button.textContent = material.name;
      button.addEventListener('click', function () { showMaterial(modal, materials, index); });
      list.appendChild(button);
    });
    stage.innerHTML = '';
    var kind = fileKind(item.name);
    if (kind === 'pdf') {
      var frame = document.createElement('iframe');
      frame.src = item.preview;
      frame.title = item.name;
      stage.appendChild(frame);
    } else if (kind === 'image') {
      var image = document.createElement('img');
      image.src = item.preview;
      image.alt = item.name;
      stage.appendChild(image);
    } else if (kind === 'video') {
      var video = document.createElement('video');
      video.src = item.preview;
      video.controls = true;
      video.preload = 'metadata';
      stage.appendChild(video);
    } else if (kind === 'audio') {
      var audio = document.createElement('audio');
      audio.src = item.preview;
      audio.controls = true;
      stage.appendChild(audio);
    } else if (kind === 'text') {
      var textPreview = document.createElement('pre');
      textPreview.className = 'recruitment-text-preview';
      textPreview.textContent = '正在读取文件…';
      stage.appendChild(textPreview);
      fetch(item.preview).then(function (response) { return response.text(); }).then(function (content) {
        textPreview.textContent = content.length > 1000000 ? content.slice(0, 1000000) + '\n\n… 已截取前 1 MB 内容 …' : content;
      }).catch(function () { textPreview.textContent = '文件读取失败，请下载后查看。'; });
    } else if (kind === 'structured' && item.dataPreview) {
      var loading = document.createElement('div'); loading.className = 'recruitment-preview-loading'; loading.textContent = '正在生成预览…'; stage.appendChild(loading);
      fetch(item.dataPreview).then(function (response) { return response.json(); }).then(function (data) { loading.remove(); renderStructuredPreview(stage, item, data); }).catch(function () { loading.remove(); renderUnsupported(stage, item, '预览生成失败，请下载后查看。'); });
    } else {
      renderUnsupported(stage, item);
    }
  }

  document.addEventListener('click', function (event) {
    var trigger = event.target.closest('.recruitment-preview-trigger');
    if (!trigger) return;
    event.preventDefault();
    try {
      var materials = JSON.parse(trigger.dataset.materials || '[]');
      if (!materials.length) return;
      var modal = createModal();
      showMaterial(modal, materials, 0);
      modal.querySelector('.recruitment-preview-close').focus();
    } catch (error) {
      window.alert('附件信息读取失败，请刷新页面后重试。');
    }
  });
}());
