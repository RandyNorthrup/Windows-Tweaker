from __future__ import annotations
from typing import List, Tuple
from .base import Tweak
from util.ps import ps
from util import registry as r
import winreg

# ---- Windows Update implementations ----

WU_AU = r"SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU"
UX_SETTINGS = r"SOFTWARE\Microsoft\WindowsUpdate\UX\Settings"


def apply_wu_mode(mode: str) -> tuple[bool, str]:
    # Map GUI selection to policy values
    # 2 = notify before download (NoAutoUpdate=0, AUOptions=2)
    # 3 = auto download and notify for install (AUOptions=3)
    # 4 = auto download and schedule install (AUOptions=4)
    hkey = getattr(winreg, 'HKEY_LOCAL_MACHINE', None)
    if hkey is None:
        return False, "Registry access not supported on this platform."
    if mode == "Default (Windows decides)":
        # Remove policies
        ok1, m1 = r.delete_reg_value(hkey, WU_AU, "NoAutoUpdate")
        ok2, m2 = r.delete_reg_value(hkey, WU_AU, "AUOptions")
        return (ok1 and ok2), f"{m1}; {m2}"
    if mode == "Notify before download":
        ok1, m1 = r.set_reg_value(hkey, WU_AU, "NoAutoUpdate", 0)
        ok2, m2 = r.set_reg_value(hkey, WU_AU, "AUOptions", 2)
        return (ok1 and ok2), f"{m1}; {m2}"
    if mode == "Auto download, schedule install":
        ok1, m1 = r.set_reg_value(hkey, WU_AU, "NoAutoUpdate", 0)
        ok2, m2 = r.set_reg_value(hkey, WU_AU, "AUOptions", 4)
        return (ok1 and ok2), f"{m1}; {m2}"
    if mode == "Disable (not recommended)":
        ok1, m1 = r.set_reg_value(hkey, WU_AU, "NoAutoUpdate", 1)
        ok2, m2 = r.delete_reg_value(hkey, WU_AU, "AUOptions")
        return (ok1 and ok2), f"{m1}; {m2}"
    return False, "unknown mode"


def apply_active_hours_start(start_h: int) -> tuple[bool, str]:
    hkey = getattr(winreg, 'HKEY_LOCAL_MACHINE', None)
    if hkey is None:
        return False, "Registry access not supported on this platform."
    ok1, m1 = r.set_reg_value(hkey, UX_SETTINGS, "ActiveHoursStart", int(start_h))
    ok2, m2 = r.set_reg_value(hkey, UX_SETTINGS, "IsActiveHoursEnabled", 1)
    return (ok1 and ok2), f"{m1}; {m2}"


def apply_active_hours_end(end_h: int) -> tuple[bool, str]:
    hkey = getattr(winreg, 'HKEY_LOCAL_MACHINE', None)
    if hkey is None:
        return False, "Registry access not supported on this platform."
    return r.set_reg_value(hkey, UX_SETTINGS, "ActiveHoursEnd", int(end_h))


def apply_driver_updates(include: bool) -> tuple[bool, str]:
    # Windows 11 22H2+ exposes driver updates toggle via policy
    val = 0 if include else 1
    hkey = getattr(winreg, 'HKEY_LOCAL_MACHINE', None)
    if hkey is None:
        return False, "Registry access not supported on this platform."
    return r.set_reg_value(hkey,
                           r"SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate",
                           "ExcludeWUDriversInQualityUpdate", val)


def get_tweaks() -> List[Tweak]:
    return [
        Tweak(
            id="wu_mode",
            category="Windows Update",
            label="Mode",
            type="dropdown",
            options=[
                "Default (Windows decides)",
                "Notify before download",
                "Auto download, schedule install",
                "Disable (not recommended)",
            ],
            default="Default (Windows decides)",
            tooltip="Choose how Windows obtains and installs updates.",
            warning="Disabling updates reduces security.",
            apply=lambda v: apply_wu_mode(v)
        ),
        Tweak(
            id="active_start",
            category="Windows Update",
            label="Active hours start",
            type="number",
            minimum=0, maximum=23, step=1,
            default=8,
            tooltip="Start of Active Hours to avoid restarts.",
            apply=lambda v: apply_active_hours_start(v)
        ),
        Tweak(
            id="active_end",
            category="Windows Update",
            label="Active hours end",
            type="number",
            minimum=0, maximum=23, step=1,
            default=20,
            tooltip="End of Active Hours to avoid restarts.",
            apply=lambda v: apply_active_hours_end(v)
        ),
        Tweak(
            id="driver_updates",
            category="Windows Update",
            label="Include driver updates",
            type="toggle",
            default=True,
            tooltip="Include drivers in Windows Update.",
            apply=lambda v: apply_driver_updates(v)
        ),
    ]
