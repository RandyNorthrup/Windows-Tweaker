from __future__ import annotations
from typing import List
from .base import Tweak
from ..util.ps import ps

# ---- Network implementations ----

DNS_PRESETS = {
    "System default": None,
    "Cloudflare (1.1.1.1)": ["1.1.1.1", "1.0.0.1"],
    "Google (8.8.8.8)": ["8.8.8.8", "8.8.4.4"],
    "Quad9 (9.9.9.9)": ["9.9.9.9", "149.112.112.112"],
}


def apply_dns(preset: str) -> tuple[bool, str]:
    # Applies to all Ethernet/Wi-Fi adapters set to DHCP; advanced setups may need per-adapter selection.
    servers = DNS_PRESETS.get(preset)
    if servers is None:
        # Reset to DHCP
        ok1, m1 = ps("Get-DnsClient | Where-Object {$_.InterfaceAlias -match 'Ethernet|Wi-Fi'} | ForEach-Object { Set-DnsClientServerAddress -InterfaceIndex $_.InterfaceIndex -ResetServerAddresses }")
        return ok1, m1
    cmd = (
        "Get-DnsClient | Where-Object {$_.InterfaceAlias -match 'Ethernet|Wi-Fi'} | "
        f"ForEach-Object {{ Set-DnsClientServerAddress -InterfaceIndex $_.InterfaceIndex -ServerAddresses {servers[0]},{servers[1]} }}"
    )
    return ps(cmd)


def apply_doh(enable: bool) -> tuple[bool, str]:
    # Windows 11 DoH per-profile is usually configured by DNS policy; simplified approach via PowerShell netsh
    if enable:
        return ps("netsh dns add encryption server=1.1.1.1 dohtemplate=https://cloudflare-dns.com/dns-query autoupgrade=yes")
    else:
        return ps("netsh dns delete encryption server=1.1.1.1")


def apply_wu_bandwidth(limit_percent: int) -> tuple[bool, str]:
    # Delivery Optimization policy
    # DODownloadMode=3 (HTTP blended) often default; limit via MaxDownloadBandwidth
    return ps(f"Set-DeliveryOptimizationStatus -Verbose; New-Item -Path HKLM:Software\\Policies\\Microsoft\\Windows\\DeliveryOptimization -Force; New-ItemProperty -Path HKLM:Software\\Policies\\Microsoft\\Windows\\DeliveryOptimization -Name MaxDownloadBandwidth -Value {limit_percent} -PropertyType DWord -Force")


def get_tweaks() -> List[Tweak]:
    return [
        Tweak(
            id="dns_provider",
            category="Network",
            label="DNS provider",
            type="dropdown",
            options=list(DNS_PRESETS.keys()),
            default="System default",
            tooltip="Applies to Ethernet/Wi‑Fi adapters; advanced setups may need manual per‑adapter changes.",
            apply=lambda v: apply_dns(v)
        ),
        Tweak(
            id="doh",
            category="Network",
            label="Force DNS over HTTPS (DoH)",
            type="toggle",
            default=False,
            tooltip="Enables DoH for known DNS endpoints (simplified).",
            warning="Implementation is simplified; advanced users should configure per‑profile.",
            apply=lambda v: apply_doh(v)
        ),
        Tweak(
            id="wu_bw_limit",
            category="Network",
            label="Windows Update bandwidth limit (%)",
            type="number",
            minimum=0, maximum=100, step=5,
            default=0,
            tooltip="Limit Windows Update bandwidth as % of measured throughput.",
            apply=lambda v: apply_wu_bandwidth(v)
        ),
    ]