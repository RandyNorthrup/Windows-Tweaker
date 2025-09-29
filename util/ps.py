from __future__ import annotations
import subprocess
from typing import Tuple

# PowerShell helpers

def ps(cmd: str) -> tuple[bool, str]:
    """Run a PowerShell command; returns (ok, output_or_error)."""
    try:
        cp = subprocess.run([
            "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", cmd
        ], capture_output=True, text=True)
        if cp.returncode == 0:
            return True, (cp.stdout or "ok").strip()
        else:
            return False, (cp.stderr or cp.stdout or "error").strip()
    except Exception as e:
        return False, str(e)


def checkpoint(description: str = "Windows11Tweaker") -> tuple[bool, str]:
    # Create a system restore point (works if Protection is enabled)
    cmd = f"Checkpoint-Computer -Description '{description}' -RestorePointType 'MODIFY_SETTINGS'"
    return ps(cmd)


def restart_explorer() -> tuple[bool, str]:
    """Restart Windows Explorer cleanly."""
    # Use PowerShell to stop and start explorer.exe reliably
    cmd = (
        "Stop-Process -Name explorer -Force -ErrorAction SilentlyContinue; "
        "Start-Process explorer.exe"
    )
    return ps(cmd)
