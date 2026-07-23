---
name: "agent_toolkit"
icon: "📦"
description: "Agent工具管理 - 查看、搜索、安装和卸载共享工具与技巧"
runtime: web
enabled: true
---

<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>📦 Agent Toolkit Manager</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  
  body {
    font-family: var(--q-sans, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif);
    background: var(--q-bg, #0f172a);
    color: var(--q-text, #e2e8f0);
    min-height: 100vh;
  }
  
  .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
  
  .header {
    background: var(--q-bg2, #1e293b);
    padding: 24px;
    border-radius: 12px;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border: 1px solid var(--q-border, #334155);
  }
  .header h1 { font-size: 24px; color: var(--q-text, #f8fafc); }
  .header h1 span { color: var(--q-blue, #38bdf8); }
  
  .search-box { position: relative; margin-bottom: 20px; }
  .search-box input {
    width: 100%;
    padding: 14px 20px 14px 48px;
    background: var(--q-bg2, #1e293b);
    border: 1px solid var(--q-border, #334155);
    border-radius: 10px;
    color: var(--q-text, #e2e8f0);
    font-size: 15px;
    outline: none;
    transition: border-color 0.2s;
  }
  .search-box input:focus { border-color: var(--q-blue, #38bdf8); }
  .search-box input::placeholder { color: var(--q-muted, #64748b); }
  .search-icon { position: absolute; left: 16px; top: 50%; transform: translateY(-50%); color: var(--q-muted, #64748b); font-size: 18px; }
  
  .tabs { display: flex; gap: 4px; margin-bottom: 20px; background: var(--q-bg2, #1e293b); padding: 4px; border-radius: 10px; }
  .tab {
    padding: 10px 20px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    color: var(--q-muted, #94a3b8);
    transition: all 0.2s;
    border: none;
    background: none;
  }
  .tab:hover { color: var(--q-text, #e2e8f0); background: var(--q-bg3, #334155); }
  .tab.active { background: var(--q-blue, #38bdf8); color: var(--q-bg, #0f172a); }
  
  .stats { display: flex; gap: 16px; margin-bottom: 20px; }
  .stat-card {
    background: var(--q-bg2, #1e293b);
    padding: 16px 24px;
    border-radius: 10px;
    flex: 1;
    text-align: center;
    border: 1px solid var(--q-border, #334155);
  }
  .stat-card .num { font-size: 28px; font-weight: 700; color: var(--q-blue, #38bdf8); }
  .stat-card .label { font-size: 12px; color: var(--q-muted, #64748b); margin-top: 4px; text-transform: uppercase; letter-spacing: 1px; }
  
  .tool-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 16px; }
  .tool-card {
    background: var(--q-bg2, #1e293b);
    border: 1px solid var(--q-border, #334155);
    border-radius: 12px;
    padding: 20px;
    transition: all 0.2s;
    cursor: pointer;
    position: relative;
  }
  .tool-card:hover {
    border-color: var(--q-blue, #38bdf8);
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(56, 189, 248, 0.1);
  }
  .tool-card .card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }
  .tool-card .card-title { font-size: 16px; font-weight: 600; color: var(--q-text, #f8fafc); }
  .tool-card .card-type { font-size: 11px; padding: 3px 8px; border-radius: 20px; font-weight: 500; }
  .type-tool { background: rgba(56, 189, 248, 0.15); color: var(--q-blue, #38bdf8); }
  .type-skill { background: rgba(168, 85, 247, 0.15); color: var(--q-purple, #a855f7); }
  .tool-card .card-desc {
    font-size: 13px;
    color: var(--q-muted, #94a3b8);
    line-height: 1.5;
    margin-bottom: 12px;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  .tool-card .card-meta { display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: var(--q-muted, #64748b); }
  .tool-card .card-tags { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 10px; }
  .tag { background: var(--q-bg3, #334155); padding: 2px 8px; border-radius: 4px; font-size: 11px; color: var(--q-muted, #94a3b8); }
  .installed-badge { position: absolute; bottom: 12px; right: 12px; background: var(--q-green, #22c55e); color: #fff; font-size: 10px; padding: 2px 8px; border-radius: 20px; font-weight: 600; }
  
  .modal-overlay { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.7); z-index: 100; justify-content: center; align-items: center; }
  .modal-overlay.active { display: flex; }
  .modal {
    background: var(--q-bg2, #1e293b);
    border-radius: 16px;
    padding: 32px;
    max-width: 600px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
    border: 1px solid var(--q-border, #334155);
  }
  .modal h2 { font-size: 22px; margin-bottom: 20px; color: var(--q-text, #f8fafc); }
  .modal .detail-row { display: flex; padding: 10px 0; border-bottom: 1px solid var(--q-border, #334155); }
  .modal .detail-label { width: 100px; color: var(--q-muted, #64748b); font-size: 14px; flex-shrink: 0; }
  .modal .detail-value { color: var(--q-text, #e2e8f0); font-size: 14px; }
  .modal .detail-tags { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 4px; }
  .modal-actions { display: flex; gap: 12px; margin-top: 24px; }
  
  .btn {
    padding: 10px 20px;
    border-radius: 8px;
    border: none;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    display: inline-flex;
    align-items: center;
    gap: 6px;
  }
  .btn-primary { background: var(--q-blue, #38bdf8); color: var(--q-bg, #0f172a); }
  .btn-primary:hover { background: var(--q-cyan, #7dd3fc); }
  .btn-danger { background: var(--q-red, #ef4444); color: #fff; }
  .btn-danger:hover { background: #f87171; }
  .btn-secondary { background: var(--q-bg3, #334155); color: var(--q-text, #e2e8f0); }
  .btn-secondary:hover { background: var(--q-bg4, #475569); }
  .btn:disabled { opacity: 0.5; cursor: not-allowed; }
  
  .loading { text-align: center; padding: 60px; color: var(--q-muted, #64748b); }
  .loading .spinner { width: 40px; height: 40px; border: 3px solid var(--q-border, #334155); border-top-color: var(--q-blue, #38bdf8); border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 16px; }
  @keyframes spin { to { transform: rotate(360deg); } }
  
  .empty { text-align: center; padding: 60px; color: var(--q-muted, #64748b); }
  .empty .icon { font-size: 48px; margin-bottom: 16px; }
  
  .toast { position: fixed; bottom: 24px; right: 24px; padding: 14px 24px; border-radius: 10px; font-size: 14px; z-index: 200; animation: slideIn 0.3s ease; }
  .toast-success { background: var(--q-green, #22c55e); color: #fff; }
  .toast-error { background: var(--q-red, #ef4444); color: #fff; }
  @keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
  
  .status-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 16px;
    background: var(--q-bg2, #1e293b);
    border-radius: 8px;
    margin-bottom: 16px;
    font-size: 13px;
    color: var(--q-muted, #64748b);
    border: 1px solid var(--q-border, #334155);
  }
  .status-bar .status-ok { color: var(--q-green, #22c55e); }
  .status-bar .status-err { color: var(--q-red, #ef4444); }
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>📦 <span>Agent</span> Toolkit Manager</h1>
    <div class="header-actions">
      <button class="btn btn-secondary" onclick="refreshTools()">🔄 刷新</button>
    </div>
  </div>
  
  <div class="status-bar">
    <span>📡 GitHub: <span id="status-github">连接中...</span></span>
    <span>💾 本地缓存: <span id="status-cache">-</span></span>
  </div>
  
  <div class="stats">
    <div class="stat-card"><div class="num" id="stat-tools">-</div><div class="label">工具</div></div>
    <div class="stat-card"><div class="num" id="stat-skills">-</div><div class="label">技巧</div></div>
    <div class="stat-card"><div class="num" id="stat-installed">-</div><div class="label">已安装</div></div>
  </div>
  
  <div class="search-box">
    <span class="search-icon">🔍</span>
    <input type="text" id="searchInput" placeholder="搜索工具名称、描述、标签、作者..." oninput="handleSearch()">
  </div>
  
  <div class="tabs">
    <button class="tab active" data-filter="all" onclick="setFilter('all', this)">全部</button>
    <button class="tab" data-filter="tool" onclick="setFilter('tool', this)">🔧 工具</button>
    <button class="tab" data-filter="skill" onclick="setFilter('skill', this)">📚 技巧</button>
    <button class="tab" data-filter="installed" onclick="setFilter('installed', this)">✅ 已安装</button>
  </div>
  
  <div id="toolGrid" class="tool-grid"></div>
</div>

<div class="modal-overlay" id="detailModal">
  <div class="modal">
    <h2 id="modalTitle"></h2>
    <div id="modalContent"></div>
    <div class="modal-actions" id="modalActions"></div>
  </div>
</div>

<script>
// GitHub 配置
const GITHUB_API = 'https://api.github.com';
const REPO = 'LiuQiang-AI/AGENT_TOOLS';
const BRANCH = 'main';

// 状态
let allTools = [];
let currentFilter = 'all';
let currentSearch = '';
let installedTools = {};

// GitHub API 调用（直接调用，GitHub 支持 CORS）
async function githubGet(path) {
  const url = `${GITHUB_API}/repos/${REPO}/contents/${path}?ref=${BRANCH}`;
  const resp = await fetch(url, {
    headers: {
      'Accept': 'application/vnd.github.v3+json',
      'User-Agent': 'QevosAgent-Toolkit'
    }
  });
  if (!resp.ok) throw new Error(`GitHub API ${resp.status}: ${resp.statusText}`);
  return resp.json();
}

// Base64 解码为 UTF-8 字符串（修复中文乱码）
function base64ToUtf8(base64) {
  const binary = atob(base64.replace(/\n/g, ''));
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return new TextDecoder('utf-8').decode(bytes);
}

// 获取文件内容（解码 base64）
async function getFileContent(path) {
  const data = await githubGet(path);
  if (data.content) {
    return base64ToUtf8(data.content);
  }
  return null;
}

// 使用 qevos 桥进行本地文件操作
async function loadInstalledTools() {
  try {
    // 尝试使用 qevos 桥读取已安装工具列表
    if (window.qevos) {
      const data = await qevos.readJSON('installed.json');
      if (data) {
        installedTools = data;
        return;
      }
    }
    // 回退到 localStorage
    const stored = localStorage.getItem('toolkit_installed');
    if (stored) {
      installedTools = JSON.parse(stored);
    }
  } catch (e) {
    console.warn('加载已安装工具失败:', e);
    installedTools = {};
  }
}

async function saveInstalledTools() {
  try {
    // 优先使用 qevos 桥
    if (window.qevos) {
      await qevos.writeJSON('installed.json', installedTools);
      return;
    }
  } catch (e) {
    console.warn('使用 qevos 保存失败，回退到 localStorage:', e);
  }
  // 回退到 localStorage
  localStorage.setItem('toolkit_installed', JSON.stringify(installedTools));
}

function isInstalled(name) {
  return name in installedTools;
}

function markInstalled(name, version) {
  installedTools[name] = {
    version: version || '0.0.0',
    install_date: new Date().toISOString()
  };
  saveInstalledTools();
}

function markUninstalled(name) {
  delete installedTools[name];
  saveInstalledTools();
}

// 获取工具列表
async function fetchTools() {
  const grid = document.getElementById('toolGrid');
  grid.innerHTML = '<div class="loading"><div class="spinner"></div><div>加载工具列表中...</div></div>';
  
  const statusGithub = document.getElementById('status-github');
  statusGithub.textContent = '连接中...';
  statusGithub.className = '';
  
  try {
    // 并行获取工具和技巧
    const [toolDirs, skillDirs] = await Promise.all([
      githubGet('tools').catch(() => []),
      githubGet('skills').catch(() => [])
    ]);
    
    allTools = [];
    
    // 处理工具
    for (const item of (Array.isArray(toolDirs) ? toolDirs : [toolDirs])) {
      if (item.type === 'dir' && !item.name.startsWith('_')) {
        try {
          const manifestContent = await getFileContent(`tools/${item.name}/manifest.json`);
          if (manifestContent) {
            const manifest = JSON.parse(manifestContent);
            allTools.push({ type: 'tool', name: item.name, manifest });
          }
        } catch (e) {
          console.warn(`获取 ${item.name} manifest 失败:`, e);
        }
      }
    }
    
    // 处理技巧
    for (const item of (Array.isArray(skillDirs) ? skillDirs : [skillDirs])) {
      if (item.type === 'dir' && !item.name.startsWith('_')) {
        try {
          const manifestContent = await getFileContent(`skills/${item.name}/manifest.json`);
          if (manifestContent) {
            const manifest = JSON.parse(manifestContent);
            allTools.push({ type: 'skill', name: item.name, manifest });
          }
        } catch (e) {
          console.warn(`获取 ${item.name} manifest 失败:`, e);
        }
      }
    }
    
    // 更新状态
    statusGithub.textContent = '已连接';
    statusGithub.className = 'status-ok';
    document.getElementById('status-cache').textContent = `${allTools.length} 个工具/技巧`;
    
    updateStats();
    renderTools();
    
  } catch (e) {
    statusGithub.textContent = '连接失败';
    statusGithub.className = 'status-err';
    grid.innerHTML = `<div class="empty">
      <div class="icon">⚠️</div>
      <div>加载失败: ${e.message}</div>
      <div style="margin-top:12px"><button class="btn btn-primary" onclick="refreshTools()">重试</button></div>
    </div>`;
  }
}

function updateStats() {
  document.getElementById('stat-tools').textContent = allTools.filter(t => t.type === 'tool').length;
  document.getElementById('stat-skills').textContent = allTools.filter(t => t.type === 'skill').length;
  document.getElementById('stat-installed').textContent = allTools.filter(t => isInstalled(t.name)).length;
}

function getFilteredTools() {
  let filtered = [...allTools];
  if (currentFilter === 'tool') filtered = filtered.filter(t => t.type === 'tool');
  else if (currentFilter === 'skill') filtered = filtered.filter(t => t.type === 'skill');
  else if (currentFilter === 'installed') filtered = filtered.filter(t => isInstalled(t.name));
  
  if (currentSearch) {
    const q = currentSearch.toLowerCase();
    filtered = filtered.filter(t => {
      const m = t.manifest || {};
      return `${t.name} ${m.description||''} ${(m.tags||[]).join(' ')} ${m.author||''}`.toLowerCase().includes(q);
    });
  }
  return filtered;
}

function renderTools() {
  const grid = document.getElementById('toolGrid');
  const filtered = getFilteredTools();
  
  if (filtered.length === 0) {
    grid.innerHTML = '<div class="empty"><div class="icon">📭</div><div>没有找到匹配的工具</div></div>';
    return;
  }
  
  grid.innerHTML = filtered.map(t => {
    const m = t.manifest || {};
    const installed = isInstalled(t.name);
    const typeClass = t.type === 'tool' ? 'type-tool' : 'type-skill';
    const typeLabel = t.type === 'tool' ? '🔧 工具' : '📚 技巧';
    const tags = (m.tags || []).slice(0, 3).map(tag => `<span class="tag">${tag}</span>`).join('');
    
    return `<div class="tool-card" onclick="showDetail('${t.name}')">
      ${installed ? '<div class="installed-badge">✅ 已安装</div>' : ''}
      <div class="card-header">
        <div class="card-title">${t.name}</div>
        <div class="card-type ${typeClass}">${typeLabel}</div>
      </div>
      <div class="card-desc">${m.description || '暂无描述'}</div>
      <div class="card-meta">
        <span>v${m.version || '0.0.0'}</span>
        <span>👤 ${m.author || '未知'}</span>
      </div>
      ${tags ? `<div class="card-tags">${tags}</div>` : ''}
    </div>`;
  }).join('');
}

function setFilter(filter, el) {
  currentFilter = filter;
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  el.classList.add('active');
  renderTools();
}

function handleSearch() {
  currentSearch = document.getElementById('searchInput').value.trim();
  renderTools();
}

async function showDetail(name) {
  const tool = allTools.find(t => t.name === name);
  if (!tool) return;
  
  const m = tool.manifest || {};
  const installed = isInstalled(name);
  
  document.getElementById('modalTitle').textContent = `${tool.type === 'tool' ? '🔧' : '📚'} ${name}`;
  
  const tags = (m.tags || []).map(tag => `<span class="tag">${tag}</span>`).join('');
  const deps = Array.isArray(m.dependencies) ? m.dependencies.join(', ') : (m.dependencies ? JSON.stringify(m.dependencies) : '无');
  const files = (m.files || []).join(', ') || '-';
  
  document.getElementById('modalContent').innerHTML = `
    <div class="detail-row"><div class="detail-label">类型</div><div class="detail-value">${tool.type === 'tool' ? '🔧 工具' : '📚 技巧'}</div></div>
    <div class="detail-row"><div class="detail-label">版本</div><div class="detail-value">v${m.version || '0.0.0'}</div></div>
    <div class="detail-row"><div class="detail-label">描述</div><div class="detail-value">${m.description || '-'}</div></div>
    <div class="detail-row"><div class="detail-label">作者</div><div class="detail-value">${m.author || '未知'} ${m.email ? `(${m.email})` : ''}</div></div>
    <div class="detail-row"><div class="detail-label">日期</div><div class="detail-value">${m.date || '-'}</div></div>
    <div class="detail-row"><div class="detail-label">标签</div><div class="detail-value"><div class="detail-tags">${tags || '无'}</div></div></div>
    <div class="detail-row"><div class="detail-label">依赖</div><div class="detail-value">${deps}</div></div>
    <div class="detail-row"><div class="detail-label">Python</div><div class="detail-value">${m.python_version || '任意'}</div></div>
    <div class="detail-row"><div class="detail-label">文件</div><div class="detail-value">${files}</div></div>
    <div class="detail-row"><div class="detail-label">状态</div><div class="detail-value">${installed ? '✅ 已安装' : '❌ 未安装'}</div></div>
  `;
  
  document.getElementById('modalActions').innerHTML = `
    ${installed 
      ? `<button class="btn btn-danger" onclick="uninstallTool('${name}')">🗑️ 卸载</button>` 
      : `<button class="btn btn-primary" onclick="installTool('${name}')">📥 安装</button>`}
    <button class="btn btn-secondary" onclick="closeModal()">关闭</button>
  `;
  
  document.getElementById('detailModal').classList.add('active');
}

function closeModal() {
  document.getElementById('detailModal').classList.remove('active');
}

async function installTool(name) {
  const btn = event.target;
  btn.disabled = true;
  btn.textContent = '⏳ 安装中...';
  
  try {
    showToast(`正在安装 ${name}...`, 'success');
    
    const tool = allTools.find(t => t.name === name);
    if (!tool) throw new Error('工具未找到');
    
    const m = tool.manifest || {};
    const files = m.files || [];
    
    // 下载文件到本地缓存
    const cacheDir = `cache/${name}`;
    
    // 保存 manifest
    const manifestContent = JSON.stringify(m, null, 2);
    if (window.qevos) {
      await qevos.writeFile(`${cacheDir}/manifest.json`, manifestContent);
    }
    
    // 下载其他文件
    for (const fname of files) {
      if (fname === 'manifest.json') continue;
      try {
        const content = await getFileContent(`${tool.type === 'tool' ? 'tools' : 'skills'}/${name}/${fname}`);
        if (content && window.qevos) {
          await qevos.writeFile(`${cacheDir}/${fname}`, content);
        }
      } catch (e) {
        console.warn(`下载 ${fname} 失败:`, e);
      }
    }
    
    // 标记为已安装
    markInstalled(name, m.version);
    
    showToast(`✅ ${name} 安装成功!`, 'success');
    closeModal();
    updateStats();
    renderTools();
    
  } catch (e) {
    showToast(`❌ 安装失败: ${e.message}`, 'error');
  } finally {
    btn.disabled = false;
  }
}

async function uninstallTool(name) {
  if (!confirm(`确定要卸载 ${name} 吗？`)) return;
  
  const btn = event.target;
  btn.disabled = true;
  btn.textContent = '⏳ 卸载中...';
  
  try {
    // 删除缓存文件
    if (window.qevos) {
      const cacheDir = `cache/${name}`;
      // 尝试删除 manifest
      try { await qevos.remove(`${cacheDir}/manifest.json`); } catch {}
    }
    
    // 标记为未安装
    markUninstalled(name);
    
    showToast(`✅ ${name} 已卸载`, 'success');
    closeModal();
    updateStats();
    renderTools();
    
  } catch (e) {
    showToast(`❌ 卸载失败: ${e.message}`, 'error');
  } finally {
    btn.disabled = false;
  }
}

function refreshTools() {
  fetchTools();
}

function showToast(msg, type = 'success') {
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = msg;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}

// 事件监听
document.getElementById('detailModal').addEventListener('click', function(e) {
  if (e.target === this) closeModal();
});

document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') closeModal();
  if (e.key === '/' && document.activeElement !== document.getElementById('searchInput')) {
    e.preventDefault();
    document.getElementById('searchInput').focus();
  }
});

// 主题变化处理
if (window.qevos && qevos.onTheme) {
  qevos.onTheme((theme) => {
    console.log('主题变化:', theme);
    // 可以在这里处理主题变化相关的逻辑
  });
}

// 初始化
(async function() {
  await loadInstalledTools();
  fetchTools();
})();
</script>
</body>
</html>