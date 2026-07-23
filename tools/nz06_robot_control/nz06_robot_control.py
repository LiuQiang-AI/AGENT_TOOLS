
import json
import os
import shutil
import socket
import subprocess
import time
import urllib.request
from pathlib import Path
from typing import Any

GITHUB_URL = 'https://github.com/LiuQiang-AI/nz06_robot_control_project.git'
SVN_URL = 'svn://203.166.186.80:3691/QHYCCD/LQ_WorkSpace/nz06_robot_control_project'
DEFAULT_CONDA_ENV = 'nz06-gui'
DEFAULT_WEB_PORT = 8766
DEFAULT_DASHBOARD_PORT = 8765
_server_port = None


def run(state: Any, **kwargs) -> Any:
    action = str(kwargs.get('action') or 'status').strip()
    try:
        if action == 'ensure_source':
            return _ensure_source_result(**kwargs)
        if action == 'update':
            return _update(**kwargs)
        if action == 'start':
            return _start_server(**kwargs)
        if action == 'stop':
            return _stop_server(**kwargs)
        if action == 'status':
            return _get_status(**kwargs)
        if action == 'get_port':
            return _get_port_result(**kwargs)
        if action == 'connect':
            return _connect(**kwargs)
        if action == 'disconnect':
            return _send_command('disconnect', {}, **kwargs)
        if action == 'set_target':
            return _send_command('set_target', {'target': kwargs.get('target', [0.0, 0.0, 0.3])}, **kwargs)
        if action == 'simulate':
            return _send_command('simulate', {}, **kwargs)
        if action == 'execute':
            dry_run = bool(kwargs.get('dry_run', False))
            if not dry_run:
                _send_command('set_dry_run', {'value': False}, **kwargs)
            return _send_command('execute', {'dry_run': dry_run}, **kwargs)
        if action == 'go_home':
            dry_run = bool(kwargs.get('dry_run', False))
            if not dry_run:
                _send_command('set_dry_run', {'value': False}, **kwargs)
            return _send_command('home', {'dry_run': dry_run}, **kwargs)
        if action == 'stop_hardware':
            return _send_command('stop', {}, **kwargs)
        if action == 'move_joints':
            args = {'joint_index': int(kwargs.get('joint_index', 0)), 'target_deg': float(kwargs.get('target_deg', 0)), 'dry_run': bool(kwargs.get('dry_run', False))}
            if not args['dry_run']:
                _send_command('set_dry_run', {'value': False}, **kwargs)
            return _send_command('execute_single_joint', args, **kwargs)
        if action == 'refresh':
            return _send_command('refresh', {}, **kwargs)
        if action == 'set_follow':
            return _send_command('set_follow', {'value': bool(kwargs.get('value', False))}, **kwargs)
        if action == 'set_collision_engine':
            return _send_command('set_collision_engine', {'engine': kwargs.get('engine', 'mesh_obb')}, **kwargs)
        if action == 'follow_target_once':
            return _send_command('follow_target_once', {}, **kwargs)
        if action == 'save_home':
            return _send_command('save_home', {}, **kwargs)
        if action == 'execute_return':
            return _send_command('execute_return', {'dry_run': bool(kwargs.get('dry_run', False))}, **kwargs)
        if action == 'sync_joints':
            return _send_command('sync_joints', {}, **kwargs)
        if action == 'preview_single_joint':
            return _send_command('preview_single_joint', {'joint_index': int(kwargs.get('joint_index', 0)), 'target_deg': float(kwargs.get('target_deg', 0))}, **kwargs)
        if action == 'execute_single_joint':
            return _send_command('execute_single_joint', {'joint_index': int(kwargs.get('joint_index', 0)), 'target_deg': float(kwargs.get('target_deg', 0)), 'dry_run': bool(kwargs.get('dry_run', False))}, **kwargs)
        supported = 'start, stop, status, get_port, connect, disconnect, set_target, simulate, execute, go_home, stop_hardware, move_joints, refresh, set_follow, set_collision_engine, follow_target_once, save_home, execute_return, sync_joints, preview_single_joint, execute_single_joint, add_sequence_point, add_sequence_points, execute_sequence, clear_sequence, update, ensure_source'
        if action == 'add_sequence_point':
            return _send_command('add_sequence_point', {'target': kwargs.get('target', [0.0, 0.0, 0.3])}, **kwargs)
        if action == 'add_sequence_points':
            return _send_command('add_sequence_points', {'points': kwargs.get('points', [])}, **kwargs)
        if action == 'execute_sequence':
            dry_run = bool(kwargs.get('dry_run', False))
            if not dry_run:
                _send_command('set_dry_run', {'value': False}, **kwargs)
            return _send_command('execute_sequence', {'dry_run': dry_run}, **kwargs)
        if action == 'clear_sequence':
            return _send_command('clear_sequence', {'keep_running': bool(kwargs.get('keep_running', False))}, **kwargs)
        return ToolResult(success=False, output=f'Unknown action: {action}', error=f'Supported actions: {supported}')
    except Exception as exc:
        return ToolResult(success=False, output=f'NZ06 tool failed: {exc}', error=str(exc))


def _tool_workspace() -> Path:
    base = os.environ.get('NZ06_TOOL_WORKSPACE')
    if base:
        return Path(base).expanduser().resolve()
    return (Path.cwd() / 'tools_workspace' / 'nz06_robot_control_project').resolve()


def _run(cmd, cwd=None, timeout=120):
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=timeout)


def _state_file() -> Path:
    return (_tool_workspace().parent / 'nz06_robot_control_state.json').resolve()


def _save_port(port, url=None, source='detected'):
    try:
        data = {'web_port': int(port), 'url': url or f'http://127.0.0.1:{int(port)}', 'source': source, 'updated_at': time.time()}
        fp = _state_file()
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    except Exception:
        pass


def _load_saved_port():
    try:
        fp = _state_file()
        if not fp.exists():
            return None
        data = json.loads(fp.read_text(encoding='utf-8'))
        port = int(data.get('web_port'))
        return port
    except Exception:
        return None


def _get_port_result(**kwargs):
    live_port = _get_web_port(kwargs.get('web_port'))
    saved_port = _load_saved_port()
    port = live_port or saved_port
    if live_port:
        _save_port(live_port, source='live_probe')
    return ToolResult(success=bool(port), output={'web_port': port, 'url': f'http://127.0.0.1:{port}' if port else None, 'live': bool(live_port), 'state_file': str(_state_file())}, error='' if port else 'NZ06 control port is unknown')


def _source_backend(**kwargs) -> str:
    return str(kwargs.get('source') or os.environ.get('NZ06_SOURCE') or 'github').strip().lower()


def _ensure_source(**kwargs):
    project = _tool_workspace()
    source = _source_backend(**kwargs)
    project.parent.mkdir(parents=True, exist_ok=True)
    if (project / 'pyproject.toml').exists() and (project / 'src' / 'nz06_control').exists():
        if (project / '.git').exists():
            result = _run(['git', 'pull', '--ff-only'], cwd=project, timeout=180)
            if result.returncode == 0:
                return True, f'Git checkout ready and updated: {project}', project
            return True, f'Git checkout exists, pull skipped/failed: {(result.stderr or result.stdout).strip()}', project
        if (project / '.svn').exists():
            result = _run(['svn', 'update'], cwd=project, timeout=180)
            if result.returncode == 0:
                return True, f'SVN checkout ready and updated: {project}', project
            return True, f'SVN checkout exists, update skipped/failed: {(result.stderr or result.stdout).strip()}', project
        return True, f'Existing NZ06 project found: {project}', project
    if project.exists() and any(project.iterdir()):
        return False, f'Workspace path exists but is not an NZ06 checkout: {project}', project
    if source == 'svn':
        if not shutil.which('svn'):
            return False, 'svn executable was not found in PATH', project
        result = _run(['svn', 'checkout', SVN_URL, str(project)], timeout=600)
    else:
        if not shutil.which('git'):
            return False, 'git executable was not found in PATH', project
        result = _run(['git', 'clone', GITHUB_URL, str(project)], timeout=600)
    if result.returncode != 0:
        return False, (result.stderr or result.stdout or 'checkout failed').strip(), project
    return True, f'{source} checkout created: {project}', project


def _ensure_source_result(**kwargs):
    ok, msg, project = _ensure_source(**kwargs)
    return ToolResult(success=ok, output={'message': msg, 'project_path': str(project)}, error='' if ok else msg)


def _update(**kwargs):
    ok, msg, project = _ensure_source(**kwargs)
    return ToolResult(success=ok, output={'message': msg, 'project_path': str(project)}, error='' if ok else msg)


def _conda_env() -> str:
    return os.environ.get('NZ06_CONDA_ENV', DEFAULT_CONDA_ENV)


def _check_conda_env(conda_env: str):
    result = _run(['conda', 'env', 'list'], timeout=20)
    if result.returncode != 0:
        return False, result.stderr.strip() or 'conda env list failed'
    if conda_env in result.stdout:
        return True, f'conda env exists: {conda_env}'
    return False, f'conda env missing: {conda_env}'


def _create_conda_env(project: Path, conda_env: str):
    result = _run(['conda', 'create', '-y', '-n', conda_env, 'python=3.10'], timeout=900)
    if result.returncode != 0:
        return False, result.stderr.strip() or result.stdout.strip()
    install = _run(['conda', 'run', '-n', conda_env, 'python', '-m', 'pip', 'install', '-r', str(project / 'requirements.txt'), '-e', str(project)], timeout=900)
    if install.returncode != 0:
        return False, install.stderr.strip() or install.stdout.strip()
    return True, f'conda env created and project installed: {conda_env}'


def _ensure_env(project: Path, **kwargs):
    conda_env = _conda_env()
    ok, msg = _check_conda_env(conda_env)
    if ok:
        return True, msg
    if kwargs.get('create_env', True) is False:
        return False, msg
    return _create_conda_env(project, conda_env)


def _check_serial_port(port='COM3', baudrate=1000000):
    try:
        import serial as serial_module
    except Exception:
        return _check_serial_port_with_conda(port, baudrate)
    try:
        with serial_module.Serial(port, int(baudrate), timeout=1, write_timeout=1):
            return True, f'serial port available: {port}'
    except Exception as exc:
        return False, f'serial port precheck failed for {port}: {exc}'


def _check_serial_port_with_conda(port='COM3', baudrate=1000000):
    code = "import sys, serial; ser=serial.Serial(sys.argv[1], int(sys.argv[2]), timeout=1, write_timeout=1); ser.close(); print('ok')"
    result = _run(['conda', 'run', '-n', _conda_env(), 'python', '-c', code, str(port), str(int(baudrate))], timeout=20)
    if result.returncode == 0:
        return True, f'serial port available: {port}'
    return False, f'serial port precheck failed for {port}: {(result.stderr or result.stdout).strip()}'


def _test_nz06_port(port) -> bool:
    try:
        req = urllib.request.Request(f'http://127.0.0.1:{int(port)}/api/state')
        with urllib.request.urlopen(req, timeout=2) as response:
            data = json.loads(response.read().decode('utf-8'))
        return isinstance(data, dict) and ('joints_deg' in data or 'hardware_enabled' in data)
    except Exception:
        return False


def _get_web_port(preferred_port=None):
    global _server_port
    candidates = []
    for value in [preferred_port, _server_port, DEFAULT_WEB_PORT, 8765, 8767, 8876]:
        if value is None:
            continue
        try:
            value = int(value)
        except Exception:
            continue
        if value not in candidates:
            candidates.append(value)
    for port in candidates:
        if _test_nz06_port(port):
            _server_port = port
            _save_port(port, source='probe')
            return port
    saved_port = _load_saved_port()
    if saved_port and saved_port not in candidates and _test_nz06_port(saved_port):
        _server_port = saved_port
        _save_port(saved_port, source='saved_probe')
        return saved_port
    return None


def _wait_for_server(preferred_port, timeout=25):
    deadline = time.time() + timeout
    while time.time() < deadline:
        port = _get_web_port(preferred_port)
        if port:
            return port
        time.sleep(0.5)
    return None


def _dashboard_port(**kwargs) -> int:
    return int(kwargs.get('dashboard_port') or os.environ.get('DASHBOARD_PORT') or DEFAULT_DASHBOARD_PORT)


def _open_agent_view(url: str, title='NZ06 Robot Control', display_id='nz06_robot_control', **kwargs):
    payload = json.dumps({'url': url, 'title': title, 'display_id': display_id}).encode('utf-8')
    req = urllib.request.Request(f'http://127.0.0.1:{_dashboard_port(**kwargs)}/api/open-view', data=payload, headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=3) as response:
            response.read()
        return True, f'opened agent browser view: {url}'
    except Exception as exc:
        return False, f'could not open agent browser view automatically: {exc}; url={url}'


def _start_server(**kwargs):
    global _server_port
    ok, source_msg, project = _ensure_source(**kwargs)
    if not ok:
        return ToolResult(success=False, output=source_msg, error=source_msg)
    env_ok, env_msg = _ensure_env(project, **kwargs)
    if not env_ok:
        return ToolResult(success=False, output=env_msg, error=env_msg)
    serial_port = kwargs.get('port', os.environ.get('NZ06_SERIAL_PORT', 'COM3'))
    baudrate = int(kwargs.get('baudrate', os.environ.get('NZ06_BAUDRATE', 1000000)))
    requested_web_port = int(kwargs.get('web_port', os.environ.get('NZ06_WEB_PORT', DEFAULT_WEB_PORT)))
    existing_port = _get_web_port(requested_web_port)
    if existing_port:
        url = f'http://127.0.0.1:{existing_port}'
        _save_port(existing_port, url, source='existing_service')
        try:
            existing_state = _read_state(existing_port)
        except Exception:
            existing_state = {}
        existing_serial = existing_state.get('serial', {}) if isinstance(existing_state, dict) else {}
        existing_port_name = str(existing_serial.get('port') or '').upper()
        requested_port_name = str(serial_port).upper()
        if existing_state.get('hardware_enabled') or existing_port_name == requested_port_name:
            port_msg = f'NZ06 service already owns/checks {existing_serial.get("port") or serial_port}'
            view_ok, view_msg = _open_agent_view(url, **kwargs)
            return ToolResult(success=True, output={'message': 'NZ06 web server already running', 'url': url, 'view': view_msg, 'serial': port_msg, 'project_path': str(project)}, error='' if view_ok else view_msg)
    port_ok, port_msg = _check_serial_port(serial_port, baudrate)
    if not port_ok:
        return ToolResult(success=False, output={'source': source_msg, 'env': env_msg, 'serial': port_msg}, error=port_msg)
    cmd = ['conda', 'run', '-n', _conda_env(), 'python', '-m', 'nz06_control.app', '--web', '--config', str(project / 'config' / 'default.yaml'), '--serial-port', str(serial_port), '--web-host', '127.0.0.1', '--web-port', str(requested_web_port)]
    process = subprocess.Popen(cmd, cwd=str(project), stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    actual_port = _wait_for_server(requested_web_port, timeout=int(kwargs.get('startup_timeout', 30)))
    if not actual_port:
        if process.poll() is not None:
            stdout, stderr = process.communicate(timeout=3)
            msg = f'NZ06 web server exited. stdout={stdout} stderr={stderr}'
        else:
            msg = 'NZ06 web server did not become ready in time'
        return ToolResult(success=False, output=msg, error=msg)
    _server_port = actual_port
    url = f'http://127.0.0.1:{actual_port}'
    _save_port(actual_port, url, source='started_service')
    if kwargs.get('auto_connect', True):
        _send_command('connect', {'port': serial_port, 'baudrate': baudrate}, web_port=actual_port)
    view_ok, view_msg = _open_agent_view(url, **kwargs)
    return ToolResult(success=True, output={'message': 'NZ06 web server started', 'url': url, 'view': view_msg, 'serial': port_msg, 'env': env_msg, 'source': source_msg, 'project_path': str(project)}, error='' if view_ok else view_msg)


def _stop_server(**kwargs):
    actual_port = _get_web_port(kwargs.get('web_port'))
    if actual_port:
        try:
            _send_command('stop', {}, web_port=actual_port)
        except Exception:
            pass
    try:
        ps = "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object { $_.CommandLine -like '*nz06_control.app*--web*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"
        _run(['powershell', '-NoProfile', '-Command', ps], timeout=20)
    except Exception as exc:
        return ToolResult(success=False, output=f'stop failed: {exc}', error=str(exc))
    return ToolResult(success=True, output='NZ06 web server stop requested', error='')


def _get_status(**kwargs):
    ok, source_msg, project = _ensure_source(**kwargs)
    env_ok, env_msg = _check_conda_env(_conda_env())
    actual_port = _get_web_port(kwargs.get('web_port'))
    serial_port = kwargs.get('port', os.environ.get('NZ06_SERIAL_PORT', 'COM3'))
    baudrate = int(kwargs.get('baudrate', os.environ.get('NZ06_BAUDRATE', 1000000)))
    port_ok, port_msg = _check_serial_port(serial_port, baudrate) if kwargs.get('check_serial', False) else (None, 'serial precheck not requested')
    state_data = _read_state(actual_port) if actual_port else None
    return ToolResult(success=True, output={'project_ready': ok, 'project_path': str(project), 'source': source_msg, 'conda_env': env_msg, 'serial': port_msg, 'web_port': actual_port, 'web_state': state_data}, error='' if ok and env_ok else (source_msg if not ok else env_msg))


def _read_state(port: int):
    req = urllib.request.Request(f'http://127.0.0.1:{int(port)}/api/state')
    with urllib.request.urlopen(req, timeout=5) as response:
        return json.loads(response.read().decode('utf-8'))


def _send_command(command: str, args=None, **kwargs):
    actual_port = _get_web_port(kwargs.get('web_port'))
    if not actual_port:
        return ToolResult(success=False, output='NZ06 web server is not running. Call action=start first.', error='NZ06 service not found')
    payload = {'command': command, 'args': args or {}}
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(f'http://127.0.0.1:{actual_port}/api/command', data=data, headers={'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(req, timeout=int(kwargs.get('timeout', 60))) as response:
        result = json.loads(response.read().decode('utf-8'))
    ok = bool(result.get('ok', True))
    return ToolResult(success=ok, output={'web_port': actual_port, 'command': command, 'result': result}, error='' if ok else str(result.get('message') or result))


def _connect(**kwargs):
    serial_port = kwargs.get('port', os.environ.get('NZ06_SERIAL_PORT', 'COM3'))
    baudrate = int(kwargs.get('baudrate', os.environ.get('NZ06_BAUDRATE', 1000000)))
    port_ok, port_msg = _check_serial_port(serial_port, baudrate)
    if not port_ok:
        return ToolResult(success=False, output=port_msg, error=port_msg)
    return _send_command('connect', {'port': serial_port, 'baudrate': baudrate}, **kwargs)
