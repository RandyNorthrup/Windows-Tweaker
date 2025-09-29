from __future__ import annotations
from typing import List, Tuple
from .base import Tweak
from util import registry as r
import winreg

# ---- Privacy tweak implementations ----

def apply_telemetry(level: str) -> tuple[bool, str]:
    # 0: Security, 1: Basic, 2: Enhanced, 3: Full
    mapv = {
        "Security (minimal)": 0,
        "Basic": 1,
        "Enhanced": 2,
        "Optional (Full)": 3,
    }
    v = mapv.get(level, 1)
    hkey = getattr(winreg, 'HKEY_LOCAL_MACHINE', None)
    regtype = getattr(winreg, 'REG_DWORD', None)
    if hkey is None or regtype is None:
        return False, "Registry access not supported on this platform."
    return r.set_reg_value(hkey,
                           r"SOFTWARE\Policies\Microsoft\Windows\DataCollection",
                           "AllowTelemetry", int(v), regtype)


def apply_ads_id(disable: bool) -> tuple[bool, str]:
    hkey = getattr(winreg, 'HKEY_CURRENT_USER', None)
    regtype = getattr(winreg, 'REG_DWORD', None)
    if hkey is None or regtype is None:
        return False, "Registry access not supported on this platform."
    return r.set_reg_value(hkey,
                           r"SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo",
                           "Enabled", 0 if disable else 1, regtype)


def apply_suggestions(disable: bool) -> tuple[bool, str]:
    # Hide suggestions in Settings (experience may vary by build)
    hkey = getattr(winreg, 'HKEY_CURRENT_USER', None)
    regtype = getattr(winreg, 'REG_DWORD', None)
    if hkey is None or regtype is None:
        return False, "Registry access not supported on this platform."
    return r.set_reg_value(hkey,
                           r"Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
                           "SubscribedContent-338389Enabled", 0 if disable else 1, regtype)


def apply_location_service(disable: bool) -> tuple[bool, str]:
    hkey = getattr(winreg, 'HKEY_LOCAL_MACHINE', None)
    regtype = getattr(winreg, 'REG_DWORD', None)
    if hkey is None or regtype is None:
        return False, "Registry access not supported on this platform."
    return r.set_reg_value(hkey,
                           r"SYSTEM\CurrentControlSet\Services\lfsvc\Service\Configuration",
                           "Status", 0 if disable else 1, regtype)


def apply_background_cam_mic(block: bool) -> tuple[bool, str]:
    # Privacy consent policy for background app access is app-scoped in many cases; provide a global default
    hkey = getattr(winreg, 'HKEY_LOCAL_MACHINE', None)
    regtype = getattr(winreg, 'REG_SZ', None)
    if hkey is None or regtype is None:
        return False, "Registry access not supported on this platform."
    ok1, m1 = r.set_reg_value(hkey,
                              r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\microphone",
                              "Value", "Deny" if block else "Allow", regtype)
    ok2, m2 = r.set_reg_value(hkey,
                              r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\webcam",
                              "Value", "Deny" if block else "Allow", regtype)
    return (ok1 and ok2), f"mic: {m1}; cam: {m2}"


# ---- Export tweak list ----

def get_tweaks() -> List[Tweak]:
    return [
        Tweak(
            id="telemetry_level",
            category="Privacy",
            label="Telemetry level",
            type="dropdown",
            options=["Security (minimal)", "Basic", "Enhanced", "Optional (Full)"],
            default="Security (minimal)",
            tooltip="Controls Windows diagnostic data level.",
            warning="Major updates may revert this.",
            apply=lambda v: apply_telemetry(v)
        ),
        Tweak(
            id="ads_id",
            category="Privacy",
            label="Disable Advertising ID",
            type="toggle",
            default=True,
            tooltip="Prevents apps using the advertising identifier.",
            apply=lambda v: apply_ads_id(v)
        ),
        Tweak(
            id="suggestions",
            category="Privacy",
            label="Disable Suggested content in Settings",
            type="toggle",
            default=True,
            tooltip="Hides Microsoft suggestions and tips in Settings panes.",
            apply=lambda v: apply_suggestions(v)
        ),
        Tweak(
            id="location_service",
            category="Privacy",
            label="Disable Location service",
            type="toggle",
            default=False,
            tooltip="Turns off system location service.",
            apply=lambda v: apply_location_service(v)
        ),
        Tweak(
            id="background_cam_mic",
            category="Privacy",
            label="Block Camera/Mic for background apps",
            type="toggle",
            default=True,
            tooltip="Restricts background access (foreground apps still prompt).",
            apply=lambda v: apply_background_cam_mic(v)
        ),
    ]
