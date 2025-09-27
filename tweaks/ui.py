from __future__ import annotations
from typing import List, Tuple
from .base import Tweak
from ..util import registry as r
import winreg

# ---- UI implementations ----

def apply_color_mode(mode: str) -> tuple[bool, str]:
    # Light/Dark via Personalize keys
    # 1 = Light, 0 = Dark
    app_light = 1 if mode in ("Light", "Auto (system)") else 0
    sys_light = 1 if mode in ("Light", "Auto (system)") else 0
    hkey = getattr(winreg, 'HKEY_CURRENT_USER', None)
    if hkey is None:
        return False, "Registry access not supported on this platform."
    ok1, m1 = r.set_reg_value(hkey,
                              r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize",
                              "AppsUseLightTheme", app_light)
    ok2, m2 = r.set_reg_value(hkey,
                              r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize",
                              "SystemUsesLightTheme", sys_light)
    return (ok1 and ok2), f"{m1}; {m2}"


def apply_taskbar_alignment(align: str) -> tuple[bool, str]:
    # 0 = left, 1 = center
    val = 1 if align == "Center" else 0
    hkey = getattr(winreg, 'HKEY_CURRENT_USER', None)
    if hkey is None:
        return False, "Registry access not supported on this platform."
    return r.set_reg_value(hkey,
                           r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
                           "TaskbarAl", val)


def apply_start_recommendations(hide: bool) -> tuple[bool, str]:
    hkey = getattr(winreg, 'HKEY_CURRENT_USER', None)
    if hkey is None:
        return False, "Registry access not supported on this platform."
    return r.set_reg_value(hkey,
                           r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer",
                           "HideRecommendedSection", 1 if hide else 0)

# Transparency/corner radius are app-surface hints for this app; for system-level acrylic intensity there isn't a single stable knob.


def get_tweaks() -> List[Tweak]:
    return [
        Tweak(
            id="color_mode",
            category="User Interface",
            label="Color mode",
            type="dropdown",
            options=["Light", "Dark", "Auto (system)"],
            default="Light",
            tooltip="Sets light/dark for apps and system.",
            apply=lambda v: apply_color_mode(v)
        ),
        Tweak(
            id="transparency",
            category="User Interface",
            label="Transparency (app UI only)",
            type="slider",
            minimum=0, maximum=100, step=1,
            default=20,
            tooltip="Visual effect for this app; not a global OS setting.",
            apply=lambda v: (True, f"ui transparency {v}%")
        ),
        Tweak(
            id="corner_radius",
            category="User Interface",
            label="Corner radius (app UI only)",
            type="number",
            minimum=0, maximum=24, step=1,
            default=12,
            tooltip="Affects this app's surfaces only.",
            apply=lambda v: (True, f"corner radius {v}px")
        ),
        Tweak(
            id="taskbar_align",
            category="User Interface",
            label="Taskbar alignment",
            type="dropdown",
            options=["Center", "Left"],
            default="Center",
            tooltip="Align taskbar icons.",
            apply=lambda v: apply_taskbar_alignment(v)
        ),
        Tweak(
            id="start_recommendations",
            category="User Interface",
            label="Hide Start menu recommendations",
            type="toggle",
            default=True,
            tooltip="Removes ‘Recommended’ items from Start (where supported).",
            apply=lambda v: apply_start_recommendations(v)
        ),
    ]