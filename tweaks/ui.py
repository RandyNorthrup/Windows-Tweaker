from __future__ import annotations
from typing import List, Tuple
from .base import Tweak
from util import registry as r
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


def apply_transparency_effects(enable: bool) -> tuple[bool, str]:
    hkey = getattr(winreg, 'HKEY_CURRENT_USER', None)
    if hkey is None:
        return False, "Registry access not supported on this platform."
    return r.set_reg_value(hkey,
                           r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize",
                           "EnableTransparency", 1 if enable else 0)


def apply_taskbar_size(size: str) -> tuple[bool, str]:
    # 0=small, 1=medium (default), 2=large
    mapv = {"Small": 0, "Medium": 1, "Large": 2}
    val = mapv.get(size, 1)
    hkey = getattr(winreg, 'HKEY_CURRENT_USER', None)
    if hkey is None:
        return False, "Registry access not supported on this platform."
    return r.set_reg_value(hkey,
                           r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
                           "TaskbarSi", val)


def apply_show_file_extensions(show: bool) -> tuple[bool, str]:
    # HideFileExt: 0 = show, 1 = hide
    hkey = getattr(winreg, 'HKEY_CURRENT_USER', None)
    if hkey is None:
        return False, "Registry access not supported on this platform."
    return r.set_reg_value(hkey,
                           r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
                           "HideFileExt", 0 if show else 1)


def apply_show_hidden_files(show: bool) -> tuple[bool, str]:
    # Hidden: 1 = show, 2 = don't show
    hkey = getattr(winreg, 'HKEY_CURRENT_USER', None)
    if hkey is None:
        return False, "Registry access not supported on this platform."
    return r.set_reg_value(hkey,
                           r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
                           "Hidden", 1 if show else 2)


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
            id="transparency_effects",
            category="User Interface",
            label="Transparency effects",
            type="toggle",
            default=True,
            tooltip="Enable or disable system transparency effects.",
            apply=lambda v: apply_transparency_effects(v)
        ),
        Tweak(
            id="taskbar_size",
            category="User Interface",
            label="Taskbar size",
            type="dropdown",
            options=["Small", "Medium", "Large"],
            default="Medium",
            tooltip="Change Windows 11 taskbar size.",
            apply=lambda v: apply_taskbar_size(v)
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
            id="show_file_extensions",
            category="User Interface",
            label="Show file name extensions",
            type="toggle",
            default=True,
            tooltip="Show known file type extensions in File Explorer.",
            apply=lambda v: apply_show_file_extensions(v)
        ),
        Tweak(
            id="show_hidden_files",
            category="User Interface",
            label="Show hidden files",
            type="toggle",
            default=False,
            tooltip="Show hidden files and folders in File Explorer.",
            apply=lambda v: apply_show_hidden_files(v)
        ),
        Tweak(
            id="start_recommendations",
            category="User Interface",
            label="Hide Start menu recommendations",
            type="toggle",
            default=True,
            tooltip="Hide 'Recommended' items in Start (where supported).",
            apply=lambda v: apply_start_recommendations(v)
        ),
    ]

