(function () {
  'use strict';

  function extension(name) {
    var value = String(name || '').split(/[./\\]/).pop() || '';
    return value.toLowerCase().split('.').pop() || '';
  }

  function fileKind(name) {
    var suffix = extension(name);
    if (suffix === 'pdf') return 'pdf';
    if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'avif', 'svg'].indexOf(suffix) !== -1) return 'image';
    if (['mp4', 'mov', 'webm', 'm4v', 'ogv', 'avi', 'mkv'].indexOf(suffix) !== -1) return 'video';
    if (['mp3', 'wav', 'm4a', 'ogg', 'oga', 'flac', 'aac'].indexOf(suffix) !== -1) return 'audio';
    if (['txt', 'md', 'csv', 'json', 'log', 'xml', 'html', 'htm', 'css', 'js', 'ts', 'tsx', 'jsx', 'vue', 'yaml', 'yml', 'ini', 'toml', 'sql', 'py', 'java', 'c', 'cpp', 'h', 'sh', 'bat'].indexOf(suffix) !== -1) return 'text';
    if (suffix === 'zip') return 'archive';
    if (['doc', 'docx', 'docm', 'wps', 'rtf', 'odt', 'xls', 'xlsx', 'xlsm', 'et', 'ods', 'ppt', 'pptx', 'pptm', 'dps', 'odp'].indexOf(suffix) !== -1) return 'structured';
    return 'other';
  }

  function formatBytes(value) {
    var size = Number(value || 0);
    if (!size) return '—';
    if (size < 1024) return size + ' B';
    if (size < 1024 * 1024) return (size / 1024).toFixed(1) + ' KB';
    return (size / (1024 * 1024)).toFixed(1) + ' MB';
  }

  function displayKind(node) {
    if (node.folder) return '文件夹';
    var kind = fileKind(node.name);
    if (kind === 'archive') return '压缩包';
    if (kind === 'pdf') return 'PDF 文件';
    if (kind === 'image') return '图片';
    if (kind === 'video') return '视频';
    if (kind === 'audio') return '音频';
    if (kind === 'text') return '文本';
    if (kind === 'structured') {
      var suffix = extension(node.name);
      return ['xls', 'xlsx', 'xlsm', 'et', 'ods'].indexOf(suffix) !== -1 ? '表格' : ['ppt', 'pptx', 'pptm', 'dps', 'odp'].indexOf(suffix) !== -1 ? '演示文稿' : '文档';
    }
    if (kind === 'other') return extension(node.name) ? '.' + extension(node.name) + ' 文件' : '文件';
    return '文件';
  }

  function fileIconType(name) {
    var suffix = extension(name);
    if (['doc', 'docx', 'docm', 'wps', 'rtf', 'odt'].indexOf(suffix) !== -1) return 'word';
    if (suffix === 'pdf') return 'pdf';
    if (['xls', 'xlsx', 'xlsm', 'et', 'ods'].indexOf(suffix) !== -1) return 'excel';
    if (['ppt', 'pptx', 'pptm', 'dps', 'odp'].indexOf(suffix) !== -1) return 'powerpoint';
    if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'avif', 'svg'].indexOf(suffix) !== -1) return 'image';
    if (['mp4', 'mov', 'webm', 'm4v', 'ogv', 'avi', 'mkv'].indexOf(suffix) !== -1) return 'video';
    if (['mp3', 'wav', 'm4a', 'ogg', 'oga', 'flac', 'aac'].indexOf(suffix) !== -1) return 'audio';
    if (['txt', 'md', 'csv', 'json', 'log', 'xml', 'html', 'htm', 'css', 'js', 'ts', 'tsx', 'jsx', 'vue', 'yaml', 'yml', 'ini', 'toml', 'sql', 'py', 'java', 'c', 'cpp', 'h', 'sh', 'bat'].indexOf(suffix) !== -1) return 'text';
    return 'document';
  }

  function fileIconLabel(name) {
    var labels = {
      word: 'Word', pdf: 'PDF', excel: 'Excel', powerpoint: 'PPT',
      image: '图片', video: '视频', audio: '音频', text: '文本', document: '文件'
    };
    return labels[fileIconType(name)] || '文件';
  }

  function addDownload(container, item) {
    if (!item || !item.download) return;
    var download = document.createElement('a');
    download.className = 'recruitment-preview-download';
    download.href = item.download;
    download.textContent = '下载此文件';
    download.setAttribute('download', '');
    container.appendChild(download);
  }

  function renderLoading(stage, message) {
    stage.innerHTML = '';
    var loading = document.createElement('div');
    loading.className = 'recruitment-preview-loading';
    loading.textContent = message || '正在生成预览…';
    stage.appendChild(loading);
  }

  function renderUnsupported(stage, item, message) {
    stage.innerHTML = '';
    var empty = document.createElement('div');
    empty.className = 'recruitment-preview-empty';
    var badge = document.createElement('span'); badge.textContent = displayKind(item); empty.appendChild(badge);
    var title = document.createElement('strong'); title.textContent = item.name || '未命名文件'; empty.appendChild(title);
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

  function renderStructuredPreview(stage, item, data) {
    if (!data || data.kind === 'unsupported') {
      renderUnsupported(stage, item, data && data.message);
      return;
    }
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
    } else {
      renderUnsupported(stage, item, data.message || '该文件没有可读取的预览内容。');
      return;
    }
    addDownload(wrapper, item);
    stage.innerHTML = '';
    stage.appendChild(wrapper);
  }

  function renderImagePreview(stage, node) {
    stage.innerHTML = '';
    var wrapper = document.createElement('div'); wrapper.className = 'recruitment-image-preview';
    var image = document.createElement('img'); image.src = node.preview; image.alt = node.name; wrapper.appendChild(image);
    stage.appendChild(wrapper); addDownload(stage, node);
  }

  function renderPdfPreview(stage, node, source, state, renderId) {
    if (window.PrimePdfViewer && typeof window.PrimePdfViewer.render === 'function') {
      window.PrimePdfViewer.render(stage, source, { title: node.name, download: node.download }).catch(function () {
        if (renderId === state.renderId) renderUnsupported(stage, node, 'PDF 排版预览失败，请下载后查看。');
      });
      return;
    }
    var frame = document.createElement('iframe'); frame.src = source; frame.title = node.name; stage.appendChild(frame); addDownload(stage, node);
  }

  function makeNode(item, key, parent, folder) {
    var node = Object.assign({}, item || {});
    node.key = key;
    node.parent = parent || null;
    node.folder = Boolean(folder);
    node.archive = !node.folder && fileKind(node.name) === 'archive';
    node.children = node.children || [];
    node.expanded = false;
    node.loaded = Boolean(node.loaded);
    node.loading = false;
    node.label = node.label || node.name || '未命名文件';
    return node;
  }

  function buildArchiveChildren(archiveNode, data) {
    var files = Array.isArray(data && data.files) ? data.files : [];
    var paths = files.map(function (file) { return String(file.path || file.name || ''); }).filter(Boolean);
    var firstParts = paths.map(function (path) { return path.split('/')[0]; });
    var sharedRoot = firstParts.length > 1 && firstParts.every(function (part) { return part === firstParts[0]; }) && paths.some(function (path) { return path.indexOf('/') !== -1; });
    var folders = {};
    archiveNode.children = [];

    function folderNode(parent, segment, depthKey) {
      var folderKey = parent.key + ':dir:' + depthKey;
      if (!folders[folderKey]) {
        folders[folderKey] = makeNode({ name: segment, label: segment }, folderKey, parent, true);
        parent.children.push(folders[folderKey]);
      }
      return folders[folderKey];
    }

    files.forEach(function (file, index) {
      var fullPath = String(file.path || file.name || '');
      var parts = fullPath.split('/').filter(Boolean);
      if (sharedRoot && parts.length > 1 && parts[0] === firstParts[0]) parts.shift();
      if (!parts.length) parts = [file.name || fullPath || ('文件 ' + (index + 1))];
      var parent = archiveNode;
      var pathKey = '';
      parts.slice(0, -1).forEach(function (part) {
        pathKey += '/' + part;
        parent = folderNode(parent, part, pathKey);
      });
      var leaf = makeNode(Object.assign({}, file, { name: file.name || parts[parts.length - 1], label: parts[parts.length - 1], path: fullPath }), archiveNode.key + ':file:' + index, parent, false);
      parent.children.push(leaf);
    });
    archiveNode.archiveTotal = Number(data && data.total) || files.length;
    archiveNode.loaded = true;
  }

  function createModal() {
    var overlay = document.createElement('div');
    overlay.className = 'recruitment-preview-modal';
    overlay.setAttribute('role', 'dialog'); overlay.setAttribute('aria-modal', 'true'); overlay.setAttribute('aria-labelledby', 'recruitment-preview-title'); overlay.tabIndex = -1;
    overlay.innerHTML =
      '<div class="recruitment-preview-panel">' +
        '<header><div><h2 id="recruitment-preview-title">报名材料预览</h2></div>' +
        '<button type="button" class="recruitment-preview-close" aria-label="关闭预览">×</button></header>' +
        '<div class="recruitment-preview-content"><aside class="recruitment-preview-list" aria-label="报名材料文件树"></aside><section class="recruitment-preview-stage" aria-live="polite"></section></div>' +
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

  function renderFolderState(stage, node) {
    stage.innerHTML = '';
    var empty = document.createElement('div'); empty.className = 'recruitment-preview-empty';
    var badge = document.createElement('span'); badge.textContent = node.archive ? 'ZIP' : 'DIR'; empty.appendChild(badge);
    var title = document.createElement('strong'); title.textContent = node.name; empty.appendChild(title);
    stage.appendChild(empty);
  }

  function renderTree(list, roots, state) {
    list.innerHTML = '';
    var tree = document.createElement('div'); tree.className = 'recruitment-file-tree'; tree.setAttribute('role', 'tree');

    function renderNodes(container, nodes, depth) {
      nodes.forEach(function (node) {
        var row = document.createElement('div'); row.className = 'recruitment-tree-row'; row.setAttribute('role', 'treeitem'); row.setAttribute('aria-level', String(depth + 1));
        var isBranch = node.folder || node.archive;
        if (isBranch) {
          var toggle = document.createElement('button'); toggle.type = 'button'; toggle.className = 'recruitment-tree-toggle';
          toggle.setAttribute('aria-label', (node.expanded ? '收起 ' : '展开 ') + node.name); toggle.setAttribute('aria-expanded', node.expanded ? 'true' : 'false');
          toggle.style.setProperty('--tree-indent', String(depth * 16) + 'px');
          var chevron = document.createElement('span'); chevron.className = 'recruitment-tree-chevron'; chevron.textContent = node.expanded ? '▾' : '▸'; toggle.appendChild(chevron);
          toggle.addEventListener('click', function () { toggleNode(node); }); row.appendChild(toggle);
        } else {
          var spacer = document.createElement('span'); spacer.className = 'recruitment-tree-spacer'; spacer.style.setProperty('--tree-indent', String(depth * 16) + 'px'); row.appendChild(spacer);
        }
        var button = document.createElement('button'); button.type = 'button'; button.className = 'recruitment-tree-button' + (state.selected === node ? ' is-active' : '') + (isBranch ? ' is-branch' : '');
        button.style.setProperty('--tree-indent', String(depth * 16) + 'px'); button.setAttribute('aria-current', state.selected === node ? 'true' : 'false');
        var icon = document.createElement('span');
        var iconType = node.archive ? 'archive' : fileIconType(node.name);
        icon.className = 'recruitment-tree-icon ' + (node.archive ? 'is-archive' : isBranch ? 'is-folder' : 'is-file is-' + iconType);
        icon.title = displayKind(node);
        if (!node.folder) icon.setAttribute('data-label', node.archive ? 'zip' : fileIconLabel(node.name));
        icon.setAttribute('aria-hidden', 'true');
        button.appendChild(icon);
        var label = document.createElement('span'); label.className = 'recruitment-tree-label'; label.textContent = node.label; button.appendChild(label);
        if (node.loading) { var loading = document.createElement('small'); loading.className = 'recruitment-tree-meta'; loading.textContent = '读取中'; button.appendChild(loading); }
        else if (!node.folder && node.size) { var size = document.createElement('small'); size.className = 'recruitment-tree-meta'; size.textContent = formatBytes(node.size); button.appendChild(size); }
        button.addEventListener('click', function () { selectNode(node); }); row.appendChild(button); container.appendChild(row);
        if (isBranch && node.expanded) {
          var childContainer = document.createElement('div'); childContainer.className = 'recruitment-tree-children'; childContainer.setAttribute('role', 'group');
          if (node.loading) { var pending = document.createElement('p'); pending.className = 'recruitment-tree-pending'; pending.textContent = '正在读取目录…'; childContainer.appendChild(pending); }
          else if (!node.children.length) { var empty = document.createElement('p'); empty.className = 'recruitment-tree-pending'; empty.textContent = '目录为空'; childContainer.appendChild(empty); }
          else renderNodes(childContainer, node.children, depth + 1);
          container.appendChild(childContainer);
        }
      });
    }

    renderNodes(tree, roots, 0); list.appendChild(tree);

    function toggleNode(node) {
      state.selected = node;
      node.expanded = !node.expanded;
      if (node.expanded && node.archive && !node.loaded) {
        loadArchive(node);
      } else {
        renderTree(list, roots, state);
        renderFolderState(state.stage, node);
      }
    }

    function selectNode(node) {
      if (node.archive || node.folder) {
        toggleNode(node);
        return;
      }
      state.selected = node;
      renderTree(list, roots, state);
      renderFile(state.stage, node);
    }

    function loadArchive(node) {
      if (node.loading || node.loaded || !node.dataPreview) return;
      node.loading = true; renderTree(list, roots, state);
      fetch(node.dataPreview).then(function (response) {
        if (!response.ok) throw new Error('preview');
        return response.json();
      }).then(function (data) {
        if (data.kind !== 'archive') throw new Error('archive');
        buildArchiveChildren(node, data); node.expanded = true; node.loading = false; renderTree(list, roots, state);
        if (state.selected === node) renderFolderState(state.stage, node);
      }).catch(function () {
        node.loading = false; node.loaded = true; node.children = [];
        renderTree(list, roots, state);
        if (state.selected === node) renderUnsupported(state.stage, node, '压缩包目录读取失败，请下载后查看。');
      });
    }

    function renderFile(stage, node) {
      var kind = fileKind(node.name);
      var renderId = ++state.renderId;
      stage.innerHTML = '';
      if (kind === 'pdf') {
        renderPdfPreview(stage, node, node.preview, state, renderId); return;
      }
      if (kind === 'image') {
        renderImagePreview(stage, node); return;
      }
      if (kind === 'video') {
        var video = document.createElement('video'); video.src = node.preview; video.controls = true; video.preload = 'metadata'; stage.appendChild(video); addDownload(stage, node); return;
      }
      if (kind === 'audio') {
        var audio = document.createElement('audio'); audio.src = node.preview; audio.controls = true; audio.preload = 'metadata'; stage.appendChild(audio); addDownload(stage, node); return;
      }
      if (kind === 'text') {
        var textPreview = document.createElement('pre'); textPreview.className = 'recruitment-text-preview'; textPreview.textContent = '正在读取文件…'; stage.appendChild(textPreview); addDownload(stage, node);
        fetch(node.preview).then(function (response) { if (!response.ok) throw new Error('preview'); return response.text(); }).then(function (content) {
          if (renderId !== state.renderId) return;
          textPreview.textContent = content.length > 1000000 ? content.slice(0, 1000000) + '\n\n… 已截取前 1 MB 内容 …' : content;
        }).catch(function () { if (renderId === state.renderId) textPreview.textContent = '文件读取失败，请下载后查看。'; });
        return;
      }
      if (kind === 'structured' && node.renderedPreview) {
        renderPdfPreview(stage, node, node.renderedPreview, state, renderId);
        return;
      }
      if (kind === 'structured' && node.dataPreview) {
        renderLoading(stage);
        fetch(node.dataPreview).then(function (response) { if (!response.ok) throw new Error('preview'); return response.json(); }).then(function (data) {
          if (renderId !== state.renderId) return;
          renderStructuredPreview(stage, node, data);
        }).catch(function () { if (renderId === state.renderId) renderUnsupported(stage, node, '预览生成失败，请下载后查看。'); });
        return;
      }
      renderUnsupported(stage, node);
    }

    function firstLeaf(node) {
      if (!node.folder && !node.archive) return node;
      if (node.archive && !node.loaded) return null;
      for (var index = 0; index < node.children.length; index += 1) {
        var found = firstLeaf(node.children[index]);
        if (found) return found;
      }
      return null;
    }

    state.selectNode = selectNode;
    state.loadArchive = loadArchive;
    state.firstLeaf = firstLeaf;
  }

  function showMaterials(modal, materials) {
    var list = modal.querySelector('.recruitment-preview-list');
    var stage = modal.querySelector('.recruitment-preview-stage');
    var roots = materials.map(function (material, index) { return makeNode(material, 'material:' + index, null, false); });
    var state = { selected: null, stage: stage, renderId: 0, selectNode: null };
    renderTree(list, roots, state);
    var first = roots[0];
    if (!first) return;
    if (first.archive) {
      state.selected = first; first.expanded = true; renderTree(list, roots, state);
      state.loadArchive(first);
      var waitForArchive = function () {
        if (!first.loaded) { window.setTimeout(waitForArchive, 80); return; }
        var leaf = state.firstLeaf(first);
        if (leaf) state.selectNode(leaf); else state.selectNode(first);
      };
      waitForArchive();
    } else {
      state.selectNode(first);
    }
  }

  document.addEventListener('click', function (event) {
    var target = event.target instanceof Element ? event.target : null;
    var trigger = target && target.closest('.recruitment-preview-trigger');
    if (!trigger) return;
    event.preventDefault();
    try {
      var materials = JSON.parse(trigger.getAttribute('data-materials') || '[]');
      if (!materials.length) return;
      var modal = createModal(); showMaterials(modal, materials);
      modal.querySelector('.recruitment-preview-close').focus();
    } catch (error) {
      window.alert('附件信息读取失败，请刷新页面后重试。');
    }
  });
}());
