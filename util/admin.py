from __future__ import annotations
import ctypes, sys, subprocess
from typing import Tuple

UAC_PROMPT_SHOWN = False


def is_admin() -> bool:
    try:
        if sys.platform != "win32":
            return False
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def ensure_admin(relaunch_args: str = "") -> Tuple[bool, str]:
    """Ensure the process is elevated. If not, try to relaunch with UAC.
    Returns (ok, message). If relaunch is attempted, returns (False, "relaunching")."""
    global UAC_PROMPT_SHOWN
    if is_admin():
        return True, "already elevated"
    try:
        if sys.platform != "win32":
            return False, "Elevation is only supported on Windows."
        # Use ShellExecuteW to prompt for elevation
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, relaunch_args or " ".join(sys.argv), None, 1)
        UAC_PROMPT_SHOWN = True
        return False, "relaunching as admin"
    except Exception as e:
        return False, f"elevation failed: {e}"


def run(cmd: list[str] | str, check: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, shell=isinstance(cmd, str), check=check)

