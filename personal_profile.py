"""
Personal profile for the Casper agent.

This is the ONE place to edit who the agent works for and the machine it runs
on. Everything else (system prompts, the greeting, the knowledge-graph seed)
reads from here, so changing a value below changes it everywhere.
"""
from __future__ import annotations

import getpass
import platform
import socket
from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class Owner:
    """Who the agent serves."""
    name: str = "Casper"
    # Only used for authorship/attribution, never sent anywhere.
    email: str = "klootwijkc@gmail.com"
    location: str = "Netherlands"
    timezone: str = "Europe/Amsterdam"
    # How the agent should address and speak to you.
    address_as: str = "Casper"
    tone: str = (
        "Direct and technical. No emojis, no filler. Assume deep knowledge of "
        "Python, TypeScript, networking and the Google ecosystem. Get to the "
        "point and always end with a concrete next step."
    )
    focus_areas: List[str] = field(default_factory=lambda: [
        "Defensive security research (Snort/YARA, quishing detection)",
        "Automation development (Google ADK, Apps Script, Cloud Run)",
        "Networking (MikroTik, RouterOS, Tailscale)",
        "Retro-gaming tooling and emulators (Pokemon, DS/Wii)",
    ])


@dataclass(frozen=True)
class Machine:
    """The primary machine this agent is meant to run on."""
    label: str = "Alienware laptop"
    os_family: str = "Windows"          # the Alienware runs Windows
    gpu: str = "NVIDIA RTX"             # typical Alienware discrete GPU
    notes: str = (
        "Primary daily driver. Windows paths, PowerShell, and local GPU are "
        "available. Prefer Windows-friendly commands and tooling by default."
    )


# ---- Edit above. Everything below derives from it. ----

OWNER = Owner()
MACHINE = Machine()


def detected_environment() -> dict:
    """Best-effort snapshot of the machine actually running this process."""
    return {
        "os": platform.system(),
        "release": platform.release(),
        "python": platform.python_version(),
        "hostname": socket.gethostname(),
        "login": _safe_login(),
        "is_windows": platform.system().lower().startswith("win"),
    }


def _safe_login() -> str:
    try:
        return getpass.getuser()
    except Exception:
        return "unknown"


def personal_context_block() -> str:
    """A compact personal-context header injected into every agent prompt."""
    env = detected_environment()
    running_on = (
        f"{MACHINE.label} ({MACHINE.os_family})"
        if env["is_windows"] or env["os"] == "Windows"
        else f"a {env['os']} host (your primary machine is the {MACHINE.label})"
    )
    return (
        "## Who you work for\n"
        f"- Owner: {OWNER.name}, based in {OWNER.location} ({OWNER.timezone}).\n"
        f"- Address them as: {OWNER.address_as}.\n"
        f"- Tone: {OWNER.tone}\n"
        f"- Primary focus: {'; '.join(OWNER.focus_areas)}.\n"
        f"- Running on: {running_on}. {MACHINE.notes}\n"
        "When suggesting shell commands, file paths or setup steps, assume "
        f"{MACHINE.os_family} and {MACHINE.label} unless told otherwise.\n"
    )
