# NZ06 Robot Control

## 描述
NZ06 机器人控制工具，使用隔离的 Git/SVN 源码检出，运行项目 Web UI，检查机器人串口后进行硬件显示。

## 环境要求

| 组件 | 要求 |
|------|------|
| Git | 已安装 |
| Conda | 环境 nz06-gui (Python 3.10) |
| PowerShell | Windows 自带 |
| pyserial | pip install pyserial |

## 环境变量

- `NZ06_GIT_URL` - GitHub 仓库地址
- `NZ06_SVN_URL` - SVN 仓库地址
- `NZ06_CONDA_ENV` - Conda 环境名 (nz06-gui)
- `NZ06_CONDA_PATH` - Conda 安装路径
- `NZ06_PORT` - 串口 (COM3)
- `NZ06_BAUDRATE` - 波特率 (1000000)
- `NZ06_WEB_PORT` - Web 端口 (8766)

## 支持的 Action

- `start/stop/status` - Web UI 管理
- `connect/disconnect` - 串口连接
- `set_target/simulate/execute` - 目标点控制
- `move_joints` - 关节移动
- `execute_sequence` - 序列执行
- `update` - 源码更新

## 使用示例

```python
# 启动 Web UI
tool = "nz06_robot_control"
args = {"action": "start"}

# 连接机器人
tool = "nz06_robot_control"
args = {"action": "connect", "port": "COM3"}

# 设置目标点
tool = "nz06_robot_control"
args = {"action": "set_target", "target": [100, 200, 300]}
```
