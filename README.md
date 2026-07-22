# AGENT_TOOLS

Agent 工具和技巧共享仓库，通过 GitHub API 提供工具浏览、搜索、安装和卸载功能。

## 仓库结构

```
├── README.md           # 本文件
├── schema.json         # 工具元数据 schema
├── tools/              # 工具目录
│   ├── _template/      # 新工具模板
│   ├── hello-world/    # 示例工具
│   └── nz06_robot_control/  # NZ06 机器人控制工具
└── skills/             # 技巧目录
    ├── _template/      # 新技巧模板
    └── python-best-practices/  # Python 最佳实践
```

## 工具创建规则

### 1. 目录结构

每个工具/技巧位于独立目录：

```
tools/<tool-name>/
├── manifest.json       # 必填：元数据
├── install.json        # 可选：安装规则
├── README.md           # 推荐：使用说明
└── <其他文件>
```

### 2. manifest.json 格式

```json
{
  "name": "工具名称",
  "version": "1.0.0",
  "type": "tool",
  "description": "工具描述",
  "author": "作者名",
  "email": "email@example.com",
  "date": "2026-07-15",
  "tags": ["tag1", "tag2"],
  "dependencies": ["pyserial"],
  "python_version": ">=3.8",
  "files": ["main.py", "utils.py"],
  "readme": "README.md"
}
```

必填字段：name, version, type, description, author

### 3. install.json 格式（可选）

```json
{
  "pre_install": ["pip install pyserial"],
  "register_tool": {
    "name": "tool_name",
    "description": "工具描述",
    "python_code": "from main import run"
  }
}
```

### 4. 上传新工具

1. 在 `tools/` 或 `skills/` 下创建目录
2. 添加 `manifest.json` 和必要文件
3. git commit 并 push

## 使用方式

通过 Agent Dashboard 的 `agent_toolkit` App 访问：
1. 启动代理服务器：`python apps/toolkit_proxy.py 8767`
2. 打开 Dashboard → Apps → agent_toolkit
3. 浏览、搜索、安装工具

## API 端点

- `GET /api/tools` - 获取工具列表
- `GET /api/skills` - 获取技巧列表
- `GET /api/installed` - 获取已安装工具
- `POST /api/install` - 安装工具
- `POST /api/uninstall` - 卸载工具
- `GET /api/content/<path>` - 获取文件内容
