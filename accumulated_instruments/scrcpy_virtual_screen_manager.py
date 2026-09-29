#!/usr/bin/env python3
"""
scrcpy virtual-screen launcher and interactive multi-screen manager.

MISSION
=======
Provide a deliberately boring, inspectable control layer around scrcpy for two
related workflows:

1. Direct mode
   Launch one scrcpy session with predictable defaults.

2. Interactive mode
   Manage multiple virtual-display scrcpy sessions from one terminal while
   centralizing device-global behavior in exactly one hidden scrcpy controller.

INTERACTIVE CONTROL MODEL
=========================
The interactive interface is a keyboard-driven terminal UI rather than a
numbered command prompt. The controller, every managed virtual display, and the
manager actions are selectable list entries. Up/down moves the selection;
Enter expands a process entry or invokes an action. Expanded process entries
show an inline submenu directly below the entry.

Every scrcpy subprocess spools its complete merged stdout/stderr stream to a
per-session temporary log file. The main list shows only one ellipsized latest
line so long output can never wrap and destroy the layout. The expanded
Console action opens a full scrollable history viewer over the complete log.

The UI is time-driven, not input-driven. It polls current terminal dimensions
and process/log state every UI tick, then repaints only when the rendered frame
changes. Terminal resizes and new subprocess output therefore appear live.

Installed-app discovery delegates to scrcpy --list-apps, which already exposes
Android application labels alongside exact package names. The interactive app
finder filters both fields case-insensitively with a focusable live search
field, highlights matched text, and is shared by Add Screen and the standalone
package-finder action.

Raw scrcpy logs remain unmodified on disk. Presentation-time pattern recognition
adds conservative semantic color for source tags, log levels, known subsystem
labels, success/error words, metrics, and package-like identifiers. Terminal
sanitization explicitly preserves Unicode Private Use codepoints so Nerd Font
glyphs survive sizing/ellipsizing operations.

DESIGN INVARIANTS
=================
- Managed screen processes never own Android-global stay-awake state.
- Managed screen processes never request physical-screen power changes.
- Managed screen processes use --no-power-on so creating a new virtual display
  cannot undo the manager's physical-screen-off policy.
- One hidden control-only scrcpy process owns:
    * --stay-awake
    * --turn-screen-off
    * --keep-active
  for the lifetime of the interactive manager once the first screen is added.
- The controller appears in the same interactive process list as virtual
  displays even though it has no video surface.
- The controller is asked to stop gracefully so scrcpy can restore the original
  stay_on_while_plugged_in value.
- Virtual-screen bitrate is deterministic from virtual framebuffer size unless
  the operator overrides it explicitly.
- Every child process receives an argv vector. Shell command construction and
  shell=True are intentionally forbidden.

The physical-screen-off action differs from stay-awake: scrcpy documents
stay-awake as restoring its previous global setting on exit, while
--turn-screen-off is an immediate device action and does not promise symmetric
restoration. Interactive mode therefore centralizes that action, but does not
attempt to guess or recreate the user's prior physical-screen state on exit.

No third-party Python packages are required. Nerd Font glyphs are intentionally
used throughout the interactive interface; a Nerd Font-capable terminal is
therefore strongly recommended. UI icon constants deliberately use only Nerd
Fonts Codicons (U+EA60-U+EC84), matching the operator-verified working Codicon
range instead of relying on relocated Font Awesome or supplementary-PUA glyphs.

Interactive surfaces are composed inside a four-sided frame that consumes the
current terminal rectangle. Main-menu and viewer row budgets are derived from
live terminal width and height so resizing changes both wrapping and viewport
capacity without waiting for user input.

On Windows, running virtual screens may optionally be collected into lightweight
organizer groups. The organizer is a dependency-free native Win32 window created
with ctypes; it does not reparent or embed scrcpy windows. Its client rectangle
is debounced and used to move/resize ordinary scrcpy top-level windows with
bounded portrait aspect-ratio wiggle. Closing an organizer disbands its group
without stopping any screen.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from dataclasses import dataclass, field
import math
import os
from pathlib import Path
import queue
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import textwrap
import threading
import time
import unicodedata
from typing import Callable, Iterable, Iterator, Sequence


# =============================================================================
# FLIGHT CONSTANTS / OPERATOR POLICY
# =============================================================================

DEFAULT_WIDTH = 288
DEFAULT_HEIGHT = 640
DEFAULT_MAX_FPS = 60
DEFAULT_BITRATE_SPEC = "auto"

AUTO_BITRATE_REFERENCE_WIDTH = 288
AUTO_BITRATE_REFERENCE_HEIGHT = 640
AUTO_BITRATE_REFERENCE_BPS = 2_000_000
AUTO_BITRATE_MIN_BPS = 2_000_000
AUTO_BITRATE_MAX_BPS = 8_000_000
AUTO_BITRATE_ROUNDING_BPS = 100_000

PROCESS_STOP_GRACE_SECONDS = 4.0
PROCESS_TERMINATE_GRACE_SECONDS = 2.0
PROCESS_STARTUP_PROBE_SECONDS = 0.25
UI_REFRESH_SECONDS = 0.169

GROUP_RESIZE_DEBOUNCE_SECONDS = 0.169
GROUP_ASPECT_WIGGLE_FRACTION = 0.12
GROUP_WINDOW_GAP_PX = 8
GROUP_WINDOW_MIN_WIDTH = 420
GROUP_WINDOW_MIN_HEIGHT = 300
GROUP_WINDOW_INITIAL_WIDTH = 1000
GROUP_WINDOW_INITIAL_HEIGHT = 700

SIZE_PATTERN = re.compile(r"^(?P<width>[1-9][0-9]*)[xX](?P<height>[1-9][0-9]*)$")
BITRATE_PATTERN = re.compile(r"^(?P<number>[1-9][0-9]*)(?P<suffix>[kKmM]?)$")
ANDROID_PACKAGE_PATTERN = re.compile(
    r"(?P<package>[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+)$"
)
SCRCPY_LOG_PREFIX_PATTERN = re.compile(
    r"^(?:\[[^\]]+\]\s*)?(?:VERBOSE|DEBUG|INFO|WARN|ERROR):\s*"
)
SCRCPY_LOG_LINE_PATTERN = re.compile(
    r"^(?P<source>\[[^\]]+\]\s*)?"
    r"(?P<level>VERBOSE|DEBUG|INFO|WARN|ERROR):(?P<body>.*)$"
)
SCRCPY_SEMANTIC_TOKEN_PATTERN = re.compile(
    r"(?P<field>\b(?:ADB device found|Device|Renderer|Texture|Encoder|Decoder|"
    r"Audio|Video|Display|OpenGL|DPI)\b(?=:))"
    r"|(?P<success>\b(?:found|pushed|turned off|connected|created|started|"
    r"successful(?:ly)?|success)\b)"
    r"|(?P<error>\b(?:failed|failure|error|exception|unable|cannot)\b)"
    r"|(?P<warning>\b(?:warning|warn)\b)"
    r"|(?P<metric>\b\d+(?:\.\d+)?(?:x\d+|\s?(?:MB/s|Mbps|Kbps|fps|Hz|ms|bytes))\b)"
    r"|(?P<package>\b[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*){2,}\b)"
    r"|(?P<arrow>-->)",
    re.IGNORECASE,
)
ANSI_ESCAPE_PATTERN = re.compile(r"\x1b(?:\[[0-?]*[ -/]*[@-~]|[@-_])")

EXIT_OK = 0
EXIT_DEPENDENCY = 3
EXIT_RUNTIME = 4

# Nerd Font / terminal presentation glyphs. These are decoration only: control
# logic never depends on glyph width or successful font rendering.
# Nerd Fonts Codicons only. This project intentionally stays within the
# current Codicon range U+EA60-U+EC84 because it is verified against the same
# glyph set as the operator's known-good U+EB53 cod-shield character.
ICON_POINTER = ""       # U+EAB6 cod-chevron_right
ICON_CONTROLLER = ""    # U+EBA2 cod-server_process
ICON_SCREEN = ""        # U+EB4C cod-screen_full
ICON_RUNNING = ""       # U+EBA6 cod-play_circle
ICON_STOPPED = ""       # U+EBA5 cod-stop_circle
ICON_STANDBY = ""       # U+EC75 cod-clockface
ICON_LOG = ""           # U+EC5E cod-file_text
ICON_ADD = ""           # U+EA60 cod-add
ICON_SETTINGS = ""      # U+EB51 cod-settings_gear
ICON_HELP = ""          # U+EB32 cod-question
ICON_QUIT = ""          # U+EA6E cod-sign_out
ICON_STOP = ""          # U+EAD7 cod-debug_stop
ICON_REMOVE = ""        # U+EA81 cod-trash
ICON_RESTART = ""       # U+EB37 cod-refresh
ICON_EXPAND = ""        # U+EAB6 cod-chevron_right
ICON_COLLAPSE = ""      # U+EAB4 cod-chevron_down
ICON_BACK = ""          # U+EA9B cod-arrow_left
ICON_SCROLL = ""        # U+EB84 cod-list_flat
ICON_INFO = ""          # U+EA74 cod-info
ICON_TERMINAL = ""      # U+EA85 cod-terminal
ICON_HEARTBEAT = ""     # U+EB31 cod-pulse
ICON_APPS = ""          # U+EB86 cod-list_tree
ICON_GROUP = ""         # U+EB23 cod-multiple_windows
ICON_USER_APP = ""      # U+EADB cod-device_mobile
ICON_SYSTEM_APP = ""    # U+EB50 cod-server
ICON_SEARCH = ""        # U+EA6D cod-search
ICON_REFRESH = ""       # U+EB37 cod-refresh

ANSI_RESET = "\x1b[0m"
ANSI_REVERSE = "\x1b[7m"
ANSI_DIM = "\x1b[2m"
ANSI_BOLD = "\x1b[1m"
ANSI_FG_RED = "\x1b[91m"
ANSI_FG_GREEN = "\x1b[92m"
ANSI_FG_YELLOW = "\x1b[93m"
ANSI_FG_BLUE = "\x1b[94m"
ANSI_FG_MAGENTA = "\x1b[95m"
ANSI_FG_CYAN = "\x1b[96m"
ANSI_FG_GRAY = "\x1b[90m"
ANSI_FG_WHITE = "\x1b[97m"
ANSI_MATCH = "\x1b[27;30;103;1m"


# =============================================================================
# DOMAIN MODEL
# =============================================================================


class ConfigurationError(ValueError):
    """Operator-supplied configuration is invalid."""


class LaunchError(RuntimeError):
    """A required external process could not be started or immediately failed."""


@dataclass(frozen=True, slots=True)
class DisplaySize:
    """Exact Android virtual-display framebuffer dimensions."""

    width: int
    height: int

    @classmethod
    def parse(cls, text: str) -> "DisplaySize":
        """Parse WIDTHxHEIGHT with positive integer dimensions."""
        match = SIZE_PATTERN.fullmatch(text.strip())
        if match is None:
            raise ConfigurationError(
                f"Invalid display size {text!r}; expected WIDTHxHEIGHT, for example 288x640."
            )

        width = int(match.group("width"))
        height = int(match.group("height"))
        return cls(width=width, height=height)

    @property
    def pixels(self) -> int:
        """Return framebuffer pixel count."""
        return self.width * self.height

    def __str__(self) -> str:
        return f"{self.width}x{self.height}"


@dataclass(frozen=True, slots=True)
class ScreenDefaults:
    """Defaults inherited by newly created virtual screens."""

    size: DisplaySize
    max_fps: int
    bitrate_spec: str


@dataclass(frozen=True, slots=True)
class ScreenRequest:
    """Complete immutable request for one virtual-display session."""

    size: DisplaySize
    max_fps: int
    bitrate_spec: str
    app: str | None = None


@dataclass(frozen=True, slots=True)
class ResolvedBitrate:
    """Normalized bitrate policy ready for scrcpy invocation and diagnostics."""

    scrcpy_value: str | None
    display_value: str
    source: str


@dataclass(slots=True)
class ManagedScreen:
    """Runtime record for one screen owned by the interactive manager."""

    screen_id: int
    request: ScreenRequest
    bitrate: ResolvedBitrate
    process: "ObservedProcess"
    started_monotonic: float = field(default_factory=time.monotonic)
    group_id: int | None = None
    window_handle: int | None = None

    @property
    def status(self) -> str:
        code = self.process.poll()
        if code is None:
            return "RUNNING"
        return f"EXIT {code}"

    @property
    def age_seconds(self) -> int:
        return max(0, int(time.monotonic() - self.started_monotonic))


@dataclass(frozen=True, slots=True)
class InstalledApp:
    """One Android app returned by scrcpy's label-aware app inventory."""

    name: str
    package: str
    is_system: bool


@dataclass(frozen=True, slots=True)
class MenuItem:
    """One selectable top-level interactive list entry."""

    key: str
    kind: str
    screen_id: int | None = None


@dataclass(frozen=True, slots=True)
class SubmenuAction:
    """One selectable action displayed beneath an expanded process entry."""

    action_id: str
    label: str
    icon: str


@dataclass(frozen=True, slots=True)
class GroupWindowEvent:
    """One geometry/lifecycle notification emitted by an organizer window."""

    group_id: int
    kind: str
    rect: tuple[int, int, int, int] | None = None
    detail: str | None = None


@dataclass(slots=True)
class ManagedGroup:
    """Runtime membership and geometry state for one organizer window."""

    group_id: int
    screen_ids: set[int]
    organizer: "OrganizerWindow"
    last_rect: tuple[int, int, int, int] | None = None
    pending_rect: tuple[int, int, int, int] | None = None


# =============================================================================
# VALIDATION AND AUTOMATIC BITRATE CONTROL LAW
# =============================================================================


def validate_max_fps(value: int) -> int:
    """Reject nonsensical frame-rate values before invoking scrcpy."""
    if value <= 0:
        raise ConfigurationError("--max-fps must be greater than zero.")
    if value > 1000:
        raise ConfigurationError("--max-fps greater than 1000 is almost certainly a typo.")
    return value


def normalize_bitrate_spec(value: str) -> str:
    """
    Validate an explicit bitrate or the special value 'auto'.

    scrcpy's conventional integer formats (for example 2500K or 8M) are kept
    intact. Floating-point suffix values are intentionally not invented.
    """
    stripped = value.strip()
    if stripped.lower() == "auto":
        return "auto"

    match = BITRATE_PATTERN.fullmatch(stripped)
    if match is None:
        raise ConfigurationError(
            f"Invalid bitrate {value!r}; expected 'auto' or an integer such as 2000000, 2500K, or 8M."
        )

    suffix = match.group("suffix").upper()
    return f"{match.group('number')}{suffix}"


def parse_bitrate_bps(value: str) -> int:
    """Convert a validated explicit bitrate string into bits per second."""
    normalized = normalize_bitrate_spec(value)
    if normalized == "auto":
        raise ConfigurationError("'auto' has no fixed bit-per-second value.")

    match = BITRATE_PATTERN.fullmatch(normalized)
    assert match is not None

    amount = int(match.group("number"))
    multiplier = {
        "": 1,
        "K": 1_000,
        "M": 1_000_000,
    }[match.group("suffix").upper()]
    return amount * multiplier


def format_bps(bps: int) -> str:
    """Human-readable decimal bitrate."""
    if bps >= 1_000_000:
        return f"{bps / 1_000_000:.1f} Mbps"
    if bps >= 1_000:
        return f"{bps / 1_000:.0f} Kbps"
    return f"{bps} bps"


def _round_half_up(value: float, quantum: int) -> int:
    """Round positive values to the nearest quantum without banker's rounding."""
    return int(math.floor(value / quantum + 0.5) * quantum)


def calculate_auto_bitrate_bps(size: DisplaySize) -> int:
    """
    Scale bitrate sub-linearly with framebuffer pixel count.

    raw = 2 Mbps * sqrt(pixels / pixels_at_288x640)
    final = clamp(round(raw, 100 Kbps), 2 Mbps, 8 Mbps)

    The square-root scaling is deliberate: linear scaling would hit the 8 Mbps
    ceiling too quickly for the tiny virtual displays this tool targets.
    """
    reference_pixels = AUTO_BITRATE_REFERENCE_WIDTH * AUTO_BITRATE_REFERENCE_HEIGHT
    scale = math.sqrt(size.pixels / reference_pixels)
    raw_bps = AUTO_BITRATE_REFERENCE_BPS * scale
    rounded_bps = _round_half_up(raw_bps, AUTO_BITRATE_ROUNDING_BPS)
    return max(AUTO_BITRATE_MIN_BPS, min(AUTO_BITRATE_MAX_BPS, rounded_bps))


def resolve_bitrate(spec: str, size: DisplaySize | None) -> ResolvedBitrate:
    """Resolve operator policy into the exact scrcpy argv value."""
    normalized = normalize_bitrate_spec(spec)

    if normalized != "auto":
        bps = parse_bitrate_bps(normalized)
        return ResolvedBitrate(
            scrcpy_value=normalized,
            display_value=format_bps(bps),
            source="operator override",
        )

    if size is None:
        return ResolvedBitrate(
            scrcpy_value=None,
            display_value="scrcpy default (8 Mbps)",
            source="auto without virtual-display geometry",
        )

    bps = calculate_auto_bitrate_bps(size)
    return ResolvedBitrate(
        scrcpy_value=f"{bps // 1_000}K",
        display_value=format_bps(bps),
        source=f"auto from {size} framebuffer",
    )


def validate_app(app: str | None) -> str | None:
    """Normalize an optional exact Android package name."""
    if app is None:
        return None

    stripped = app.strip()
    if not stripped:
        return None
    if any(character.isspace() for character in stripped):
        raise ConfigurationError(f"App/package must not contain whitespace: {app!r}")
    return stripped


def parse_scrcpy_app_list(output: str) -> tuple[InstalledApp, ...]:
    """
    Parse the human-label + package inventory emitted by scrcpy --list-apps.

    scrcpy formats ordinary names on one line and wraps names longer than its
    fixed name column onto a following package-only line. Parsing from the
    package token at the end keeps this tolerant of both layouts and of normal
    scrcpy/server log prefixes.
    """
    apps: dict[str, InstalledApp] = {}
    pending_name: str | None = None
    pending_system = False

    for raw_line in output.splitlines():
        line = sanitize_log_line(raw_line).strip()
        line = SCRCPY_LOG_PREFIX_PATTERN.sub("", line).strip()
        if not line or line == "List of apps:" or "Processing Android apps" in line:
            continue

        is_bullet = line.startswith(("* ", "- "))
        if is_bullet:
            pending_system = line.startswith("* ")
            line = line[2:].strip()

        package_match = ANDROID_PACKAGE_PATTERN.search(line)
        if package_match is None:
            if is_bullet and line:
                pending_name = line
            continue

        package = package_match.group("package")
        name_part = line[: package_match.start()].rstrip()
        name = name_part or pending_name
        if not name:
            name = package

        is_system = pending_system if not name_part else pending_system if is_bullet else False
        apps[package] = InstalledApp(name=name, package=package, is_system=is_system)
        pending_name = None
        pending_system = False

    return tuple(
        sorted(
            apps.values(),
            key=lambda app: (app.name.casefold(), app.package.casefold()),
        )
    )


def list_installed_apps(scrcpy: str) -> tuple[InstalledApp, ...]:
    """Ask scrcpy/Android for installed app labels and package names."""
    command = [scrcpy, "--list-apps", "--no-terminal-title"]
    try:
        completed = subprocess.run(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=45,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise LaunchError(f"Unable to query installed Android apps: {exc}") from exc

    apps = parse_scrcpy_app_list(completed.stdout or "")
    if completed.returncode != 0 or not apps:
        tail = "\n".join((completed.stdout or "").splitlines()[-20:])
        raise LaunchError(
            "scrcpy --list-apps did not return a usable app inventory."
            + (f"\n\n{tail}" if tail else "")
        )
    return apps


# =============================================================================
# SCRCPY COMMAND CONSTRUCTION
# =============================================================================


def resolve_scrcpy_executable() -> str:
    """
    Locate scrcpy.

    The SCRCPY environment variable may contain an explicit executable path.
    Otherwise normal PATH lookup is used.
    """
    configured = os.environ.get("SCRCPY")
    if configured:
        return configured

    executable = shutil.which("scrcpy")
    if executable is None:
        raise LaunchError(
            "Could not find 'scrcpy' on PATH. Install scrcpy or set the SCRCPY "
            "environment variable to its executable path."
        )
    return executable


def command_for_display(
    scrcpy: str,
    request: ScreenRequest,
    *,
    managed_screen_id: int | None = None,
    interactive_managed: bool = False,
) -> tuple[list[str], ResolvedBitrate]:
    """
    Construct one virtual-display command.

    interactive_managed=True intentionally omits all manager-owned device-global
    flags and adds --no-power-on.
    """
    bitrate = resolve_bitrate(request.bitrate_spec, request.size)

    command = [
        scrcpy,
        f"--new-display={request.size}",
        f"--max-fps={request.max_fps}",
        "--no-window-aspect-ratio-lock",
        "--render-fit=stretched",
        "--display-ime-policy=local",
    ]

    if request.app is not None:
        command.append(f"--start-app={request.app}")

    if bitrate.scrcpy_value is not None:
        command.append(f"--video-bit-rate={bitrate.scrcpy_value}")

    if interactive_managed:
        # The hidden manager controller owns physical/device-global behavior.
        # Child sessions must not wake the physical screen as they start.
        command.extend(
            [
                "--no-power-on",
                "--no-terminal-title",
                "--verbosity=info",
            ]
        )
        if managed_screen_id is not None:
            label = request.app or "virtual display"
            command.append(f"--window-title=scrcpy [{managed_screen_id:02d}] {label}")
    else:
        command.extend(
            [
                "--keep-active",
                "--stay-awake",
                "--turn-screen-off",
            ]
        )

    return command, bitrate


def command_for_physical_display(
    scrcpy: str,
    *,
    max_fps: int,
    bitrate_spec: str,
) -> tuple[list[str], ResolvedBitrate]:
    """Construct the direct-mode fallback that mirrors the normal device display."""
    bitrate = resolve_bitrate(bitrate_spec, None)

    command = [
        scrcpy,
        f"--max-fps={max_fps}",
        "--no-window-aspect-ratio-lock",
        "--render-fit=stretched",
        "--keep-active",
        "--stay-awake",
        "--turn-screen-off",
    ]

    if bitrate.scrcpy_value is not None:
        command.append(f"--video-bit-rate={bitrate.scrcpy_value}")

    return command, bitrate


def command_for_device_state_controller(scrcpy: str) -> list[str]:
    """
    Build the hidden control-only process for interactive mode.

    This process owns the Android-global/session-global policy exactly once:
    - --stay-awake: scrcpy snapshots/restores stay_on_while_plugged_in.
    - --turn-screen-off: one immediate physical-screen-off request.
    - --keep-active: one periodic user-activity source.

    --no-power-on prevents controller startup from briefly waking the screen.
    --no-window explicitly suppresses the host-side scrcpy window while keeping
    the control channel needed for the manager-owned device-state operations.
    """
    return [
        scrcpy,
        "--no-video",
        "--no-audio",
        "--no-window",
        "--no-power-on",
        "--keep-active",
        "--stay-awake",
        "--turn-screen-off",
        "--no-clipboard-autosync",
        "--no-terminal-title",
        "--verbosity=info",
    ]


def printable_command(command: Sequence[str]) -> str:
    """Render argv for diagnostics only; this string is never executed."""
    if os.name == "nt":
        return subprocess.list2cmdline(list(command))
    return shlex.join(command)


# =============================================================================
# LOG SANITIZATION / DISPLAY GEOMETRY
# =============================================================================


def sanitize_log_line(line: str) -> str:
    """
    Convert arbitrary subprocess output into one harmless terminal UI line.

    Python deliberately reports Unicode Private Use characters (category Co)
    as non-printable. Nerd Fonts live in those private-use ranges, so treating
    str.isprintable() as the whole policy would destroy valid UI glyphs by
    replacing them with U+FFFD. Preserve private-use codepoints explicitly while
    still rejecting actual control/unassigned formatting garbage.
    """
    value = ANSI_ESCAPE_PATTERN.sub("", line)
    value = value.replace("\r", " ").replace("\n", " ").replace("\t", "    ")
    return "".join(
        character
        if character.isprintable() or unicodedata.category(character) == "Co"
        else "�"
        for character in value
    )


def ellipsize(text: str, width: int) -> str:
    """Fit text to exactly one terminal line without wrapping."""
    if width <= 0:
        return ""
    clean = sanitize_log_line(text)
    if len(clean) <= width:
        return clean
    if width == 1:
        return "…"
    return clean[: width - 1] + "…"



def styled(text: str, style: str, *, base_style: str = "") -> str:
    """Apply one ANSI style and reliably restore the caller's surrounding style."""
    return f"{style}{text}{ANSI_RESET}{base_style}"


def highlight_matches(text: str, query: str, *, base_style: str = "") -> str:
    """Highlight every case-insensitive literal query match without changing text."""
    if not query:
        return text

    pattern = re.compile(re.escape(query), re.IGNORECASE)
    output: list[str] = []
    cursor = 0
    for match in pattern.finditer(text):
        output.append(text[cursor : match.start()])
        output.append(
            f"{ANSI_MATCH}{match.group(0)}{ANSI_RESET}{base_style}"
        )
        cursor = match.end()
    output.append(text[cursor:])
    return "".join(output)


def colorize_scrcpy_body(text: str, *, base_style: str = "") -> str:
    """Color only conservative, semantically recognizable scrcpy tokens."""
    output: list[str] = []
    cursor = 0

    for match in SCRCPY_SEMANTIC_TOKEN_PATTERN.finditer(text):
        output.append(text[cursor : match.start()])
        token = match.group(0)

        if match.lastgroup == "field":
            style = ANSI_FG_BLUE + ANSI_BOLD
        elif match.lastgroup == "success":
            style = ANSI_FG_GREEN
        elif match.lastgroup == "error":
            style = ANSI_FG_RED + ANSI_BOLD
        elif match.lastgroup == "warning":
            style = ANSI_FG_YELLOW + ANSI_BOLD
        elif match.lastgroup == "metric":
            style = ANSI_FG_YELLOW
        elif match.lastgroup == "package":
            style = ANSI_FG_MAGENTA
        else:
            style = ANSI_FG_CYAN

        output.append(styled(token, style, base_style=base_style))
        cursor = match.end()

    output.append(text[cursor:])
    return "".join(output)


def colorize_scrcpy_log_line(line: str, *, base_style: str = "") -> str:
    """
    Add presentation-only semantic color to one raw scrcpy console line.

    Unknown text is deliberately left untouched. Raw log files never contain
    these ANSI sequences; coloring happens only while rendering the TUI.
    """
    clean = sanitize_log_line(line)
    match = SCRCPY_LOG_LINE_PATTERN.match(clean)
    if match is None:
        return colorize_scrcpy_body(clean, base_style=base_style)

    source = match.group("source") or ""
    level = match.group("level")
    body = match.group("body")

    level_style = {
        "VERBOSE": ANSI_DIM + ANSI_FG_GRAY,
        "DEBUG": ANSI_FG_BLUE,
        "INFO": ANSI_FG_CYAN,
        "WARN": ANSI_FG_YELLOW + ANSI_BOLD,
        "ERROR": ANSI_FG_RED + ANSI_BOLD,
    }[level]

    output = ""
    if source:
        output += styled(source.rstrip(), ANSI_FG_MAGENTA, base_style=base_style) + " "

    output += styled(f"{level}:", level_style, base_style=base_style)

    if level == "ERROR":
        output += styled(body, ANSI_FG_RED, base_style=base_style)
    elif level == "WARN":
        output += styled(body, ANSI_FG_YELLOW, base_style=base_style)
    else:
        output += colorize_scrcpy_body(body, base_style=base_style)

    return output


def terminal_dimensions() -> tuple[int, int]:
    """Return the terminal's current live dimensions."""
    size = shutil.get_terminal_size(fallback=(100, 30))
    return max(1, size.columns), max(1, size.lines)


def terminal_rule(width: int, glyph: str = "─") -> str:
    """Build a horizontal rule for an already-computed content width."""
    return glyph * max(1, width)


def visible_width(text: str) -> int:
    """Return printable width approximation with ANSI control sequences removed."""
    return len(ANSI_ESCAPE_PATTERN.sub("", text))


def fit_ansi_line(text: str, width: int) -> str:
    """
    Fit a styled line into exactly the requested terminal width.

    Normal lines retain ANSI styling. If truncation is required, styling is
    stripped before ellipsizing so an escape sequence can never be cut in half.
    """
    if width <= 0:
        return ""

    current = visible_width(text)
    if current > width:
        return ellipsize(ANSI_ESCAPE_PATTERN.sub("", text), width)

    return text + (" " * (width - current))


def compose_terminal_frame(
    content_lines: Sequence[str],
    width: int,
    height: int,
    *,
    frame_style: str = ANSI_FG_CYAN,
) -> str:
    """
    Compose one complete frame occupying the current terminal rectangle.

    The caller supplies logical interior rows. This function truncates/pads them
    to the available interior and supplies all four borders. The output therefore
    always tracks both terminal width and terminal height, not merely a top rule.
    """
    width = max(1, width)
    height = max(1, height)

    if width < 2 or height < 2:
        raw = list(content_lines)[:height]
        raw.extend([""] * max(0, height - len(raw)))
        return "\n".join(ellipsize(line, width) for line in raw)

    inner_width = width - 2
    inner_height = height - 2

    visible_content = list(content_lines)[:inner_height]
    visible_content.extend([""] * max(0, inner_height - len(visible_content)))

    top = f"{frame_style}╔{'═' * inner_width}╗{ANSI_RESET}"
    bottom = f"{frame_style}╚{'═' * inner_width}╝{ANSI_RESET}"

    rows = [top]
    for line in visible_content:
        fitted = fit_ansi_line(line, inner_width)
        rows.append(
            f"{frame_style}║{ANSI_RESET}{fitted}"
            f"{frame_style}║{ANSI_RESET}"
        )
    rows.append(bottom)
    return "\n".join(rows)


def selected_viewport(
    blocks: Sequence[Sequence[str]],
    selected_index: int,
    row_budget: int,
) -> list[str]:
    """
    Slice variable-height menu blocks while keeping the selected block visible.

    The viewport is centered loosely around the selection when there is enough
    space, while small terminals still prioritize the selected entry itself.
    """
    if row_budget <= 0 or not blocks:
        return []

    flat: list[str] = []
    starts: list[int] = []
    ends: list[int] = []
    for block in blocks:
        starts.append(len(flat))
        flat.extend(block)
        ends.append(len(flat))

    if len(flat) <= row_budget:
        return flat

    selected_index = max(0, min(selected_index, len(blocks) - 1))
    selected_start = starts[selected_index]
    selected_end = ends[selected_index]

    target_top = selected_start - row_budget // 3
    top = max(0, min(target_top, len(flat) - row_budget))
    if selected_end > top + row_budget:
        top = max(0, selected_end - row_budget)
    if selected_start < top:
        top = selected_start

    return flat[top : top + row_budget]


# =============================================================================
# CHILD-PROCESS SUPERVISION AND COMPLETE LOG SPOOLING
# =============================================================================


class ObservedProcess:
    """
    One scrcpy process with complete file-backed console history.

    stdout and stderr are merged and drained continuously by a daemon reader
    thread. The complete stream is written to log_path. Only the latest line and
    line count stay in memory, making the always-visible UI cheap regardless of
    session duration.
    """

    def __init__(self, command: Sequence[str], *, label: str, log_path: Path) -> None:
        self.command = list(command)
        self.label = label
        self.log_path = log_path
        self._lock = threading.Lock()
        self._process: subprocess.Popen[str] | None = None
        self._reader: threading.Thread | None = None
        self._latest_line = ""
        self._line_count = 0
        self._load_existing_log_state()

    def _load_existing_log_state(self) -> None:
        if not self.log_path.is_file():
            return
        try:
            lines = self.log_path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            return
        self._line_count = len(lines)
        if lines:
            self._latest_line = lines[-1]

    @property
    def pid(self) -> int | None:
        process = self._process
        return None if process is None else process.pid

    @property
    def latest_line(self) -> str:
        with self._lock:
            return self._latest_line

    @property
    def line_count(self) -> int:
        with self._lock:
            return self._line_count

    def start(self) -> None:
        if self._process is not None:
            raise LaunchError(f"{self.label} was already started.")

        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        creationflags = 0
        if os.name == "nt":
            creationflags |= subprocess.CREATE_NEW_PROCESS_GROUP

        try:
            self._process = subprocess.Popen(
                self.command,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                creationflags=creationflags,
            )
        except OSError as exc:
            raise LaunchError(
                f"Failed to launch {self.label}: {exc}\nCommand: {printable_command(self.command)}"
            ) from exc

        assert self._process.stdout is not None
        self._reader = threading.Thread(
            target=self._drain_output,
            args=(self._process.stdout,),
            name=f"{self.label}-log-reader",
            daemon=True,
        )
        self._reader.start()

    def _drain_output(self, stream: Iterable[str]) -> None:
        try:
            with self.log_path.open("a", encoding="utf-8", buffering=1) as log_file:
                for line in stream:
                    normalized = line.rstrip("\r\n")
                    log_file.write(normalized + "\n")
                    with self._lock:
                        self._latest_line = normalized
                        self._line_count += 1
        except OSError as exc:
            with self._lock:
                self._latest_line = f"[log spool failure: {exc}]"

    def poll(self) -> int | None:
        if self._process is None:
            return None
        return self._process.poll()

    def startup_probe(self) -> None:
        """Catch immediately rejected command lines before reporting success."""
        time.sleep(PROCESS_STARTUP_PROBE_SECONDS)
        code = self.poll()
        if code is None:
            return

        detail = "\n".join(self.tail(20))
        raise LaunchError(
            f"{self.label} exited during startup with code {code}."
            + (f"\n{detail}" if detail else "")
        )

    def read_all_lines(self) -> list[str]:
        """Snapshot complete console history from disk."""
        if not self.log_path.is_file():
            return []
        try:
            return self.log_path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError as exc:
            return [f"[unable to read log: {exc}]"]

    def tail(self, line_count: int = 40) -> list[str]:
        """Return the latest logical lines from complete file-backed history."""
        if line_count <= 0:
            return []
        return self.read_all_lines()[-line_count:]

    def request_stop(self) -> bool:
        """Ask scrcpy to exit cleanly; force termination only as a fallback."""
        process = self._process
        if process is None or process.poll() is not None:
            return True

        graceful = True
        try:
            if os.name == "nt":
                process.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                process.send_signal(signal.SIGINT)
            process.wait(timeout=PROCESS_STOP_GRACE_SECONDS)
            return True
        except (OSError, subprocess.TimeoutExpired):
            graceful = False

        try:
            process.terminate()
            process.wait(timeout=PROCESS_TERMINATE_GRACE_SECONDS)
        except (OSError, subprocess.TimeoutExpired):
            try:
                process.kill()
                process.wait(timeout=PROCESS_TERMINATE_GRACE_SECONDS)
            except (OSError, subprocess.TimeoutExpired):
                pass

        return graceful


# =============================================================================
# OPTIONAL WINDOWS GROUP ORGANIZER
# =============================================================================


def win32_visible_window_for_pid(pid: int) -> int | None:
    """Return one visible top-level HWND owned by pid, or None."""
    if os.name != "nt":
        return None

    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    matches: list[int] = []

    callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    user32.IsWindowVisible.argtypes = [wintypes.HWND]
    user32.IsWindowVisible.restype = wintypes.BOOL
    user32.GetWindowThreadProcessId.argtypes = [
        wintypes.HWND,
        ctypes.POINTER(wintypes.DWORD),
    ]
    user32.GetWindowThreadProcessId.restype = wintypes.DWORD
    user32.EnumWindows.argtypes = [callback_type, wintypes.LPARAM]
    user32.EnumWindows.restype = wintypes.BOOL

    @callback_type
    def callback(hwnd: int, _lparam: int) -> bool:
        if not user32.IsWindowVisible(hwnd):
            return True

        process_id = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
        if process_id.value == pid:
            matches.append(int(hwnd))
            return False
        return True

    user32.EnumWindows(callback, 0)
    return matches[0] if matches else None


def win32_is_window(hwnd: int | None) -> bool:
    """Return whether hwnd still names a live Win32 window."""
    if os.name != "nt" or hwnd is None:
        return False

    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    user32.IsWindow.argtypes = [wintypes.HWND]
    user32.IsWindow.restype = wintypes.BOOL
    return bool(user32.IsWindow(hwnd))


def win32_client_rect_on_screen(hwnd: int) -> tuple[int, int, int, int] | None:
    """Return a Win32 client rectangle as screen x, y, width, height."""
    if os.name != "nt":
        return None

    import ctypes
    from ctypes import wintypes

    class Point(ctypes.Structure):
        _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]

    user32 = ctypes.windll.user32
    user32.GetClientRect.argtypes = [
        wintypes.HWND,
        ctypes.POINTER(wintypes.RECT),
    ]
    user32.GetClientRect.restype = wintypes.BOOL
    user32.ClientToScreen.argtypes = [
        wintypes.HWND,
        ctypes.POINTER(Point),
    ]
    user32.ClientToScreen.restype = wintypes.BOOL

    rect = wintypes.RECT()
    if not user32.GetClientRect(hwnd, ctypes.byref(rect)):
        return None

    origin = Point(0, 0)
    if not user32.ClientToScreen(hwnd, ctypes.byref(origin)):
        return None

    return (
        int(origin.x),
        int(origin.y),
        max(1, int(rect.right - rect.left)),
        max(1, int(rect.bottom - rect.top)),
    )


def win32_set_window_rect(hwnd: int, rect: tuple[int, int, int, int]) -> bool:
    """Move/resize a top-level window without activating it."""
    if os.name != "nt":
        return False

    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    user32.SetWindowPos.argtypes = [
        wintypes.HWND,
        wintypes.HWND,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        wintypes.UINT,
    ]
    user32.SetWindowPos.restype = wintypes.BOOL

    x, y, width, height = rect
    # HWND_TOP plus SWP_NOACTIVATE keeps grouped scrcpy windows above the
    # organizer without stealing keyboard focus from the terminal.
    HWND_TOP = 0
    SWP_NOACTIVATE = 0x0010
    SWP_SHOWWINDOW = 0x0040
    return bool(
        user32.SetWindowPos(
            hwnd,
            HWND_TOP,
            int(x),
            int(y),
            max(1, int(width)),
            max(1, int(height)),
            SWP_NOACTIVATE | SWP_SHOWWINDOW,
        )
    )


def _fit_ratio_inside_cell(
    cell_x: int,
    cell_y: int,
    cell_width: int,
    cell_height: int,
    preferred_ratio: float,
    wiggle_fraction: float,
) -> tuple[int, int, int, int]:
    """
    Fit one portrait window into a cell with bounded aspect-ratio distortion.

    The organizer is allowed to stretch/squish each screen independently by the
    configured fraction. Outside that band, empty space is preferred over more
    geometric distortion.
    """
    minimum_ratio = preferred_ratio * (1.0 - wiggle_fraction)
    maximum_ratio = preferred_ratio * (1.0 + wiggle_fraction)
    cell_ratio = cell_width / max(1, cell_height)
    target_ratio = max(minimum_ratio, min(maximum_ratio, cell_ratio))

    if cell_ratio > target_ratio:
        height = cell_height
        width = max(1, round(height * target_ratio))
    else:
        width = cell_width
        height = max(1, round(width / target_ratio))

    x = cell_x + (cell_width - width) // 2
    y = cell_y + (cell_height - height) // 2
    return x, y, width, height


def calculate_group_layout(
    bounds: tuple[int, int, int, int],
    screens: Sequence[ManagedScreen],
) -> dict[int, tuple[int, int, int, int]]:
    """
    Choose a compact portrait-only row layout for the current organizer shape.

    Candidate row counts are intentionally finite and boring. Row heights are
    weighted toward the height that would preserve each row's preferred screen
    ratios, then every individual screen may wiggle within a small bounded band.
    The candidate covering the most total window area wins.
    """
    x0, y0, total_width, total_height = bounds
    count = len(screens)
    if count == 0:
        return {}

    best_score = -1
    best_layout: dict[int, tuple[int, int, int, int]] = {}

    for row_count in range(1, count + 1):
        base = count // row_count
        remainder = count % row_count
        if base == 0:
            continue

        row_sizes = [
            base + (1 if row_index < remainder else 0)
            for row_index in range(row_count)
        ]
        usable_height = total_height - GROUP_WINDOW_GAP_PX * (row_count - 1)
        if usable_height <= 0:
            continue

        row_specs: list[tuple[list[ManagedScreen], int, float]] = []
        cursor = 0
        ideal_height_sum = 0.0
        for row_size in row_sizes:
            row_screens = list(screens[cursor : cursor + row_size])
            cursor += row_size

            usable_width = total_width - GROUP_WINDOW_GAP_PX * (row_size - 1)
            if usable_width <= 0:
                row_specs = []
                break

            cell_width = usable_width / row_size
            preferred_heights = [
                cell_width / max(0.05, screen.request.size.width / screen.request.size.height)
                for screen in row_screens
            ]
            ideal_height = sum(preferred_heights) / len(preferred_heights)
            ideal_height_sum += ideal_height
            row_specs.append((row_screens, usable_width, ideal_height))

        if not row_specs or ideal_height_sum <= 0:
            continue

        row_heights = [
            max(1, round(usable_height * ideal_height / ideal_height_sum))
            for _row_screens, _usable_width, ideal_height in row_specs
        ]
        row_heights[-1] += usable_height - sum(row_heights)
        if row_heights[-1] <= 0:
            continue

        layout: dict[int, tuple[int, int, int, int]] = {}
        used_area = 0
        row_y = y0

        for (row_screens, usable_width, _ideal_height), row_height in zip(
            row_specs,
            row_heights,
        ):
            row_size = len(row_screens)
            cell_widths = [usable_width // row_size] * row_size
            cell_widths[-1] += usable_width - sum(cell_widths)

            cell_x = x0
            for screen, cell_width in zip(row_screens, cell_widths):
                preferred_ratio = (
                    screen.request.size.width / screen.request.size.height
                )
                rect = _fit_ratio_inside_cell(
                    cell_x,
                    row_y,
                    max(1, cell_width),
                    max(1, row_height),
                    preferred_ratio,
                    GROUP_ASPECT_WIGGLE_FRACTION,
                )
                layout[screen.screen_id] = rect
                used_area += rect[2] * rect[3]
                cell_x += cell_width + GROUP_WINDOW_GAP_PX

            row_y += row_height + GROUP_WINDOW_GAP_PX

        if used_area > best_score:
            best_score = used_area
            best_layout = layout

    return best_layout


class OrganizerWindow:
    """
    Native Win32 geometry-master window for one scrcpy screen group.

    The organizer is deliberately dependency-free: it creates one ordinary
    resizable top-level Win32 window with ctypes, debounces WM_MOVE/WM_SIZE, and
    emits its client rectangle through the manager's thread-safe event queue.
    scrcpy windows remain independent top-level windows.
    """

    def __init__(
        self,
        group_id: int,
        member_count: int,
        events: "queue.SimpleQueue[GroupWindowEvent]",
    ) -> None:
        self.group_id = group_id
        self._member_count = member_count
        self._events = events
        self._stop_event = threading.Event()
        self._member_lock = threading.Lock()
        self._window_lock = threading.Lock()
        self._hwnd: int | None = None
        self._thread = threading.Thread(
            target=self._run,
            name=f"scrcpy-organizer-{group_id:02d}",
            daemon=True,
        )
        self._thread.start()

    def set_member_count(self, member_count: int) -> None:
        """Update the organizer title without coupling manager and GUI threads."""
        with self._member_lock:
            self._member_count = member_count

        hwnd = self._current_hwnd()
        if hwnd is not None and os.name == "nt":
            import ctypes
            from ctypes import wintypes

            WM_APP_UPDATE_TITLE = 0x8001
            user32 = ctypes.windll.user32
            user32.PostMessageW.argtypes = [
                wintypes.HWND,
                wintypes.UINT,
                wintypes.WPARAM,
                wintypes.LPARAM,
            ]
            user32.PostMessageW.restype = wintypes.BOOL
            user32.PostMessageW(
                hwnd,
                WM_APP_UPDATE_TITLE,
                0,
                0,
            )

    def place_behind(self, foreground_hwnd: int) -> None:
        """
        Place the organizer immediately behind one group member.

        Member windows are moved to HWND_TOP in deterministic sequence during a
        layout pass. The first member processed therefore becomes the lowest
        member in that little stack. Putting the organizer directly behind that
        window keeps the whole group together in z-order without pinning the
        organizer beneath unrelated applications.
        """
        hwnd = self._current_hwnd()
        if hwnd is None or os.name != "nt":
            return

        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        user32.SetWindowPos.argtypes = [
            wintypes.HWND,
            wintypes.HWND,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            wintypes.UINT,
        ]
        user32.SetWindowPos.restype = wintypes.BOOL

        SWP_NOSIZE = 0x0001
        SWP_NOMOVE = 0x0002
        SWP_NOACTIVATE = 0x0010
        user32.SetWindowPos(
            hwnd,
            foreground_hwnd,
            0,
            0,
            0,
            0,
            SWP_NOSIZE | SWP_NOMOVE | SWP_NOACTIVATE,
        )

    def close(self) -> None:
        """Request native-window shutdown and briefly wait for its UI thread."""
        self._stop_event.set()
        hwnd = self._current_hwnd()
        if hwnd is not None and os.name == "nt":
            import ctypes
            from ctypes import wintypes

            WM_CLOSE = 0x0010
            user32 = ctypes.windll.user32
            user32.PostMessageW.argtypes = [
                wintypes.HWND,
                wintypes.UINT,
                wintypes.WPARAM,
                wintypes.LPARAM,
            ]
            user32.PostMessageW.restype = wintypes.BOOL
            user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)

        if threading.current_thread() is not self._thread:
            self._thread.join(timeout=1.0)

    def _current_member_count(self) -> int:
        with self._member_lock:
            return self._member_count

    def _current_hwnd(self) -> int | None:
        with self._window_lock:
            return self._hwnd

    def _set_hwnd(self, hwnd: int | None) -> None:
        with self._window_lock:
            self._hwnd = hwnd

    def _window_title(self) -> str:
        return (
            f"scrcpy group {self.group_id:02d} — "
            f"{self._current_member_count()} screens"
        )

    def _run(self) -> None:
        if os.name != "nt":
            self._events.put(
                GroupWindowEvent(
                    self.group_id,
                    "error",
                    detail="native organizer requires Windows",
                )
            )
            return

        try:
            self._run_windows()
        except Exception as exc:
            self._events.put(
                GroupWindowEvent(
                    self.group_id,
                    "error",
                    detail=f"{type(exc).__name__}: {exc}",
                )
            )

    def _run_windows(self) -> None:
        """Own one native Win32 window and its message pump on this thread."""
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32

        WM_CLOSE = 0x0010
        WM_DESTROY = 0x0002
        WM_MOVE = 0x0003
        WM_SIZE = 0x0005
        WM_TIMER = 0x0113
        WM_GETMINMAXINFO = 0x0024
        WM_APP_UPDATE_TITLE = 0x8001

        TIMER_LAYOUT = 1
        debounce_ms = max(1, round(GROUP_RESIZE_DEBOUNCE_SECONDS * 1000))

        WS_OVERLAPPEDWINDOW = 0x00CF0000
        WS_VISIBLE = 0x10000000
        CW_USEDEFAULT = -2147483648
        SW_SHOW = 5
        COLOR_APPWORKSPACE = 12
        IDC_ARROW = 32512

        wndproc_type = ctypes.WINFUNCTYPE(
            ctypes.c_ssize_t,
            wintypes.HWND,
            wintypes.UINT,
            wintypes.WPARAM,
            wintypes.LPARAM,
        )

        class WindowClass(ctypes.Structure):
            _fields_ = [
                ("cbSize", wintypes.UINT),
                ("style", wintypes.UINT),
                ("lpfnWndProc", wndproc_type),
                ("cbClsExtra", ctypes.c_int),
                ("cbWndExtra", ctypes.c_int),
                ("hInstance", wintypes.HINSTANCE),
                ("hIcon", wintypes.HICON),
                ("hCursor", wintypes.HCURSOR),
                ("hbrBackground", wintypes.HBRUSH),
                ("lpszMenuName", wintypes.LPCWSTR),
                ("lpszClassName", wintypes.LPCWSTR),
                ("hIconSm", wintypes.HICON),
            ]

        class MinMaxInfo(ctypes.Structure):
            _fields_ = [
                ("ptReserved", wintypes.POINT),
                ("ptMaxSize", wintypes.POINT),
                ("ptMaxPosition", wintypes.POINT),
                ("ptMinTrackSize", wintypes.POINT),
                ("ptMaxTrackSize", wintypes.POINT),
            ]

        # Pointer-sized parameters and return values must be declared explicitly
        # on 64-bit Windows; ctypes otherwise assumes c_int for unannotated APIs.
        kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
        kernel32.GetModuleHandleW.restype = wintypes.HMODULE

        user32.LoadCursorW.restype = wintypes.HCURSOR
        user32.GetSysColorBrush.argtypes = [ctypes.c_int]
        user32.GetSysColorBrush.restype = wintypes.HBRUSH

        user32.RegisterClassExW.argtypes = [ctypes.POINTER(WindowClass)]
        user32.RegisterClassExW.restype = ctypes.c_ushort
        user32.UnregisterClassW.argtypes = [
            wintypes.LPCWSTR,
            wintypes.HINSTANCE,
        ]
        user32.UnregisterClassW.restype = wintypes.BOOL

        user32.CreateWindowExW.argtypes = [
            wintypes.DWORD,
            wintypes.LPCWSTR,
            wintypes.LPCWSTR,
            wintypes.DWORD,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            wintypes.HWND,
            wintypes.HANDLE,
            wintypes.HINSTANCE,
            wintypes.LPVOID,
        ]
        user32.CreateWindowExW.restype = wintypes.HWND

        user32.DefWindowProcW.argtypes = [
            wintypes.HWND,
            wintypes.UINT,
            wintypes.WPARAM,
            wintypes.LPARAM,
        ]
        user32.DefWindowProcW.restype = ctypes.c_ssize_t

        user32.SetTimer.argtypes = [
            wintypes.HWND,
            ctypes.c_size_t,
            wintypes.UINT,
            wintypes.LPVOID,
        ]
        user32.SetTimer.restype = ctypes.c_size_t
        user32.KillTimer.argtypes = [wintypes.HWND, ctypes.c_size_t]
        user32.KillTimer.restype = wintypes.BOOL

        user32.SetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPCWSTR]
        user32.SetWindowTextW.restype = wintypes.BOOL
        user32.DestroyWindow.argtypes = [wintypes.HWND]
        user32.DestroyWindow.restype = wintypes.BOOL
        user32.IsWindow.argtypes = [wintypes.HWND]
        user32.IsWindow.restype = wintypes.BOOL
        user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
        user32.ShowWindow.restype = wintypes.BOOL
        user32.UpdateWindow.argtypes = [wintypes.HWND]
        user32.UpdateWindow.restype = wintypes.BOOL
        user32.PostMessageW.argtypes = [
            wintypes.HWND,
            wintypes.UINT,
            wintypes.WPARAM,
            wintypes.LPARAM,
        ]
        user32.PostMessageW.restype = wintypes.BOOL
        user32.PostQuitMessage.argtypes = [ctypes.c_int]

        user32.GetMessageW.argtypes = [
            ctypes.POINTER(wintypes.MSG),
            wintypes.HWND,
            wintypes.UINT,
            wintypes.UINT,
        ]
        user32.GetMessageW.restype = wintypes.BOOL
        user32.TranslateMessage.argtypes = [ctypes.POINTER(wintypes.MSG)]
        user32.TranslateMessage.restype = wintypes.BOOL
        user32.DispatchMessageW.argtypes = [ctypes.POINTER(wintypes.MSG)]
        user32.DispatchMessageW.restype = ctypes.c_ssize_t

        hinstance = kernel32.GetModuleHandleW(None)
        class_name = (
            f"ScrcpyOrganizer_{os.getpid()}_{self.group_id}_"
            f"{threading.get_ident()}"
        )

        def schedule_geometry(hwnd: int) -> None:
            user32.KillTimer(hwnd, TIMER_LAYOUT)
            user32.SetTimer(hwnd, TIMER_LAYOUT, debounce_ms, None)

        @wndproc_type
        def wndproc(
            hwnd: int,
            message: int,
            wparam: int,
            lparam: int,
        ) -> int:
            if message in {WM_MOVE, WM_SIZE}:
                schedule_geometry(hwnd)
                return 0

            if message == WM_TIMER and wparam == TIMER_LAYOUT:
                user32.KillTimer(hwnd, TIMER_LAYOUT)
                if not self._stop_event.is_set():
                    rect = win32_client_rect_on_screen(int(hwnd))
                    if rect is not None:
                        self._events.put(
                            GroupWindowEvent(
                                self.group_id,
                                "geometry",
                                rect=rect,
                            )
                        )
                return 0

            if message == WM_APP_UPDATE_TITLE:
                user32.SetWindowTextW(hwnd, self._window_title())
                return 0

            if message == WM_GETMINMAXINFO:
                info = ctypes.cast(
                    lparam,
                    ctypes.POINTER(MinMaxInfo),
                ).contents
                info.ptMinTrackSize.x = GROUP_WINDOW_MIN_WIDTH
                info.ptMinTrackSize.y = GROUP_WINDOW_MIN_HEIGHT
                return 0

            if message == WM_CLOSE:
                if not self._stop_event.is_set():
                    self._events.put(
                        GroupWindowEvent(self.group_id, "closed")
                    )
                user32.DestroyWindow(hwnd)
                return 0

            if message == WM_DESTROY:
                self._set_hwnd(None)
                user32.PostQuitMessage(0)
                return 0

            return int(user32.DefWindowProcW(hwnd, message, wparam, lparam))

        window_class = WindowClass()
        window_class.cbSize = ctypes.sizeof(WindowClass)
        window_class.style = 0
        window_class.lpfnWndProc = wndproc
        window_class.cbClsExtra = 0
        window_class.cbWndExtra = 0
        window_class.hInstance = hinstance
        window_class.hIcon = None
        window_class.hCursor = user32.LoadCursorW(None, IDC_ARROW)
        window_class.hbrBackground = user32.GetSysColorBrush(COLOR_APPWORKSPACE)
        window_class.lpszMenuName = None
        window_class.lpszClassName = class_name
        window_class.hIconSm = None

        atom = user32.RegisterClassExW(ctypes.byref(window_class))
        if not atom:
            raise ctypes.WinError()

        hwnd: int | None = None
        try:
            hwnd_value = user32.CreateWindowExW(
                0,
                class_name,
                self._window_title(),
                WS_OVERLAPPEDWINDOW | WS_VISIBLE,
                CW_USEDEFAULT,
                CW_USEDEFAULT,
                GROUP_WINDOW_INITIAL_WIDTH,
                GROUP_WINDOW_INITIAL_HEIGHT,
                None,
                None,
                hinstance,
                None,
            )
            if not hwnd_value:
                raise ctypes.WinError()

            hwnd = int(hwnd_value)
            self._set_hwnd(hwnd)

            user32.ShowWindow(hwnd, SW_SHOW)
            user32.UpdateWindow(hwnd)
            schedule_geometry(hwnd)

            # close() may race with window creation. Honor an already-pending
            # stop request immediately instead of entering a stranded pump.
            if self._stop_event.is_set():
                user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)

            message = wintypes.MSG()
            while True:
                result = user32.GetMessageW(
                    ctypes.byref(message),
                    None,
                    0,
                    0,
                )
                if result == -1:
                    raise ctypes.WinError()
                if result == 0:
                    break
                user32.TranslateMessage(ctypes.byref(message))
                user32.DispatchMessageW(ctypes.byref(message))
        finally:
            self._set_hwnd(None)
            if hwnd is not None and user32.IsWindow(hwnd):
                user32.DestroyWindow(hwnd)
            user32.UnregisterClassW(class_name, hinstance)


# =============================================================================
# TERMINAL ABSTRACTION
# =============================================================================


class TerminalUI:
    """Small ANSI/keyboard abstraction with Windows and POSIX key decoding."""

    def __init__(self) -> None:
        self._entered = False
        self._posix_fd: int | None = None
        self._posix_saved_attributes: object | None = None
        self._last_frame: str | None = None

    def __enter__(self) -> "TerminalUI":
        if not (sys.stdin.isatty() and sys.stdout.isatty()):
            raise LaunchError("Interactive mode requires an interactive terminal (TTY).")

        self._entered = True
        if os.name != "nt":
            import termios
            import tty

            self._posix_fd = sys.stdin.fileno()
            self._posix_saved_attributes = termios.tcgetattr(self._posix_fd)
            tty.setcbreak(self._posix_fd)

        # Alternate screen + hidden cursor + DECAWM off. Disabling terminal
        # autowrap lets the frame safely occupy the physical last column
        # without the right border wrapping into the next row.
        sys.stdout.write("\x1b[?1049h\x1b[?25l\x1b[?7l")
        sys.stdout.flush()
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self._restore_posix_input()
        # Restore autowrap before leaving the alternate screen.
        sys.stdout.write("\x1b[0m\x1b[?7h\x1b[?25h\x1b[?1049l")
        sys.stdout.flush()
        self._entered = False

    def _restore_posix_input(self) -> None:
        if os.name == "nt" or self._posix_fd is None or self._posix_saved_attributes is None:
            return
        import termios

        termios.tcsetattr(self._posix_fd, termios.TCSADRAIN, self._posix_saved_attributes)

    def _enable_posix_cbreak(self) -> None:
        if os.name == "nt" or self._posix_fd is None:
            return
        import tty

        tty.setcbreak(self._posix_fd)

    @contextmanager
    def line_mode(self) -> Iterator[None]:
        """Temporarily restore conventional line input for dialog prompts."""
        self._restore_posix_input()
        sys.stdout.write("\x1b[?25h")
        sys.stdout.flush()
        try:
            yield
        finally:
            self._enable_posix_cbreak()
            sys.stdout.write("\x1b[?25l")
            sys.stdout.flush()

    def draw(self, content: str, *, force: bool = False) -> None:
        """
        Redraw only when the frame changed.

        The manager calls this on every timed UI tick, so process/log changes and
        terminal resizes appear without keyboard input while identical frames do
        not cause pointless terminal repaint traffic.
        """
        if not force and content == self._last_frame:
            return
        self._last_frame = content
        sys.stdout.write("\x1b[H\x1b[2J" + content)
        sys.stdout.flush()

    def clear_for_dialog(self, title: str) -> None:
        width, _ = terminal_dimensions()
        self._last_frame = None
        header = f"{ICON_TERMINAL}  {title}"
        sys.stdout.write("\x1b[H\x1b[2J" + ANSI_BOLD + header + ANSI_RESET + "\n")
        sys.stdout.write(terminal_rule(width) + "\n\n")
        sys.stdout.flush()

    def read_key(self, timeout: float = UI_REFRESH_SECONDS) -> str | None:
        """Return a normalized key name, or None when only the refresh timer fired."""
        if os.name == "nt":
            return self._read_key_windows(timeout)
        return self._read_key_posix(timeout)

    @staticmethod
    def _read_key_windows(timeout: float) -> str | None:
        import msvcrt

        deadline = time.monotonic() + timeout
        while not msvcrt.kbhit():
            if time.monotonic() >= deadline:
                return None
            time.sleep(min(0.02, max(0.0, deadline - time.monotonic())))

        char = msvcrt.getwch()
        if char in {"\x00", "\xe0"}:
            extended = msvcrt.getwch()
            return {
                "H": "UP",
                "P": "DOWN",
                "K": "LEFT",
                "M": "RIGHT",
                "G": "HOME",
                "O": "END",
                "I": "PAGE_UP",
                "Q": "PAGE_DOWN",
                "S": "DELETE",
            }.get(extended, "UNKNOWN")

        return TerminalUI._normalize_character_key(char)

    @staticmethod
    def _read_key_posix(timeout: float) -> str | None:
        import select

        ready, _, _ = select.select([sys.stdin], [], [], timeout)
        if not ready:
            return None

        char = sys.stdin.read(1)
        if char != "\x1b":
            return TerminalUI._normalize_character_key(char)

        sequence = ""
        while True:
            ready, _, _ = select.select([sys.stdin], [], [], 0.005)
            if not ready:
                break
            sequence += sys.stdin.read(1)
            if sequence and (sequence[-1].isalpha() or sequence[-1] == "~"):
                break

        return {
            "": "ESC",
            "[A": "UP",
            "[B": "DOWN",
            "[C": "RIGHT",
            "[D": "LEFT",
            "[H": "HOME",
            "[F": "END",
            "[1~": "HOME",
            "[4~": "END",
            "[5~": "PAGE_UP",
            "[6~": "PAGE_DOWN",
            "[3~": "DELETE",
        }.get(sequence, "UNKNOWN")

    @staticmethod
    def _normalize_character_key(char: str) -> str:
        return {
            "\r": "ENTER",
            "\n": "ENTER",
            "\x1b": "ESC",
            "\x03": "CTRL_C",
            "\x09": "TAB",
            "\x12": "CTRL_R",
            "\x08": "BACKSPACE",
            "\x7f": "BACKSPACE",
            " ": "SPACE",
        }.get(char, char.lower())


# =============================================================================
# INTERACTIVE MANAGER
# =============================================================================


class VirtualScreenManager:
    """Keyboard-driven 90s-terminal manager for multiple scrcpy processes."""

    def __init__(self, scrcpy: str, defaults: ScreenDefaults) -> None:
        self.scrcpy = scrcpy
        self.defaults = defaults
        self.screens: dict[int, ManagedScreen] = {}
        self.next_screen_id = 1
        self.controller: ObservedProcess | None = None
        self.selected_index = 0
        self.expanded_key: str | None = None
        self.submenu_index = 0
        self.terminal: TerminalUI | None = None
        self._log_directory = tempfile.TemporaryDirectory(prefix="scrcpy-screen-manager-")
        self.log_root = Path(self._log_directory.name)
        self._installed_apps: tuple[InstalledApp, ...] | None = None
        self.groups: dict[int, ManagedGroup] = {}
        self.next_group_id = 1
        self._group_events: queue.SimpleQueue[GroupWindowEvent] = queue.SimpleQueue()

    def run(self) -> int:
        """Run until the operator selects Quit or sends Ctrl+C."""
        try:
            with TerminalUI() as terminal:
                self.terminal = terminal
                while True:
                    self._maintain_groups()
                    items = self._menu_items()
                    self.selected_index = min(self.selected_index, max(0, len(items) - 1))
                    terminal.draw(self._render(items))
                    key = terminal.read_key(UI_REFRESH_SECONDS)
                    if key is None:
                        continue
                    if key == "CTRL_C":
                        return EXIT_OK
                    if self._handle_key(key, items):
                        return EXIT_OK
        finally:
            self._shutdown()
            try:
                self._log_directory.cleanup()
            except OSError:
                # A truly unkillable child may still hold its spool file open on
                # Windows. Never mask manager shutdown with temp cleanup failure.
                pass
            self.terminal = None

    def _menu_items(self) -> list[MenuItem]:
        items = [MenuItem("controller", "controller")]
        items.extend(
            MenuItem(f"screen:{screen_id}", "screen", screen_id)
            for screen_id in sorted(self.screens)
        )
        items.extend(
            [
                MenuItem("action:add", "action_add"),
                MenuItem("action:group", "action_group"),
                MenuItem("action:apps", "action_apps"),
                MenuItem("action:defaults", "action_defaults"),
                MenuItem("action:help", "action_help"),
                MenuItem("action:quit", "action_quit"),
            ]
        )
        return items

    def _handle_key(self, key: str, items: list[MenuItem]) -> bool:
        selected = items[self.selected_index]
        actions = self._submenu_actions(selected)

        if key == "q" and self.expanded_key is None:
            return True
        if key == "a" and self.expanded_key is None:
            self._action_add()
            return False
        if key == "f" and self.expanded_key is None:
            self._action_browse_apps()
            return False
        if key == "g" and self.expanded_key is None:
            self._action_create_group()
            return False
        if key == "d" and self.expanded_key is None:
            self._run_dialog("NEW-SCREEN DEFAULTS", self._action_defaults)
            return False
        if key in {"h", "?"} and self.expanded_key is None:
            self._show_help()
            return False

        if key == "UP":
            self.selected_index = (self.selected_index - 1) % len(items)
            self._collapse_if_selection_changed(items)
            return False
        if key == "DOWN":
            self.selected_index = (self.selected_index + 1) % len(items)
            self._collapse_if_selection_changed(items)
            return False
        if key in {"LEFT", "RIGHT"} and self.expanded_key == selected.key and actions:
            delta = -1 if key == "LEFT" else 1
            self.submenu_index = (self.submenu_index + delta) % len(actions)
            return False
        if key == "ESC":
            self.expanded_key = None
            self.submenu_index = 0
            return False
        if key == "ENTER":
            if selected.kind.startswith("action_"):
                return self._invoke_top_level_action(selected.kind)

            if self.expanded_key != selected.key:
                self.expanded_key = selected.key
                self.submenu_index = 0
                return False

            if not actions:
                self.expanded_key = None
                return False

            self.submenu_index = min(self.submenu_index, len(actions) - 1)
            self._invoke_submenu_action(selected, actions[self.submenu_index])
            return False

        return False

    def _collapse_if_selection_changed(self, items: list[MenuItem]) -> None:
        selected = items[self.selected_index]
        if self.expanded_key != selected.key:
            self.expanded_key = None
            self.submenu_index = 0

    def _invoke_top_level_action(self, kind: str) -> bool:
        if kind == "action_add":
            self._action_add()
        elif kind == "action_group":
            self._action_create_group()
        elif kind == "action_apps":
            self._action_browse_apps()
        elif kind == "action_defaults":
            self._run_dialog("NEW-SCREEN DEFAULTS", self._action_defaults)
        elif kind == "action_help":
            self._show_help()
        elif kind == "action_quit":
            return True
        return False

    def _submenu_actions(self, item: MenuItem) -> list[SubmenuAction]:
        if item.kind == "controller":
            actions = [
                SubmenuAction(
                    "console",
                    f"Console history ({self._controller_line_count()} lines)",
                    ICON_LOG,
                )
            ]
            if self.controller is None or self.controller.poll() is not None:
                actions.append(SubmenuAction("restart_controller", "Start controller", ICON_RESTART))
            return actions

        if item.kind != "screen" or item.screen_id is None:
            return []

        screen = self.screens[item.screen_id]
        actions = [
            SubmenuAction(
                "console",
                f"Console history ({screen.process.line_count} lines)",
                ICON_LOG,
            )
        ]
        if screen.group_id is not None:
            actions.append(
                SubmenuAction("ungroup", "Remove from group", ICON_GROUP)
            )
        if screen.process.poll() is None:
            actions.append(SubmenuAction("stop", "Stop screen", ICON_STOP))
        else:
            actions.append(SubmenuAction("remove", "Remove record", ICON_REMOVE))
        return actions

    def _invoke_submenu_action(self, item: MenuItem, action: SubmenuAction) -> None:
        if action.action_id == "console":
            process = self._process_for_item(item)
            if process is None:
                self._show_log_viewer(
                    title="CTRL / DEVICE-STATE CONTROLLER",
                    process=None,
                    standby_message="Controller has not started yet; no console history exists.",
                )
            else:
                title = (
                    "CTRL / DEVICE-STATE CONTROLLER"
                    if item.kind == "controller"
                    else (
                        f"SCREEN {item.screen_id:02d} / "
                        f"{self.screens[item.screen_id].request.app or 'bare virtual display'}"
                    )
                )
                self._show_log_viewer(title=title, process=process)
            return

        if action.action_id == "restart_controller":
            try:
                self._ensure_controller()
            except LaunchError as exc:
                self._show_message("CONTROLLER START FAILED", str(exc))
            return

        if item.kind != "screen" or item.screen_id is None:
            return
        screen = self.screens[item.screen_id]

        if action.action_id == "ungroup":
            self._remove_screen_from_group(screen.screen_id)
            self.expanded_key = None
            self.submenu_index = 0
            return

        if action.action_id == "stop":
            graceful = screen.process.request_stop()
            self._remove_screen_from_group(screen.screen_id)
            if not graceful:
                self._show_message(
                    "FORCED TERMINATION",
                    f"Screen {screen.screen_id:02d} required the forced termination fallback.",
                )
            return

        if action.action_id == "remove":
            self._remove_screen_from_group(screen.screen_id)
            del self.screens[item.screen_id]
            self.expanded_key = None
            self.submenu_index = 0

    def _process_for_item(self, item: MenuItem) -> ObservedProcess | None:
        if item.kind == "controller":
            return self.controller
        if item.kind == "screen" and item.screen_id is not None:
            return self.screens[item.screen_id].process
        return None

    def _maintain_groups(self) -> None:
        """Consume organizer events, remove dead members, and retry pending layouts."""
        while True:
            try:
                event = self._group_events.get_nowait()
            except queue.Empty:
                break

            group = self.groups.get(event.group_id)
            if group is None:
                continue

            if event.kind == "geometry" and event.rect is not None:
                group.last_rect = event.rect
                group.pending_rect = event.rect
            elif event.kind == "closed":
                self._dissolve_group(event.group_id)
            elif event.kind == "error":
                detail = event.detail or "unknown organizer error"
                self._dissolve_group(event.group_id)
                self._show_message(
                    "GROUP ORGANIZER FAILED",
                    f"Group {event.group_id:02d}: {detail}",
                )

        for group_id in list(self.groups):
            group = self.groups.get(group_id)
            if group is None:
                continue

            for screen_id in list(group.screen_ids):
                screen = self.screens.get(screen_id)
                if screen is None or screen.process.poll() is not None:
                    self._remove_screen_from_group(screen_id)

            group = self.groups.get(group_id)
            if group is not None and group.pending_rect is not None:
                if self._layout_group(group):
                    group.pending_rect = None

    def _layout_group(self, group: ManagedGroup) -> bool:
        """Apply the best current portrait layout to every member window."""
        rect = group.pending_rect or group.last_rect
        if rect is None:
            return False

        screens: list[ManagedScreen] = []
        for screen_id in sorted(group.screen_ids):
            screen = self.screens.get(screen_id)
            if screen is None or screen.process.poll() is not None:
                continue

            if not win32_is_window(screen.window_handle):
                screen.window_handle = win32_visible_window_for_pid(
                    screen.process.pid or 0
                )
            if screen.window_handle is None:
                return False
            screens.append(screen)

        if len(screens) < 2:
            return False

        layout = calculate_group_layout(rect, screens)
        if len(layout) != len(screens):
            return False

        success = True
        for screen in screens:
            target = layout.get(screen.screen_id)
            if target is None or screen.window_handle is None:
                success = False
                continue
            if not win32_set_window_rect(screen.window_handle, target):
                screen.window_handle = None
                success = False

        if success and screens[0].window_handle is not None:
            # The organizer is normally the active window while the operator is
            # dragging/resizing it. Member windows above were deliberately moved
            # to HWND_TOP in sorted order, making the first one the lowest member
            # in the resulting stack. Put the organizer directly behind that
            # member, not at the global bottom of the desktop, so unrelated apps
            # cannot wedge themselves between the organizer and its screens.
            group.organizer.place_behind(screens[0].window_handle)

        return success

    def _action_create_group(self) -> None:
        """Select running ungrouped screens and create one geometry organizer."""
        if os.name != "nt":
            self._show_message(
                "GROUPS ARE WINDOWS-ONLY FOR NOW",
                "The organizer currently uses direct Win32 window positioning.",
            )
            return

        eligible = [
            screen
            for screen in self.screens.values()
            if screen.process.poll() is None and screen.group_id is None
        ]
        if len(eligible) < 2:
            self._show_message(
                "NOT ENOUGH UNGROUPED SCREENS",
                "Create at least two running ungrouped screens first.",
            )
            return

        selected_ids = self._show_group_picker(eligible)
        if selected_ids is None:
            return

        group_id = self.next_group_id
        organizer = OrganizerWindow(
            group_id,
            len(selected_ids),
            self._group_events,
        )
        group = ManagedGroup(
            group_id=group_id,
            screen_ids=set(selected_ids),
            organizer=organizer,
        )
        self.groups[group_id] = group
        self.next_group_id += 1

        for screen_id in selected_ids:
            self.screens[screen_id].group_id = group_id

    def _show_group_picker(
        self,
        eligible: Sequence[ManagedScreen],
    ) -> list[int] | None:
        """Checkbox picker used by Create Group."""
        terminal = self._require_terminal()
        screens = list(sorted(eligible, key=lambda screen: screen.screen_id))
        selected_index = 0
        checked = {screen.screen_id for screen in screens}
        top = 0

        while True:
            width, height = terminal_dimensions()
            inner_width = max(1, width - 2)
            inner_height = max(1, height - 2)
            body_height = max(1, inner_height - 5)

            selected_index = max(0, min(selected_index, len(screens) - 1))
            if selected_index < top:
                top = selected_index
            elif selected_index >= top + body_height:
                top = selected_index - body_height + 1
            top = max(0, min(top, max(0, len(screens) - body_height)))

            lines = [
                f" {ANSI_BOLD}{ANSI_FG_CYAN}{ICON_GROUP} CREATE GROUP{ANSI_RESET}",
                (
                    f" {ANSI_DIM}{len(checked)} selected / {len(screens)} eligible"
                    f"   aspect wiggle ±{GROUP_ASPECT_WIGGLE_FRACTION * 100:.0f}%{ANSI_RESET}"
                ),
                f"{ANSI_FG_CYAN}{terminal_rule(inner_width)}{ANSI_RESET}",
            ]

            visible = screens[top : top + body_height]
            for offset, screen in enumerate(visible):
                absolute = top + offset
                hovered = absolute == selected_index
                pointer = ICON_POINTER if hovered else " "
                mark = "x" if screen.screen_id in checked else " "
                app = screen.request.app or "(bare virtual display)"
                row = ellipsize(
                    f" {pointer} [{mark}] {ICON_SCREEN} "
                    f"Screen {screen.screen_id:02d}  {app}",
                    inner_width,
                )
                lines.append(
                    ANSI_REVERSE + row + ANSI_RESET if hovered else row
                )

            lines.extend(
                [""] * max(0, body_height - len(visible))
            )
            lines.append(
                f"{ANSI_DIM}Space toggle · A all · N none · Enter create · Esc cancel{ANSI_RESET}"
            )
            terminal.draw(compose_terminal_frame(lines, width, height))

            key = terminal.read_key(UI_REFRESH_SECONDS)
            if key is None:
                continue
            if key in {"ESC", "CTRL_C"}:
                return None
            if key == "UP":
                selected_index = (selected_index - 1) % len(screens)
            elif key == "DOWN":
                selected_index = (selected_index + 1) % len(screens)
            elif key == "PAGE_UP":
                selected_index = max(0, selected_index - body_height)
            elif key == "PAGE_DOWN":
                selected_index = min(
                    len(screens) - 1,
                    selected_index + body_height,
                )
            elif key == "HOME":
                selected_index = 0
            elif key == "END":
                selected_index = len(screens) - 1
            elif key == "SPACE":
                screen_id = screens[selected_index].screen_id
                if screen_id in checked:
                    checked.remove(screen_id)
                else:
                    checked.add(screen_id)
            elif key == "a":
                checked = {screen.screen_id for screen in screens}
            elif key == "n":
                checked.clear()
            elif key == "ENTER":
                if len(checked) >= 2:
                    return sorted(checked)

    def _remove_screen_from_group(self, screen_id: int) -> None:
        """Remove one screen and dissolve its group when fewer than two remain."""
        screen = self.screens.get(screen_id)
        if screen is None or screen.group_id is None:
            return

        group_id = screen.group_id
        screen.group_id = None
        group = self.groups.get(group_id)
        if group is None:
            return

        group.screen_ids.discard(screen_id)
        if len(group.screen_ids) < 2:
            self._dissolve_group(group_id)
            return

        group.organizer.set_member_count(len(group.screen_ids))
        if group.last_rect is not None:
            group.pending_rect = group.last_rect

    def _dissolve_group(self, group_id: int) -> None:
        """Release members and close one organizer without stopping scrcpy."""
        group = self.groups.pop(group_id, None)
        if group is None:
            return

        for screen_id in group.screen_ids:
            screen = self.screens.get(screen_id)
            if screen is not None and screen.group_id == group_id:
                screen.group_id = None

        group.organizer.close()

    def _ensure_controller(self) -> None:
        """Lazily start the single process that owns device-global state."""
        if self.controller is not None and self.controller.poll() is None:
            return

        command = command_for_device_state_controller(self.scrcpy)
        controller = ObservedProcess(
            command,
            label="device-state controller",
            log_path=self.log_root / "controller.log",
        )
        controller.start()
        controller.startup_probe()
        self.controller = controller

    def _action_add(self) -> None:
        """Choose an app source, then create one managed virtual display."""
        mode = self._show_choice_menu(
            title="ADD VIRTUAL SCREEN / APP SOURCE",
            choices=(
                (ICON_SEARCH, "Browse/search installed apps", "browse"),
                (ICON_TERMINAL, "Enter exact package manually", "manual"),
                (ICON_SCREEN, "Bare virtual display", "bare"),
            ),
        )
        if mode is None:
            return

        app: str | None
        if mode == "browse":
            selected = self._show_app_picker("SELECT INSTALLED APP")
            if selected is None:
                return
            app = selected.package
        elif mode == "manual":
            value: list[str | None] = [None]

            def prompt_manual() -> None:
                raw = input("Exact Android package [blank = cancel]: ").strip()
                value[0] = validate_app(raw) if raw else None

            self._run_dialog("ADD VIRTUAL SCREEN / MANUAL PACKAGE", prompt_manual)
            if value[0] is None:
                return
            app = value[0]
        else:
            app = None

        self._run_dialog(
            "ADD VIRTUAL SCREEN / SETTINGS",
            lambda: self._finish_add_screen(app),
        )

    def _finish_add_screen(self, app: str | None) -> None:
        try:
            use_defaults = self._prompt_yes_no(
                f"Use defaults ({self.defaults.size}, {self.defaults.max_fps} FPS, "
                f"{self.defaults.bitrate_spec} bitrate)?",
                default=True,
            )

            request = ScreenRequest(
                size=self.defaults.size,
                max_fps=self.defaults.max_fps,
                bitrate_spec=self.defaults.bitrate_spec,
                app=app,
            )
            if not use_defaults:
                request = ScreenRequest(
                    size=self._prompt_size("Size", request.size),
                    max_fps=self._prompt_fps("Max FPS", request.max_fps),
                    bitrate_spec=self._prompt_bitrate("Bitrate", request.bitrate_spec),
                    app=app,
                )

            self._ensure_controller()

            screen_id = self.next_screen_id
            command, bitrate = command_for_display(
                self.scrcpy,
                request,
                managed_screen_id=screen_id,
                interactive_managed=True,
            )
            process = ObservedProcess(
                command,
                label=f"screen {screen_id:02d}",
                log_path=self.log_root / f"screen_{screen_id:02d}.log",
            )
            process.start()
            process.startup_probe()

            self.screens[screen_id] = ManagedScreen(screen_id, request, bitrate, process)
            self.next_screen_id += 1
            print()
            print(f"{ICON_RUNNING} Screen {screen_id:02d} launched successfully.")
            print(printable_command(command))
            input("\nPress Enter to return to the manager...")
        except (ConfigurationError, LaunchError) as exc:
            print()
            print(f"{ICON_STOPPED} ADD FAILED")
            print(exc)
            input("\nPress Enter to return to the manager...")

    def _action_browse_apps(self) -> None:
        selected = self._show_app_picker("INSTALLED APPS / PACKAGE FINDER")
        if selected is None:
            return
        kind = "system app" if selected.is_system else "user app"
        self._show_message(
            "INSTALLED APP",
            f"{selected.name}\n{selected.package}\n\nType: {kind}",
        )

    def _load_installed_apps(self, *, force: bool = False) -> tuple[InstalledApp, ...]:
        if self._installed_apps is not None and not force:
            return self._installed_apps

        terminal = self._require_terminal()
        width, _ = terminal_dimensions()
        terminal.draw(
            "\n".join(
                [
                    f"{ANSI_BOLD}{ICON_APPS}  READING INSTALLED ANDROID APPS{ANSI_RESET}",
                    terminal_rule(width),
                    "",
                    f"{ICON_HEARTBEAT} scrcpy --list-apps",
                    "",
                    f"{ANSI_DIM}Android app labels may take several seconds to resolve...{ANSI_RESET}",
                ]
            ),
            force=True,
        )
        self._installed_apps = list_installed_apps(self.scrcpy)
        return self._installed_apps

    def _show_choice_menu(
        self,
        *,
        title: str,
        choices: Sequence[tuple[str, str, str]],
    ) -> str | None:
        terminal = self._require_terminal()
        selected = 0

        while True:
            width, _ = terminal_dimensions()
            lines = [
                f"{ANSI_BOLD}{ICON_POINTER}  {title}{ANSI_RESET}",
                terminal_rule(width),
                "",
            ]
            for index, (icon, label, _value) in enumerate(choices):
                pointer = ICON_POINTER if index == selected else " "
                row = ellipsize(f" {pointer}  {icon} {label}", max(1, width - 2))
                lines.append(
                    ANSI_REVERSE + row + ANSI_RESET if index == selected else row
                )
            lines.extend(
                [
                    "",
                    f"{ANSI_DIM}↑/↓ select   Enter confirm   Esc cancel{ANSI_RESET}",
                ]
            )
            terminal.draw("\n".join(lines))
            key = terminal.read_key(UI_REFRESH_SECONDS)
            if key is None:
                continue
            if key in {"ESC", "CTRL_C"}:
                return None
            if key == "UP":
                selected = (selected - 1) % len(choices)
            elif key == "DOWN":
                selected = (selected + 1) % len(choices)
            elif key == "ENTER":
                return choices[selected][2]

    def _show_app_picker(self, title: str) -> InstalledApp | None:
        """
        Live installed-app browser with three keyboard-focus regions.

        Focus order:
            app list -> living search input -> Back / Cancel

        The search is deliberately case-insensitive and matches both the
        human-readable app label and exact Android package name. Typing while
        Search is focused changes the result set immediately; Enter is not
        required.
        """
        terminal = self._require_terminal()
        try:
            apps = self._load_installed_apps()
        except LaunchError as exc:
            self._show_message("APP INVENTORY FAILED", str(exc))
            return None

        query = ""
        selected = 0
        top = 0
        focus = "list"

        while True:
            width, height = terminal_dimensions()
            inner_width = max(1, width - 2)
            inner_height = max(1, height - 2)
            folded = query.casefold()
            matches = [
                app
                for app in apps
                if not folded
                or folded in app.name.casefold()
                or folded in app.package.casefold()
            ]
            matches.sort(
                key=lambda app: (
                    not app.name.casefold().startswith(folded) if folded else False,
                    not app.package.casefold().startswith(folded) if folded else False,
                    app.is_system,
                    app.name.casefold(),
                    app.package.casefold(),
                )
            )

            if matches:
                selected = max(0, min(selected, len(matches) - 1))
            else:
                selected = 0
                if focus == "list":
                    focus = "search"

            # Reserve title/status above and divider/search/back/help below.
            body_height = max(1, inner_height - 6)
            if selected < top:
                top = selected
            elif selected >= top + body_height:
                top = selected - body_height + 1
            max_top = max(0, len(matches) - body_height)
            top = max(0, min(top, max_top))

            lines = [
                f"{ANSI_BOLD}{ANSI_FG_CYAN}{ICON_APPS}  {title}{ANSI_RESET}",
                f"{ANSI_FG_CYAN}{terminal_rule(width)}{ANSI_RESET}",
                f"{ANSI_DIM}{len(matches)} matches / {len(apps)} installed   "
                f"{ICON_REFRESH} Ctrl+R refresh inventory{ANSI_RESET}",
                "",
            ]

            visible = matches[top : top + body_height]
            if not visible:
                lines.append(f"  {ANSI_DIM}(no matching apps){ANSI_RESET}")

            for offset, app in enumerate(visible):
                absolute = top + offset
                hovered = focus == "list" and absolute == selected
                pointer = ICON_POINTER if hovered else " "
                app_icon = ICON_SYSTEM_APP if app.is_system else ICON_USER_APP
                kind = "SYS" if app.is_system else "USR"
                kind_style = ANSI_FG_YELLOW if app.is_system else ANSI_FG_GREEN

                prefix_plain = f" {pointer} {app_icon} {kind}  "
                available = max(1, inner_width - len(prefix_plain) - 1)
                combined = ellipsize(f"{app.name}  [{app.package}]", available)

                base_style = ANSI_REVERSE if hovered else ""
                prefix = (
                    f"{base_style} {pointer} "
                    f"{kind_style}{app_icon} {kind}{ANSI_RESET}{base_style}  "
                )
                highlighted = highlight_matches(
                    combined,
                    query,
                    base_style=base_style,
                )
                lines.append(prefix + highlighted + ANSI_RESET)

            # Fill the list viewport so Search and Back remain pinned near the
            # bottom edge of the surrounding full-terminal frame.
            list_rows_used = max(1, len(visible))
            lines.extend([""] * max(0, body_height - list_rows_used))
            lines.append(
                f"{ANSI_FG_CYAN}{terminal_rule(inner_width)}{ANSI_RESET}"
            )

            search_hovered = focus == "search"
            search_base = ANSI_REVERSE if search_hovered else ""
            search_value = query or "(empty — all apps)"
            search_prefix = f" {ICON_POINTER if search_hovered else ' '} {ICON_SEARCH} Search: "
            search_available = max(1, inner_width - len(search_prefix) - 1)
            visible_search = ellipsize(search_value, search_available)
            lines.append(
                search_base
                + search_prefix
                + (
                    highlight_matches(
                        visible_search,
                        query,
                        base_style=search_base,
                    )
                    if query
                    else visible_search
                )
                + ANSI_RESET
            )

            cancel_hovered = focus == "cancel"
            cancel_row = f" {ICON_POINTER if cancel_hovered else ' '} {ICON_BACK} Back / Cancel"
            lines.append(
                ANSI_REVERSE + ellipsize(cancel_row, max(1, inner_width - 1)) + ANSI_RESET
                if cancel_hovered
                else ellipsize(cancel_row, max(1, inner_width - 1))
            )

            lines.append(
                f"{ANSI_DIM}↑/↓ navigate · type to search · Tab focus · Enter select · "
                f"Ctrl+R refresh · Esc cancel{ANSI_RESET}"
            )
            terminal.draw(compose_terminal_frame(lines, width, height))

            key = terminal.read_key(UI_REFRESH_SECONDS)
            if key is None:
                continue
            if key in {"ESC", "CTRL_C"}:
                return None

            if key == "CTRL_R":
                try:
                    apps = self._load_installed_apps(force=True)
                    selected = 0
                    top = 0
                except LaunchError as exc:
                    self._show_message("APP INVENTORY FAILED", str(exc))
                continue

            if key == "TAB":
                focus = {
                    "list": "search",
                    "search": "cancel",
                    "cancel": "list" if matches else "search",
                }[focus]
                continue

            if focus == "search":
                if key == "UP":
                    if matches:
                        focus = "list"
                elif key == "DOWN":
                    focus = "cancel"
                elif key == "ENTER":
                    if matches:
                        focus = "list"
                elif key == "BACKSPACE":
                    query = query[:-1]
                    selected = 0
                    top = 0
                elif key == "SPACE":
                    query += " "
                    selected = 0
                    top = 0
                elif len(key) == 1 and key.isprintable():
                    query += key
                    selected = 0
                    top = 0
                continue

            if focus == "cancel":
                if key == "ENTER":
                    return None
                if key == "UP":
                    focus = "search"
                elif key == "DOWN" and matches:
                    focus = "list"
                continue

            # App-list focus. Typing starts a search immediately, so no
            # keyboard-layout-specific search shortcut is required.
            if key == "SPACE":
                focus = "search"
                query = " "
                selected = 0
                top = 0
                continue
            if len(key) == 1 and key.isprintable():
                focus = "search"
                query = key
                selected = 0
                top = 0
                continue

            if key == "ENTER" and matches:
                return matches[selected]
            if key == "UP" and matches:
                if selected == 0:
                    focus = "cancel"
                else:
                    selected -= 1
            elif key == "DOWN" and matches:
                if selected == len(matches) - 1:
                    focus = "search"
                else:
                    selected += 1
            elif key == "PAGE_UP" and matches:
                selected = max(0, selected - body_height)
            elif key == "PAGE_DOWN" and matches:
                selected = min(len(matches) - 1, selected + body_height)
            elif key == "HOME" and matches:
                selected = 0
            elif key == "END" and matches:
                selected = len(matches) - 1

    def _action_defaults(self) -> None:
        try:
            size = self._prompt_size("Default size", self.defaults.size)
            max_fps = self._prompt_fps("Default max FPS", self.defaults.max_fps)
            bitrate = self._prompt_bitrate("Default bitrate", self.defaults.bitrate_spec)
            self.defaults = ScreenDefaults(size=size, max_fps=max_fps, bitrate_spec=bitrate)
            print(f"\n{ICON_SETTINGS} New-screen defaults updated.")
            input("\nPress Enter to return to the manager...")
        except ConfigurationError as exc:
            print(f"\n{ICON_STOPPED} DEFAULT UPDATE FAILED\n{exc}")
            input("\nPress Enter to return to the manager...")

    def _run_dialog(self, title: str, action: Callable[[], None]) -> None:
        terminal = self._require_terminal()
        with terminal.line_mode():
            terminal.clear_for_dialog(title)
            action()

    def _show_message(self, title: str, message: str) -> None:
        terminal = self._require_terminal()
        with terminal.line_mode():
            terminal.clear_for_dialog(title)
            print(message)
            input("\nPress Enter to return to the manager...")

    def _show_help(self) -> None:
        terminal = self._require_terminal()
        width, height = terminal_dimensions()
        inner_width = max(1, width - 2)
        content = [
            f"{ANSI_BOLD}{ICON_HELP}  HELP / CONTROL MAP{ANSI_RESET}",
            f"{ANSI_FG_CYAN}{terminal_rule(inner_width)}{ANSI_RESET}",
            "",
            f"  {ICON_POINTER} Up / Down      Select controller, screen, or manager action",
            f"  {ICON_EXPAND} Enter           Expand a process entry / invoke selected action",
            f"  {ICON_SCROLL} Left / Right    Select an expanded submenu action",
            f"  {ICON_BACK} Esc              Collapse the current submenu",
            f"  {ICON_ADD} A                Add screen",
            f"  {ICON_GROUP} G                Create organizer group",
            f"  {ICON_APPS} F                Find installed app/package",
            f"  {ICON_SETTINGS} D                Edit defaults",
            f"  {ICON_HELP} H / ?            Help",
            f"  {ICON_QUIT} Q                Quit manager (and stop owned processes)",
            "",
            f"{ICON_CONTROLLER} Controller architecture",
            "  One hidden control-only scrcpy process owns --stay-awake,",
            "  --turn-screen-off and --keep-active. Managed displays receive",
            "  --no-power-on and never independently own those shared behaviors.",
            "",
            f"{ICON_LOG} Console history",
            "  Every process is fully spooled to a temporary log file. The list",
            "  shows only an ellipsized latest line. Console history opens a",
            "  scrollable viewer over the complete output generated this session.",
            "",
            f"{ICON_GROUP} Organizer groups (Windows)",
            "  Create Group selects two or more running ungrouped screens.",
            "  A normal resizable organizer window becomes their geometry master.",
            "  Closing it disbands the group; screens remain alive and independent.",
            "  Groups automatically dissolve when fewer than two members remain.",
            "",
            f"{ICON_APPS} Installed-app finder",
            "  Uses scrcpy's Android-side app inventory to search human app labels",
            "  and exact package names case-insensitively. Search is a focusable",
            "  live field: typing anywhere in the app list jumps into it immediately,",
            "  updates results without Enter, and highlights matched text.",
            "  The inventory is cached until Ctrl+R refreshes it.",
            "",
            f"{ANSI_DIM}Press Esc, Enter, Q, or H to return.{ANSI_RESET}",
        ]
        terminal.draw(compose_terminal_frame(content, width, height))
        while True:
            key = terminal.read_key(0.5)
            if key in {"ESC", "ENTER", "q", "h", "?", "CTRL_C"}:
                return

    def _show_log_viewer(
        self,
        *,
        title: str,
        process: ObservedProcess | None,
        standby_message: str | None = None,
    ) -> None:
        terminal = self._require_terminal()
        top = 0
        follow_tail = True

        while True:
            width, height = terminal_dimensions()
            inner_width = max(1, width - 2)
            inner_height = max(1, height - 2)
            logical_lines = process.read_all_lines() if process is not None else []
            visual_lines = self._wrap_log_lines(
                logical_lines,
                max(1, inner_width - 2),
            )
            if not visual_lines and standby_message:
                visual_lines = [standby_message]
            elif not visual_lines:
                visual_lines = ["(no console output yet)"]

            body_height = max(1, inner_height - 5)
            max_top = max(0, len(visual_lines) - body_height)
            if follow_tail:
                top = max_top
            else:
                top = max(0, min(top, max_top))

            visible = [
                colorize_scrcpy_log_line(line)
                for line in visual_lines[top : top + body_height]
            ]
            logical_count = process.line_count if process is not None else 0
            status = self._process_status(process)
            position = (
                f"{top + 1}-{min(len(visual_lines), top + body_height)} / "
                f"{len(visual_lines)} visual"
            )
            follow_text = "FOLLOW" if follow_tail else "PAUSED"

            header = [
                f"{ANSI_BOLD}{ICON_TERMINAL}  {title}{ANSI_RESET}",
                f"{ICON_HEARTBEAT} {status}    {ICON_LOG} {logical_count} logical lines    "
                f"{ICON_SCROLL} {position}    {follow_text}",
                f"{ANSI_FG_CYAN}{terminal_rule(inner_width)}{ANSI_RESET}",
            ]
            footer = [
                f"{ANSI_FG_CYAN}{terminal_rule(inner_width)}{ANSI_RESET}",
                f"{ANSI_DIM}↑/↓ line  PgUp/PgDn page  Home/End boundary  "
                f"R refresh/follow  Esc/Enter/Q back{ANSI_RESET}",
            ]
            terminal.draw(
                compose_terminal_frame(header + visible + footer, width, height)
            )

            key = terminal.read_key(UI_REFRESH_SECONDS)
            if key is None:
                continue
            if key in {"ESC", "ENTER", "q", "CTRL_C"}:
                return
            if key == "UP":
                follow_tail = False
                top = max(0, top - 1)
            elif key == "DOWN":
                top = min(max_top, top + 1)
                follow_tail = top >= max_top
            elif key == "PAGE_UP":
                follow_tail = False
                top = max(0, top - body_height)
            elif key == "PAGE_DOWN":
                top = min(max_top, top + body_height)
                follow_tail = top >= max_top
            elif key == "HOME":
                follow_tail = False
                top = 0
            elif key in {"END", "r"}:
                follow_tail = True
                top = max_top

    @staticmethod
    def _wrap_log_lines(lines: Sequence[str], width: int) -> list[str]:
        """Expand logical log lines into wrapped visual lines for full-history view."""
        output: list[str] = []
        for line in lines:
            clean = sanitize_log_line(line)
            wrapped = textwrap.wrap(
                clean,
                width=width,
                replace_whitespace=False,
                drop_whitespace=False,
                break_long_words=True,
                break_on_hyphens=False,
            )
            output.extend(wrapped or [""])
        return output

    def _render(self, items: list[MenuItem]) -> str:
        width, height = terminal_dimensions()
        inner_width = max(1, width - 2)
        inner_height = max(1, height - 2)
        running = sum(screen.process.poll() is None for screen in self.screens.values())

        if inner_width >= 90:
            status = (
                f" {ANSI_FG_GREEN}{ICON_SCREEN}{ANSI_RESET} "
                f"{len(self.screens)} displays / {running} running"
                f"    {ANSI_FG_MAGENTA}{ICON_GROUP}{ANSI_RESET} {len(self.groups)} groups"
                f"    {ANSI_FG_YELLOW}{ICON_SETTINGS}{ANSI_RESET} defaults "
                f"{self.defaults.size} · {self.defaults.max_fps} FPS · "
                f"{self.defaults.bitrate_spec}"
            )
            footer = (
                " ↑/↓ select   Enter expand/invoke   ←/→ submenu   "
                "Esc collapse   A add   G group   F apps   D defaults   H help   Q quit"
            )
        elif inner_width >= 58:
            status = (
                f" {ANSI_FG_GREEN}{ICON_SCREEN}{ANSI_RESET} "
                f"{running}/{len(self.screens)} running   "
                f"{ANSI_FG_YELLOW}{ICON_SETTINGS}{ANSI_RESET} "
                f"{self.defaults.size} · {self.defaults.max_fps}fps · "
                f"{self.defaults.bitrate_spec}"
            )
            footer = " ↑/↓ select · Enter · Esc · A add · G group · F apps · D defaults · H help · Q quit"
        else:
            status = (
                f" {ANSI_FG_GREEN}{ICON_SCREEN}{ANSI_RESET} "
                f"{running}/{len(self.screens)}   "
                f"{self.defaults.size} {self.defaults.max_fps}fps"
            )
            footer = " ↑↓ Enter Esc  A G F D H Q"

        title = (
            f" {ANSI_BOLD}{ANSI_FG_CYAN}{ICON_TERMINAL} "
            f"SCRCPY VIRTUAL DISPLAY CONTROL{ANSI_RESET}"
        )
        section = (
            f" {ANSI_BOLD}{ANSI_FG_BLUE}[ {ICON_SCREEN} SESSIONS / CONTROLS ]"
            f"{ANSI_RESET}"
        )
        divider = f"{ANSI_FG_CYAN}{terminal_rule(inner_width)}{ANSI_RESET}"

        fixed_rows = 5
        body_budget = max(0, inner_height - fixed_rows)

        blocks: list[list[str]] = []
        for index, item in enumerate(items):
            blocks.append(
                self._render_item(
                    item,
                    selected=index == self.selected_index,
                    width=inner_width,
                )
            )

        body = selected_viewport(blocks, self.selected_index, body_budget)
        content = [title, status, section]
        content.extend(body)

        reserved_bottom = 2
        filler = max(0, inner_height - len(content) - reserved_bottom)
        content.extend([""] * filler)
        content.extend([divider, f"{ANSI_DIM}{footer}{ANSI_RESET}"])

        return compose_terminal_frame(content, width, height)

    def _render_item(self, item: MenuItem, *, selected: bool, width: int) -> list[str]:
        pointer = ICON_POINTER if selected else " "
        expanded = self.expanded_key == item.key
        expander = ICON_COLLAPSE if expanded else ICON_EXPAND

        if item.kind == "controller":
            status = self._controller_status_short()
            pid = self.controller.pid if self.controller is not None else None
            row = (
                f" {pointer} {expander} {ICON_CONTROLLER} CTRL  {status:<9}  "
                f"pid={pid or '-':<7}  device-state controller"
            )
            process = self.controller
            latest = (
                "(standby — starts with first virtual screen)"
                if process is None
                else (process.latest_line or "(no console output yet)")
            )
            return self._render_process_block(item, row, latest, selected, width)

        if item.kind == "screen" and item.screen_id is not None:
            screen = self.screens[item.screen_id]
            pid = screen.process.pid or 0
            age = self._format_age(screen.age_seconds)
            app = screen.request.app or "(bare virtual display)"
            icon = ICON_RUNNING if screen.process.poll() is None else ICON_STOPPED
            group_badge = (
                f"G{screen.group_id:02d} "
                if screen.group_id is not None
                else ""
            )
            row = (
                f" {pointer} {expander} {ICON_SCREEN} {screen.screen_id:02d} "
                f"{group_badge:>4} "
                f"{icon} {screen.status:<8} pid={pid:<7} {age:<8} "
                f"{screen.request.size} {screen.request.max_fps}fps "
                f"{screen.bitrate.display_value}  {app}"
            )
            latest = screen.process.latest_line or "(no console output yet)"
            return self._render_process_block(item, row, latest, selected, width)

        action_data = {
            "action_add": (ICON_ADD, "Add virtual screen"),
            "action_group": (ICON_GROUP, "Create group"),
            "action_apps": (ICON_APPS, "Find installed app / package"),
            "action_defaults": (ICON_SETTINGS, "Edit new-screen defaults"),
            "action_help": (ICON_HELP, "Help / architecture notes"),
            "action_quit": (ICON_QUIT, "Quit manager"),
        }
        icon, label = action_data[item.kind]
        row = ellipsize(f" {pointer}   {icon} {label}", width)
        return [self._style_selected(row, selected)]

    def _render_process_block(
        self,
        item: MenuItem,
        row: str,
        latest: str,
        selected: bool,
        width: int,
    ) -> list[str]:
        # Keep a small width reserve because Nerd Font glyphs may occupy two
        # terminal cells even though Python len() counts one code point. This is
        # especially important for the always-visible log preview: it must never
        # wrap and destabilize the list layout.
        safe_width = max(1, width)
        output = [self._style_selected(ellipsize(row, safe_width), selected)]

        if self.expanded_key == item.key:
            actions = self._submenu_actions(item)
            if actions:
                rendered_actions = []
                for index, action in enumerate(actions):
                    label = f" {action.icon} {action.label} "
                    if index == self.submenu_index:
                        label = ANSI_REVERSE + label + ANSI_RESET
                    rendered_actions.append(label)
                submenu = "       ╰─ " + "   ".join(rendered_actions)
                output.append(ellipsize_ansi_safe(submenu, safe_width))

        log_prefix = f"       {ICON_LOG} "
        preview_width = max(1, safe_width - len(log_prefix) - 2)
        latest_preview = ellipsize(latest, preview_width)
        output.append(
            ANSI_DIM
            + log_prefix
            + colorize_scrcpy_log_line(latest_preview, base_style=ANSI_DIM)
            + ANSI_RESET
        )
        return output

    @staticmethod
    def _style_selected(text: str, selected: bool) -> str:
        return ANSI_REVERSE + text + ANSI_RESET if selected else text

    def _controller_status_short(self) -> str:
        if self.controller is None:
            return "STANDBY"
        code = self.controller.poll()
        return "RUNNING" if code is None else f"EXIT {code}"

    def _controller_line_count(self) -> int:
        return 0 if self.controller is None else self.controller.line_count

    @staticmethod
    def _process_status(process: ObservedProcess | None) -> str:
        if process is None:
            return "STANDBY"
        code = process.poll()
        return "RUNNING" if code is None else f"EXIT {code}"

    def _shutdown(self) -> None:
        for group_id in list(self.groups):
            self._dissolve_group(group_id)

        running = [screen for screen in self.screens.values() if screen.process.poll() is None]
        for screen in running:
            screen.process.request_stop()

        controller = self.controller
        if controller is not None and controller.poll() is None:
            graceful = controller.request_stop()
            if not graceful:
                print(
                    "\nWARNING: the device-state controller required forced termination. "
                    "scrcpy may not have had an opportunity to restore its saved "
                    "stay_on_while_plugged_in value.",
                    file=sys.stderr,
                )

    def _require_terminal(self) -> TerminalUI:
        if self.terminal is None:
            raise RuntimeError("Interactive terminal is not active.")
        return self.terminal

    def _prompt_size(self, label: str, current: DisplaySize) -> DisplaySize:
        text = input(f"{label} [{current}]: ").strip()
        return current if not text else DisplaySize.parse(text)

    def _prompt_fps(self, label: str, current: int) -> int:
        text = input(f"{label} [{current}]: ").strip()
        if not text:
            return current
        if not text.isdigit():
            raise ConfigurationError(f"{label} must be an integer.")
        return validate_max_fps(int(text))

    def _prompt_bitrate(self, label: str, current: str) -> str:
        text = input(f"{label} [{current}]: ").strip()
        return current if not text else normalize_bitrate_spec(text)

    @staticmethod
    def _prompt_yes_no(prompt: str, *, default: bool) -> bool:
        suffix = "[Y/n]" if default else "[y/N]"
        while True:
            text = input(f"{prompt} {suffix} ").strip().lower()
            if not text:
                return default
            if text in {"y", "yes"}:
                return True
            if text in {"n", "no"}:
                return False
            print("Please answer y or n.")

    @staticmethod
    def _format_age(seconds: int) -> str:
        hours, remainder = divmod(seconds, 3600)
        minutes, secs = divmod(remainder, 60)
        if hours:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"


def ellipsize_ansi_safe(text: str, width: int) -> str:
    """
    Conservative submenu fitting while preserving our own ANSI styling.

    Submenus are short; if they exceed the terminal, strip styling and emit an
    ordinary ellipsized line rather than risk cutting an escape sequence.
    """
    visible = ANSI_ESCAPE_PATTERN.sub("", text)
    if len(visible) <= width:
        return text
    return ellipsize(visible, width)


# =============================================================================
# DIRECT MODE
# =============================================================================


def run_direct(
    *,
    scrcpy: str,
    app: str | None,
    size: DisplaySize,
    max_fps: int,
    bitrate_spec: str,
) -> int:
    """Launch exactly one foreground scrcpy process and return its exit code."""
    app = validate_app(app)

    if app is not None:
        request = ScreenRequest(
            size=size,
            max_fps=max_fps,
            bitrate_spec=bitrate_spec,
            app=app,
        )
        command, bitrate = command_for_display(scrcpy, request)
        mode = "virtual display"
        geometry = str(size)
    else:
        command, bitrate = command_for_physical_display(
            scrcpy,
            max_fps=max_fps,
            bitrate_spec=bitrate_spec,
        )
        mode = "physical display"
        geometry = "device native"

    print("[SCRCPY APP / PRE-FLIGHT]")
    print(f"  Mode          : {mode}")
    print(f"  Package       : {app or '(none)'}")
    print(f"  Geometry      : {geometry}")
    print(f"  Max FPS       : {max_fps}")
    print(f"  Video bitrate : {bitrate.display_value} [{bitrate.source}]")
    print("  Host scaling  : arbitrary resize + stretched framebuffer")
    print("  Keep active   : enabled")
    print("  Stay awake    : enabled")
    print("  Phone screen  : off")
    print()
    print("[COMMAND]")
    print(f"  {printable_command(command)}")
    print()

    try:
        completed = subprocess.run(command, check=False)
    except OSError as exc:
        raise LaunchError(f"Failed to execute scrcpy: {exc}") from exc

    return int(completed.returncode)


# =============================================================================
# CLI / ENTRYPOINT
# =============================================================================


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=Path(sys.argv[0]).name,
        description=(
            "Launch scrcpy with small fixed virtual displays, or manage multiple "
            "virtual displays interactively."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s
  %(prog)s --size 360x800 --max-fps 45 --bitrate auto
  %(prog)s -i
  %(prog)s com.example.app
  %(prog)s com.example.app --size 360x800 --max-fps 45
  %(prog)s com.example.app --bitrate 4M
  %(prog)s --physical

With no app package, interactive mode is the default. Interactive mode
centralizes --stay-awake, --turn-screen-off and --keep-active in one hidden
scrcpy control process. Managed virtual-display processes use --no-power-on so
they do not wake the physical phone screen. Use --physical explicitly to mirror
the device's normal physical display instead.
""".strip(),
    )
    parser.add_argument(
        "app",
        nargs="?",
        help=(
            "Android package to start directly on a virtual display. "
            "Omit the package to enter interactive mode by default."
        ),
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Explicitly run the interactive multi-virtual-display manager.",
    )
    parser.add_argument(
        "--physical",
        action="store_true",
        help="Mirror the device's normal physical display instead of entering interactive mode.",
    )
    parser.add_argument(
        "--size",
        default=f"{DEFAULT_WIDTH}x{DEFAULT_HEIGHT}",
        metavar="WIDTHxHEIGHT",
        help=f"Virtual-display size (default: {DEFAULT_WIDTH}x{DEFAULT_HEIGHT}).",
    )
    parser.add_argument(
        "--max-fps",
        type=int,
        default=DEFAULT_MAX_FPS,
        metavar="FPS",
        help=f"Maximum video frame rate (default: {DEFAULT_MAX_FPS}).",
    )
    parser.add_argument(
        "--bitrate",
        default=DEFAULT_BITRATE_SPEC,
        metavar="RATE|auto",
        help="Video bitrate such as 4M or 2500K; default 'auto' derives it from virtual-display size.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        size = DisplaySize.parse(args.size)
        max_fps = validate_max_fps(args.max_fps)
        bitrate_spec = normalize_bitrate_spec(args.bitrate)
        app = validate_app(args.app)
        scrcpy = resolve_scrcpy_executable()

        if args.interactive and args.physical:
            parser.error("--interactive and --physical are mutually exclusive.")
        if args.physical and app is not None:
            parser.error("--physical does not accept an app package.")

        interactive_mode = args.interactive or (app is None and not args.physical)

        if interactive_mode:
            if app is not None:
                parser.error(
                    "Do not supply the positional app in interactive mode; "
                    "choose apps from Add screen."
                )

            manager = VirtualScreenManager(
                scrcpy=scrcpy,
                defaults=ScreenDefaults(
                    size=size,
                    max_fps=max_fps,
                    bitrate_spec=bitrate_spec,
                ),
            )
            return manager.run()

        return run_direct(
            scrcpy=scrcpy,
            app=app,
            size=size,
            max_fps=max_fps,
            bitrate_spec=bitrate_spec,
        )

    except ConfigurationError as exc:
        parser.error(str(exc))
    except LaunchError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return EXIT_DEPENDENCY
    except KeyboardInterrupt:
        print(file=sys.stderr)
        return 130

    return EXIT_RUNTIME


if __name__ == "__main__":
    raise SystemExit(main())
