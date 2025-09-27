from __future__ import annotations
import importlib, pkgutil
from typing import List, Dict
from .base import Tweak, Category

__all__ = ["load_all_tweaks", "group_by_category"]


def load_all_tweaks() -> List[Tweak]:
    tweaks: List[Tweak] = []
    pkg = __name__
    for _, modname, ispkg in pkgutil.iter_modules(__path__):
        if ispkg or modname in {"base"}:  # skip internal helper
            continue
        mod = importlib.import_module(f"{pkg}.{modname}")
        if hasattr(mod, "get_tweaks"):
            tweaks.extend(mod.get_tweaks())
    return tweaks


def group_by_category(items: List[Tweak]) -> Dict[Category, List[Tweak]]:
    g: Dict[Category, List[Tweak]] = {}
    for t in items:
        g.setdefault(t.category, []).append(t)
    for k in g:
        g[k].sort(key=lambda x: x.label.lower())
    return g