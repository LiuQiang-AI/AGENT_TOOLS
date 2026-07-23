#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Agent Toolkit Backend Server

使用 FastAPI 提供 CORS 支持的 API 服务，替代独立的代理服务器。
自动处理跨域请求，前端可以直接访问。

用法:
  python agent_toolkit_backend.py [port]
  默认端口: 8767
"""
import sys
import os
import json
import base64
import subprocess
from pathlib import Path
from datetime import datetime
from urllib.parse import urlencode

import urllib.request
import urllib.error

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# ==================== 配置 ====================
GITHUB_API = "https://api.github.com"
TOKEN = os.environ.get('GITHUB_TOKEN', '')  # 设置环境变量 GITHUB_TOKEN
REPO = "LiuQiang-AI/AGENT_TOOLS"
BRANCH = "main"

# 工具存储目录
TOOLKIT_DIR = Path(os.environ.get('APPDATA', str(Path.home()))) / '.qevos' / 'toolkit'
LOCAL_CACHE = TOOLKIT_DIR / 'cache'
INSTALLED_DIR = TOOLKIT_DIR / 'installed'

# ==================== FastAPI 应用 ====================
app = FastAPI(title="Agent Toolkit Backend", version="1.0.0")

# 配置 CORS - 允许所有来源
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 数据模型 ====================
class InstallRequest(BaseModel):
    name: str

class UninstallRequest(BaseModel):
    name: str

# ==================== Gitea API 客户端 ====================
def github_get(path: str, params: dict = None) -> dict:
    """调用 Gitea API"""
    url = f"{GITEA_API}/{path}"
    if params:
        query = urlencode(params)
        url = f"{url}?{query}"
    
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'token {TOKEN}')
    req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read().decode('utf-8')
            return json.loads(data) if data else {}
    except urllib.error.HTTPError as e:
        raise HTTPException(status_code=e.code, detail=f"Gitea API error: {e.reason}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")

def get_manifest(content_path: str) -> dict:
    """获取 manifest.json 内容"""
    result = github_get(f"repos/{REPO}/contents/{content_path}", {"ref": BRANCH})
    
    if isinstance(result, dict) and 'content' in result:
        content = base64.b64decode(result['content']).decode('utf-8', errors='replace')
        return json.loads(content)
    elif isinstance(result, list) and result and 'content' in result[0]:
        content = base64.b64decode(result[0]['content']).decode('utf-8', errors='replace')
        return json.loads(content)
    return {}

def get_file_content(content_path: str) -> str:
    """获取文件内容（解码 base64）"""
    result = github_get(f"repos/{REPO}/contents/{content_path}", {"ref": BRANCH})
    
    if isinstance(result, dict) and 'content' in result:
        return base64.b64decode(result['content']).decode('utf-8', errors='replace')
    elif isinstance(result, list) and result and 'content' in result[0]:
        return base64.b64decode(result[0]['content']).decode('utf-8', errors='replace')
    return ""

# ==================== API 端点 ====================

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "service": "agent_toolkit_backend"}

@app.get("/api/tools")
async def list_tools():
    """获取工具列表"""
    try:
        result = github_get(f"repos/{REPO}/contents/tools", {"ref": BRANCH})
        items = result if isinstance(result, list) else [result]
        
        tools = []
        for item in items:
            if item.get('type') == 'dir' and not item.get('name', '').startswith('_'):
                name = item['name']
                try:
                    manifest = get_manifest(f"tools/{name}/manifest.json")
                    tools.append({
                        "type": "tool",
                        "name": name,
                        "manifest": manifest
                    })
                except:
                    tools.append({
                        "type": "tool",
                        "name": name,
                        "manifest": {}
                    })
        return tools
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/skills")
async def list_skills():
    """获取技巧列表"""
    try:
        result = github_get(f"repos/{REPO}/contents/skills", {"ref": BRANCH})
        items = result if isinstance(result, list) else [result]
        
        skills = []
        for item in items:
            if item.get('type') == 'dir' and not item.get('name', '').startswith('_'):
                name = item['name']
                try:
                    manifest = get_manifest(f"skills/{name}/manifest.json")
                    skills.append({
                        "type": "skill",
                        "name": name,
                        "manifest": manifest
                    })
                except:
                    skills.append({
                        "type": "skill",
                        "name": name,
                        "manifest": {}
                    })
        return skills
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/content/{path:path}")
async def get_content(path: str):
    """获取文件内容"""
    try:
        content = get_file_content(path)
        return {"content": content}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/installed")
async def list_installed():
    """获取已安装工具列表"""
    installed = {}
    INSTALLED_DIR.mkdir(parents=True, exist_ok=True)
    
    for f in INSTALLED_DIR.glob('*.json'):
        try:
            with open(f, 'r', encoding='utf-8') as fp:
                info = json.load(fp)
                installed[f.stem] = {
                    "version": info.get('version', '0.0.0'),
                    "install_date": info.get('install_date', ''),
                    "local_path": info.get('local_path', '')
                }
        except:
            pass
    return installed

@app.post("/api/install")
async def install_tool(req: InstallRequest):
    """安装工具"""
    name = req.name
    if not name:
        raise HTTPException(status_code=400, detail="Name required")
    
    try:
        manifest = get_manifest(f"tools/{name}/manifest.json")
        if not manifest:
            raise HTTPException(status_code=404, detail=f"Tool {name} not found")
        
        # 创建目录
        LOCAL_CACHE.mkdir(parents=True, exist_ok=True)
        INSTALLED_DIR.mkdir(parents=True, exist_ok=True)
        tool_dir = LOCAL_CACHE / name
        tool_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存 manifest
        (tool_dir / 'manifest.json').write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8'
        )
        
        # 下载文件
        files = manifest.get('files', [])
        for fname in files:
            if fname in ['manifest.json', 'install.json']:
                continue
            try:
                content = get_file_content(f"tools/{name}/{fname}")
                if content:
                    (tool_dir / fname).write_text(content, encoding='utf-8')
            except:
                pass
        
        # 执行 pre_install
        try:
            install_content = get_file_content(f"tools/{name}/install.json")
            if install_content:
                install_rules = json.loads(install_content)
                if install_rules.get('pre_install'):
                    for cmd in install_rules['pre_install']:
                        subprocess.run(cmd, shell=True, check=True, 
                                     capture_output=True, text=True, timeout=120)
        except:
            pass
        
        # 保存安装信息
        installed_info = {
            "name": name,
            "version": manifest.get('version', '0.0.0'),
            "install_date": datetime.now().isoformat(),
            "local_path": str(tool_dir),
            "manifest": manifest
        }
        (INSTALLED_DIR / f"{name}.json").write_text(
            json.dumps(installed_info, ensure_ascii=False, indent=2), encoding='utf-8'
        )
        
        return {"success": True, "message": f"{name} installed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/uninstall")
async def uninstall_tool(req: UninstallRequest):
    """卸载工具"""
    name = req.name
    if not name:
        raise HTTPException(status_code=400, detail="Name required")
    
    installed_file = INSTALLED_DIR / f"{name}.json"
    if not installed_file.exists():
        raise HTTPException(status_code=404, detail=f"{name} not installed")
    
    try:
        installed_file.unlink()
        
        tool_dir = LOCAL_CACHE / name
        if tool_dir.exists():
            import shutil
            shutil.rmtree(tool_dir, ignore_errors=True)
        
        return {"success": True, "message": f"{name} uninstalled successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 启动 ====================
if __name__ == '__main__':
    import uvicorn
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8767
    print(f"📦 Agent Toolkit Backend running on http://127.0.0.1:{port}")
    print(f"   Gitea: {GITEA_API}")
    print(f"   Repo:  {REPO}")
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")
