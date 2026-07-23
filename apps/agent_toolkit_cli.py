#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Agent Toolkit CLI - 命令行工具管理

用法:
  agent_toolkit_cli list              # 列出所有工具和技巧
  agent_toolkit_cli search <关键词>   # 搜索工具
  agent_toolkit_cli info <名称>       # 查看详情
  agent_toolkit_cli install <名称>    # 安装工具
  agent_toolkit_cli uninstall <名称>  # 卸载工具
"""
import sys
import os
import json
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

GITHUB_API = "https://api.github.com"
TOKEN = os.environ.get('GITHUB_TOKEN', '')  # 设置环境变量 GITHUB_TOKEN
REPO = "LiuQiang-AI/AGENT_TOOLS"
BRANCH = "main"
TOOLKIT_DIR = Path(os.environ.get('APPDATA', str(Path.home()))) / '.qevos' / 'toolkit'
LOCAL_CACHE = TOOLKIT_DIR / 'cache'
INSTALLED_DIR = TOOLKIT_DIR / 'installed'

def init_dirs():
    for d in [TOOLKIT_DIR, LOCAL_CACHE, INSTALLED_DIR]:
        d.mkdir(parents=True, exist_ok=True)

def github_get(path, params=None):
    """调用 GitHub API，path 相对于 repos/{REPO}/"""
    url = f"{GITHUB_API}/repos/{REPO}/{path}"
    if params:
        query = '&'.join(f"{k}={v}" for k, v in params.items())
        url = f"{url}?{query}"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'token {TOKEN}')
    req.add_header('Content-Type', 'application/json')
    req.add_header('User-Agent', 'QevosAgent-Toolkit-CLI')
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read().decode('utf-8')
            return json.loads(data) if data else []
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        print(f"API错误 ({e.code}): {body}")
        return None
    except Exception as e:
        print(f"请求失败: {e}")
        return None

def get_repo_contents(path='tools', branch=BRANCH):
    result = github_get(f"contents/{path}", {'ref': branch})
    if result is None:
        return []
    if isinstance(result, list):
        return result
    return [result]

def download_file_content(path, branch=BRANCH):
    import base64
    result = github_get(f"contents/{path}", {'ref': branch})
    if result and isinstance(result, dict) and 'content' in result:
        return base64.b64decode(result['content']).decode('utf-8', errors='replace')
    return None

def list_tools():
    print("\n" + "="*60)
    print("📦 可用工具列表")
    print("="*60)
    tools = get_repo_contents('tools')
    skills = get_repo_contents('skills')
    tool_dirs = [t for t in tools if t.get('type') == 'dir' and not t.get('name', '').startswith('_') and t.get('name') != 'README.md']
    skill_dirs = [s for s in skills if s.get('type') == 'dir' and not s.get('name', '').startswith('_') and s.get('name') != 'README.md']
    if not tool_dirs and not skill_dirs:
        print("\n暂无工具或技巧。\n")
        return
    print(f"\n🔧 工具 ({len(tool_dirs)}个):")
    print("-"*40)
    for t in tool_dirs:
        name = t.get('name', 'unknown')
        manifest_content = download_file_content(f"tools/{name}/manifest.json")
        if manifest_content:
            try:
                manifest = json.loads(manifest_content)
                desc = manifest.get('description', '无描述')[:40]
                author = manifest.get('author', '未知')
                version = manifest.get('version', '0.0.0')
                print(f"  [{version}] {name}")
                print(f"         {desc}")
                print(f"         作者: {author}")
            except:
                print(f"  {name}")
        else:
            print(f"  {name}")
        print()
    print(f"\n📚 技巧 ({len(skill_dirs)}个):")
    print("-"*40)
    for s in skill_dirs:
        name = s.get('name', 'unknown')
        manifest_content = download_file_content(f"skills/{name}/manifest.json")
        if manifest_content:
            try:
                manifest = json.loads(manifest_content)
                desc = manifest.get('description', '无描述')[:40]
                author = manifest.get('author', '未知')
                print(f"  {name}")
                print(f"    {desc}")
                print(f"    作者: {author}")
            except:
                print(f"  {name}")
        else:
            print(f"  {name}")
        print()

def search_tools(keyword):
    print(f"\n🔍 搜索: {keyword}")
    print("-"*40)
    tools = get_repo_contents('tools')
    skills = get_repo_contents('skills')
    all_items = []
    for t in tools:
        if t.get('type') == 'dir' and not t.get('name', '').startswith('_'):
            all_items.append(('tool', t.get('name'), f"tools/{t.get('name')}/manifest.json"))
    for s in skills:
        if s.get('type') == 'dir' and not s.get('name', '').startswith('_'):
            all_items.append(('skill', s.get('name'), f"skills/{s.get('name')}/manifest.json"))
    found = []
    for item_type, name, manifest_path in all_items:
        content = download_file_content(manifest_path)
        if content:
            try:
                manifest = json.loads(content)
                searchable = f"{name} {manifest.get('description','')} {' '.join(manifest.get('tags',[]))} {manifest.get('author','')}"
                if keyword.lower() in searchable.lower():
                    found.append((item_type, name, manifest))
            except:
                pass
    if not found:
        print("未找到匹配的工具或技巧。")
        return
    for item_type, name, manifest in found:
        icon = "🔧" if item_type == "tool" else "📚"
        print(f"\n  {icon} {name} (v{manifest.get('version','0.0.0')})")
        print(f"     {manifest.get('description','')}")
        print(f"     作者: {manifest.get('author','未知')} | 标签: {', '.join(manifest.get('tags',[]))}")

def show_info(name):
    for item_type, base_path in [('tool', 'tools'), ('skill', 'skills')]:
        manifest_path = f"{base_path}/{name}/manifest.json"
        content = download_file_content(manifest_path)
        if content:
            try:
                manifest = json.loads(content)
                icon = "🔧" if item_type == "tool" else "📚"
                print(f"\n{icon} {name} (v{manifest.get('version','0.0.0')})")
                print("="*50)
                print(f"类型:     {item_type}")
                print(f"描述:     {manifest.get('description','')}")
                print(f"作者:     {manifest.get('author','未知')}")
                print(f"邮箱:     {manifest.get('email','')}")
                print(f"日期:     {manifest.get('date','')}")
                print(f"标签:     {', '.join(manifest.get('tags',[]))}")
                print(f"依赖:     {', '.join(manifest.get('dependencies',[]))}")
                print(f"Python:   {manifest.get('python_version','任意')}")
                print(f"文件:     {', '.join(manifest.get('files',[]))}")
                installed_file = INSTALLED_DIR / f"{name}.json"
                if installed_file.exists():
                    print(f"\n✅ 已安装")
                else:
                    print(f"\n❌ 未安装")
                return
            except:
                pass
    print(f"\n未找到 '{name}'")

def install_tool(name):
    import subprocess
    print(f"\n📥 安装工具: {name}")
    print("-"*40)
    manifest_path = f"tools/{name}/manifest.json"
    content = download_file_content(manifest_path)
    if not content:
        print(f"❌ 未找到工具 '{name}'")
        return
    try:
        manifest = json.loads(content)
    except:
        print("❌ manifest.json 格式错误")
        return
    tool_dir = LOCAL_CACHE / name
    tool_dir.mkdir(parents=True, exist_ok=True)
    manifest_file = tool_dir / 'manifest.json'
    manifest_file.write_text(content, encoding='utf-8')
    install_content = download_file_content(f"tools/{name}/install.json")
    install_rules = None
    if install_content:
        try:
            install_rules = json.loads(install_content)
            install_file = tool_dir / 'install.json'
            install_file.write_text(install_content, encoding='utf-8')
        except:
            pass
    files_list = manifest.get('files', [])
    for fname in files_list:
        if fname in ['manifest.json', 'install.json']:
            continue
        file_content = download_file_content(f"tools/{name}/{fname}")
        if file_content:
            fpath = tool_dir / fname
            fpath.write_text(file_content, encoding='utf-8')
    if install_rules and install_rules.get('pre_install'):
        print("\n📦 安装依赖...")
        for cmd in install_rules['pre_install']:
            print(f"  执行: {cmd}")
            try:
                subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True, timeout=120)
                print(f"  ✅ 成功")
            except subprocess.CalledProcessError as e:
                print(f"  ❌ 失败: {e.stderr.strip()}")
            except Exception as e:
                print(f"  ❌ 错误: {e}")
    installed_info = {
        'name': name,
        'version': manifest.get('version', '0.0.0'),
        'install_date': datetime.now().isoformat(),
        'local_path': str(tool_dir),
        'manifest': manifest
    }
    installed_file = INSTALLED_DIR / f"{name}.json"
    installed_file.write_text(json.dumps(installed_info, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\n✅ {name} 安装完成!")
    print(f"   路径: {tool_dir}")
    print(f"   版本: {manifest.get('version', '0.0.0')}")

def uninstall_tool(name):
    import shutil
    installed_file = INSTALLED_DIR / f"{name}.json"
    if not installed_file.exists():
        print(f"❌ '{name}' 未安装")
        return
    info = json.loads(installed_file.read_text(encoding='utf-8'))
    local_path = info.get('local_path', '')
    if local_path and os.path.exists(local_path):
        shutil.rmtree(local_path, ignore_errors=True)
    installed_file.unlink()
    print(f"✅ {name} 已卸载")

def show_usage():
    print("""\n📦 Agent Toolkit Manager\n用法:
  agent_toolkit list              # 列出所有工具和技巧
  agent_toolkit search <关键词>   # 搜索工具
  agent_toolkit info <名称>       # 查看详情
  agent_toolkit install <名称>    # 安装工具
  agent_toolkit uninstall <名称>  # 卸载工具
  agent_toolkit help              # 显示帮助""")

if __name__ == '__main__':
    init_dirs()
    if len(sys.argv) < 2:
        show_usage()
        sys.exit(0)
    command = sys.argv[1].lower()
    if command == 'list':
        list_tools()
    elif command == 'search':
        if len(sys.argv) < 3:
            print("用法: agent_toolkit search <关键词>")
        else:
            search_tools(' '.join(sys.argv[2:]))
    elif command == 'info':
        if len(sys.argv) < 3:
            print("用法: agent_toolkit info <名称>")
        else:
            show_info(sys.argv[2])
    elif command == 'install':
        if len(sys.argv) < 3:
            print("用法: agent_toolkit install <名称>")
        else:
            install_tool(sys.argv[2])
    elif command == 'uninstall':
        if len(sys.argv) < 3:
            print("用法: agent_toolkit uninstall <名称>")
        else:
            uninstall_tool(sys.argv[2])
    elif command == 'help':
        show_usage()
    else:
        print(f"未知命令: {command}")
        show_usage()
