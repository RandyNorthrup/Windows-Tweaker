from __future__ import annotations
import winreg
from typing import Any, Tuple

# Generic registry helpers returning (ok, message)

def set_reg_value(root, path: str, name: str, value: Any, reg_type=None) -> tuple[bool, str]:
    reg_type = reg_type or getattr(winreg, 'REG_DWORD', None)
    CreateKeyEx = getattr(winreg, 'CreateKeyEx', None)
    KEY_SET_VALUE = getattr(winreg, 'KEY_SET_VALUE', None)
    SetValueEx = getattr(winreg, 'SetValueEx', None)
    CloseKey = getattr(winreg, 'CloseKey', None)
    if None in (reg_type, CreateKeyEx, KEY_SET_VALUE, SetValueEx, CloseKey):
        return False, "Registry access not supported on this platform."
    try:
        if CreateKeyEx is None:
            return False, "Registry access not supported on this platform."
        key = CreateKeyEx(root, path, 0, KEY_SET_VALUE)
        if key is None:
            return False, "Registry access not supported on this platform."
        if SetValueEx is None or CloseKey is None:
            return False, "Registry access not supported on this platform."
        SetValueEx(key, name, 0, reg_type, value)
        CloseKey(key)
        return True, f"{path}::{name} set to {value}"
    except Exception as e:
        return False, f"reg set failed {path}::{name}: {e}"


def get_reg_value(root, path: str, name: str, default: Any = None) -> Any:
    OpenKey = getattr(winreg, 'OpenKey', None)
    KEY_READ = getattr(winreg, 'KEY_READ', None)
    QueryValueEx = getattr(winreg, 'QueryValueEx', None)
    CloseKey = getattr(winreg, 'CloseKey', None)
    if None in (OpenKey, KEY_READ, QueryValueEx, CloseKey):
        return default
    try:
        if OpenKey is None or KEY_READ is None:
            return default
        key = OpenKey(root, path, 0, KEY_READ)
        if key is None or QueryValueEx is None or CloseKey is None:
            return default
        val, _ = QueryValueEx(key, name)
        CloseKey(key)
        return val
    except FileNotFoundError:
        return default
    except Exception:
        return default


def delete_reg_value(root, path: str, name: str) -> tuple[bool, str]:
    OpenKey = getattr(winreg, 'OpenKey', None)
    KEY_SET_VALUE = getattr(winreg, 'KEY_SET_VALUE', None)
    DeleteValue = getattr(winreg, 'DeleteValue', None)
    CloseKey = getattr(winreg, 'CloseKey', None)
    if None in (OpenKey, KEY_SET_VALUE, DeleteValue, CloseKey):
        return False, "Registry access not supported on this platform."
    try:
        if OpenKey is None or KEY_SET_VALUE is None:
            return False, "Registry access not supported on this platform."
        key = OpenKey(root, path, 0, KEY_SET_VALUE)
        if key is None or DeleteValue is None or CloseKey is None:
            return False, "Registry access not supported on this platform."
        DeleteValue(key, name)
        CloseKey(key)
        return True, f"deleted {path}::{name}"
    except FileNotFoundError:
        return True, f"not present {path}::{name}"
    except Exception as e:
        return False, f"reg delete failed {path}::{name}: {e}"

