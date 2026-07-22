#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Agent Toolkit Proxy Server - 解决跨域问题

用法:
  python toolkit_proxy.py [port]
  默认端口: 8767
"""
import sys
import os
import json
import base64
import urllib.request
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

GITHUB_API = "https://api.github.com"
TOKEN = "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"
REPO = "LiuQiang-AI/AGENT_TOOLS"
BRANCH = "main"

class ToolkitHandler(BaseHTTPRequestHandler):
    
    def send_cors_headers(self):
        """发送 CORS 头 - 必须在 send_response 之后调用"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    
    def send_json(self, data, status=200):
        """发送 JSON 响应 - 正确的 HTTP 响应顺序"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)
        
        if path == '/api/tools':
            self.handle_tools()
        elif path == '/api/skills':
            self.handle_skills()
        elif path.startswith('/api/content/'):
            content_path = path[len('/api/content/'):]
            self.handle_content(content_path)
        elif path == '/api/installed':
            self.handle_installed()
        elif path == '/api/health':
            self.send_json({'status': 'ok', 'source': 'github', 'repo': REPO})
        else:
            self.send_json({'error': 'Not Found'}, 404)
    
    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path == '/api/install':
            self.handle_install()
        elif path == '/api/uninstall':
            self.handle_uninstall()
        else:
            self.send_json({'error': 'Not Found'}, 404)
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
    
    def github_get(self, path, params=None):
        """调用 GitHub API
        path 应该是相对于 repos/{REPO}/ 的路径，如 'contents/tools'
        """
        url = f"{GITHUB_API}/repos/{REPO}/{path}"
        if params:
            query = '&'.join(f"{k}={v}" for k, v in params.items())
            url = f"{url}?{query}"
        req = urllib.request.Request(url)
        req.add_header('Authorization', f'token {TOKEN}')
        req.add_header('Content-Type', 'application/json')
        req.add_header('User-Agent', 'QevosAgent-Toolkit-Proxy')
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read().decode('utf-8')
                return json.loads(data) if data else []
        except Exception as e:
            return {'error': str(e)}
    
    def get_manifest(self, path):
        """获取 manifest.json 内容并解析为 JSON"""
        result = self.github_get(f"contents/{path}", {'ref': BRANCH})
        # GitHub API 返回单个文件时是 dict
        if isinstance(result, dict) and 'content' in result:
            content = base64.b64decode(result['content']).decode('utf-8', errors='replace')
            try:
                return json.loads(content)
            except:
                return None
        elif isinstance(result, list) and result and 'content' in result[0]:
            content = base64.b64decode(result[0]['content']).decode('utf-8', errors='replace')
            try:
                return json.loads(content)
            except:
                return None
        return None
    
    def get_content(self, path):
        """获取文件内容（解码 base64）"""
        result = self.github_get(f"contents/{path}", {'ref': BRANCH})
        # Gitea API 返回单个文件时是 dict，不是 list
        if isinstance(result, dict) and 'content' in result:
            return base64.b64decode(result['content']).decode('utf-8', errors='replace')
        elif isinstance(result, list) and result and 'content' in result[0]:
            return base64.b64decode(result[0]['content']).decode('utf-8', errors='replace')
        return None
    
    def handle_tools(self):
        """获取工具列表"""
        result = self.github_get("contents/tools", {'ref': BRANCH})
        if isinstance(result, dict) and 'error' in result:
            self.send_json({'error': result['error']}, 500)
            return
        
        tools = []
        for item in (result if isinstance(result, list) else [result]):
            if item.get('type') == 'dir' and not item.get('name', '').startswith('_') and item.get('name') != 'README.md':
                manifest = self.get_manifest(f"tools/{item['name']}/manifest.json")
                tools.append({
                    'type': 'tool',
                    'name': item['name'],
                    'manifest': manifest or {}
                })
        self.send_json(tools)
    
    def handle_skills(self):
        """获取技巧列表"""
        result = self.github_get("contents/skills", {'ref': BRANCH})
        if isinstance(result, dict) and 'error' in result:
            self.send_json({'error': result['error']}, 500)
            return
        
        skills = []
        for item in (result if isinstance(result, list) else [result]):
            if item.get('type') == 'dir' and not item.get('name', '').startswith('_') and item.get('name') != 'README.md':
                manifest = self.get_manifest(f"skills/{item['name']}/manifest.json")
                skills.append({
                    'type': 'skill',
                    'name': item['name'],
                    'manifest': manifest or {}
                })
        self.send_json(skills)
    
    def handle_content(self, content_path):
        """获取文件内容"""
        result = self.github_get(f"contents/{content_path}", {'ref': BRANCH})
        if isinstance(result, dict) and 'error' in result:
            self.send_json({'error': result['error']}, 500)
        elif isinstance(result, dict) and 'content' in result:
            # Gitea API 返回单个文件时是 dict
            content = base64.b64decode(result['content']).decode('utf-8', errors='replace')
            self.send_json({'content': content})
        elif isinstance(result, list) and result and 'content' in result[0]:
            content = base64.b64decode(result[0]['content']).decode('utf-8', errors='replace')
            self.send_json({'content': content})
        else:
            self.send_json({'error': 'Content not found'}, 404)
    
    def handle_installed(self):
        """获取已安装工具列表"""
        from pathlib import Path
        toolkit_dir = Path(os.environ.get('APPDATA', str(Path.home()))) / '.qevos' / 'toolkit' / 'installed'
        installed = {}
        if toolkit_dir.exists():
            for f in toolkit_dir.glob('*.json'):
                try:
                    with open(f, 'r', encoding='utf-8') as fp:
                        info = json.load(fp)
                        installed[f.stem] = {
                            'version': info.get('version', '0.0.0'),
                            'install_date': info.get('install_date', ''),
                            'local_path': info.get('local_path', '')
                        }
                except:
                    pass
        self.send_json(installed)
    
    def handle_install(self):
        """安装工具"""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        try:
            data = json.loads(body)
            name = data.get('name', '')
            if not name:
                self.send_json({'error': 'Name required'}, 400)
                return
            
            manifest = self.get_manifest(f"tools/{name}/manifest.json")
            if not manifest:
                self.send_json({'error': f'Tool {name} not found'}, 404)
                return
            
            import subprocess
            from pathlib import Path
            from datetime import datetime
            
            toolkit_dir = Path(os.environ.get('APPDATA', str(Path.home()))) / '.qevos' / 'toolkit'
            local_cache = toolkit_dir / 'cache'
            installed_dir = toolkit_dir / 'installed'
            for d in [local_cache, installed_dir]:
                d.mkdir(parents=True, exist_ok=True)
            
            tool_dir = local_cache / name
            tool_dir.mkdir(parents=True, exist_ok=True)
            
            # Save manifest
            (tool_dir / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
            
            # Download files
            files = manifest.get('files', [])
            for fname in files:
                if fname in ['manifest.json', 'install.json']:
                    continue
                content = self.get_content(f"tools/{name}/{fname}")
                if content:
                    (tool_dir / fname).write_text(content, encoding='utf-8')
            
            # Run pre_install if exists
            install_content = self.get_content(f"tools/{name}/install.json")
            if install_content:
                try:
                    install_rules = json.loads(install_content)
                    if install_rules.get('pre_install'):
                        for cmd in install_rules['pre_install']:
                            subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True, timeout=120)
                except:
                    pass
            
            # Save installed info
            installed_info = {
                'name': name,
                'version': manifest.get('version', '0.0.0'),
                'install_date': datetime.now().isoformat(),
                'local_path': str(tool_dir),
                'manifest': manifest
            }
            (installed_dir / f"{name}.json").write_text(json.dumps(installed_info, ensure_ascii=False, indent=2), encoding='utf-8')
            
            self.send_json({'success': True, 'message': f'{name} installed successfully'})
            
        except Exception as e:
            self.send_json({'error': str(e)}, 500)
    
    def handle_uninstall(self):
        """卸载工具"""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        try:
            data = json.loads(body)
            name = data.get('name', '')
            if not name:
                self.send_json({'error': 'Name required'}, 400)
                return
            
            import shutil
            from pathlib import Path
            
            toolkit_dir = Path(os.environ.get('APPDATA', str(Path.home()))) / '.qevos' / 'toolkit'
            installed_dir = toolkit_dir / 'installed'
            
            installed_file = installed_dir / f"{name}.json"
            if not installed_file.exists():
                self.send_json({'error': f'{name} not installed'}, 404)
                return
            
            installed_file.unlink()
            
            local_cache = toolkit_dir / 'cache' / name
            if local_cache.exists():
                shutil.rmtree(local_cache, ignore_errors=True)
            
            self.send_json({'success': True, 'message': f'{name} uninstalled successfully'})
            
        except Exception as e:
            self.send_json({'error': str(e)}, 500)
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8767
    server = HTTPServer(('127.0.0.1', port), ToolkitHandler)
    print(f"📦 Agent Toolkit Proxy Server running on http://127.0.0.1:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()
