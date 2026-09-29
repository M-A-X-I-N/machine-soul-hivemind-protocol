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
therefore strongly recommended.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from dataclasses import dataclass, field
import math
import os
from pathlib import Path
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
UI_REFRESH_SECONDS = 0.20

SIZE_PATTERN = re.compile(r"^(?P<width>[1-9][0-9]*)[xX](?P<height>[1-9][0-9]*)$")
BITRATE_PATTERN = re.compile(r"^(?P<number>[1-9][0-9]*)(?P<suffix>[kKmM]?)$")
ANSI_ESCAPE_PATTERN = re.compile(r"\x1b(?:\[[0-?]*[ -/]*[@-~]|[@-_])")

EXIT_OK = 0
EXIT_DEPENDENCY = 3
EXIT_RUNTIME = 4

# Nerd Font / terminal presentation glyphs. These are decoration only: control
# logic never depends on glyph width or successful font rendering.
ICON_POINTER = "󰜴"
ICON_CONTROLLER = "󰒋"
ICON_SCREEN = "󰍹"
ICON_RUNNING = "󰐊"
ICON_STOPPED = "󰅖"
ICON_STANDBY = "󰒲"
ICON_LOG = "󰆍"
ICON_ADD = "󰐕"
ICON_SETTINGS = "󰒓"
ICON_HELP = "󰋗"
ICON_QUIT = "󰈆"
ICON_STOP = "󰆴"
ICON_REMOVE = "󰆴"
ICON_RESTART = "󰜉"
ICON_EXPAND = "󰅂"
ICON_COLLAPSE = "󰅀"
ICON_BACK = "󰁍"
ICON_SCROLL = "󰹹"
ICON_INFO = "󰋽"
ICON_TERMINAL = ""
ICON_HEARTBEAT = "󰓅"

ANSI_RESET = "\x1b[0m"
ANSI_REVERSE = "\x1b[7m"
ANSI_DIM = "\x1b[2m"
ANSI_BOLD = "\x1b[1m"


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
    """Normalize an optional Android package name without over-policing scrcpy syntax."""
    if app is None:
        return None

    stripped = app.strip()
    if not stripped:
        return None
    if any(character.isspace() for character in stripped):
        raise ConfigurationError(f"App/package must not contain whitespace: {app!r}")
    return stripped


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
    --no-video --no-audio leaves a control-only scrcpy session with no window.
    """
    return [
        scrcpy,
        "--no-video",
        "--no-audio",
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
    """Convert arbitrary subprocess output into one harmless terminal UI line."""
    value = ANSI_ESCAPE_PATTERN.sub("", line)
    value = value.replace("\r", " ").replace("\n", " ").replace("\t", "    ")
    return "".join(character if character.isprintable() else "�" for character in value)


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


def terminal_dimensions() -> tuple[int, int]:
    """Return conservative terminal dimensions for deterministic rendering."""
    size = shutil.get_terminal_size(fallback=(100, 30))
    return max(50, size.columns), max(16, size.lines)


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
# TERMINAL ABSTRACTION
# =============================================================================


class TerminalUI:
    """Small ANSI/keyboard abstraction with Windows and POSIX key decoding."""

    def __init__(self) -> None:
        self._entered = False
        self._posix_fd: int | None = None
        self._posix_saved_attributes: object | None = None

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

        sys.stdout.write("\x1b[?1049h\x1b[?25l")
        sys.stdout.flush()
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self._restore_posix_input()
        sys.stdout.write("\x1b[0m\x1b[?25h\x1b[?1049l")
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

    def draw(self, content: str) -> None:
        """Redraw the alternate-screen surface from home."""
        sys.stdout.write("\x1b[H\x1b[2J" + content)
        sys.stdout.flush()

    def clear_for_dialog(self, title: str) -> None:
        width, _ = terminal_dimensions()
        header = f"{ICON_TERMINAL}  {title}"
        sys.stdout.write("\x1b[H\x1b[2J" + ANSI_BOLD + header + ANSI_RESET + "\n")
        sys.stdout.write("─" * min(width, 100) + "\n\n")
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

    def run(self) -> int:
        """Run until the operator selects Quit or sends Ctrl+C."""
        try:
            with TerminalUI() as terminal:
                self.terminal = terminal
                while True:
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
            self._run_dialog("ADD VIRTUAL SCREEN", self._action_add)
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
            self._run_dialog("ADD VIRTUAL SCREEN", self._action_add)
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

        if action.action_id == "stop":
            graceful = screen.process.request_stop()
            if not graceful:
                self._show_message(
                    "FORCED TERMINATION",
                    f"Screen {screen.screen_id:02d} required the forced termination fallback.",
                )
            return

        if action.action_id == "remove":
            del self.screens[item.screen_id]
            self.expanded_key = None
            self.submenu_index = 0

    def _process_for_item(self, item: MenuItem) -> ObservedProcess | None:
        if item.kind == "controller":
            return self.controller
        if item.kind == "screen" and item.screen_id is not None:
            return self.screens[item.screen_id].process
        return None

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
        try:
            app = validate_app(input("App/package [blank = bare virtual display]: "))
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
        width, _ = terminal_dimensions()
        content = [
            f"{ANSI_BOLD}{ICON_HELP}  HELP / CONTROL MAP{ANSI_RESET}",
            "─" * min(width, 100),
            "",
            f"  {ICON_POINTER} Up / Down      Select controller, screen, or manager action",
            f"  {ICON_EXPAND} Enter           Expand a process entry / invoke selected action",
            f"  {ICON_SCROLL} Left / Right    Select an expanded submenu action",
            f"  {ICON_BACK} Esc              Collapse the current submenu",
            f"  {ICON_ADD} A                Add screen",
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
            f"{ANSI_DIM}Press Esc, Enter, Q, or H to return.{ANSI_RESET}",
        ]
        terminal.draw("\n".join(content))
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
            logical_lines = process.read_all_lines() if process is not None else []
            visual_lines = self._wrap_log_lines(logical_lines, max(20, width - 4))
            if not visual_lines and standby_message:
                visual_lines = [standby_message]
            elif not visual_lines:
                visual_lines = ["(no console output yet)"]

            body_height = max(3, height - 7)
            max_top = max(0, len(visual_lines) - body_height)
            if follow_tail:
                top = max_top
            else:
                top = max(0, min(top, max_top))

            visible = visual_lines[top : top + body_height]
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
                "─" * min(width, 140),
            ]
            footer = [
                "─" * min(width, 140),
                f"{ANSI_DIM}↑/↓ line  PgUp/PgDn page  Home/End boundary  "
                f"R refresh/follow  Esc/Enter/Q back{ANSI_RESET}",
            ]
            terminal.draw("\n".join(header + visible + footer))

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
        width, _ = terminal_dimensions()
        running = sum(screen.process.poll() is None for screen in self.screens.values())
        lines = [
            f"{ANSI_BOLD}╔{'═' * min(width - 2, 98)}╗{ANSI_RESET}",
            f"{ANSI_BOLD}  {ICON_TERMINAL} SCRCPY VIRTUAL DISPLAY CONTROL{ANSI_RESET}",
            f"  {ICON_SCREEN} {len(self.screens)} displays / {running} running    "
            f"{ICON_SETTINGS} defaults {self.defaults.size} · "
            f"{self.defaults.max_fps} FPS · {self.defaults.bitrate_spec}",
            "",
            f"{ANSI_BOLD}[ {ICON_SCREEN} SESSIONS / CONTROLS ]{ANSI_RESET}",
        ]

        for index, item in enumerate(items):
            selected = index == self.selected_index
            lines.extend(self._render_item(item, selected=selected, width=width))

        lines.extend(
            [
                "",
                f"{ANSI_DIM}↑/↓ select   Enter expand/invoke   ←/→ submenu   "
                f"Esc collapse   A add   D defaults   H help   Q quit{ANSI_RESET}",
            ]
        )
        return "\n".join(lines)

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
            row = (
                f" {pointer} {expander} {ICON_SCREEN} {screen.screen_id:02d}    "
                f"{icon} {screen.status:<8} pid={pid:<7} {age:<8} "
                f"{screen.request.size} {screen.request.max_fps}fps "
                f"{screen.bitrate.display_value}  {app}"
            )
            latest = screen.process.latest_line or "(no console output yet)"
            return self._render_process_block(item, row, latest, selected, width)

        action_data = {
            "action_add": (ICON_ADD, "Add virtual screen"),
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
        safe_width = max(20, width - 4)
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
        output.append(
            ANSI_DIM + log_prefix + ellipsize(latest, preview_width) + ANSI_RESET
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
  %(prog)s com.example.app
  %(prog)s com.example.app --size 360x800 --max-fps 45
  %(prog)s com.example.app --bitrate 4M
  %(prog)s -i
  %(prog)s -i --size 360x800 --max-fps 45 --bitrate auto

Interactive mode centralizes --stay-awake, --turn-screen-off and --keep-active
in one hidden scrcpy control process. Managed virtual-display processes use
--no-power-on so they do not wake the physical phone screen.
""".strip(),
    )
    parser.add_argument(
        "app",
        nargs="?",
        help="Android package to start in direct mode. Omit to mirror the physical display.",
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Run the interactive multi-virtual-display manager.",
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

        if args.interactive:
            if app is not None:
                parser.error("Do not supply the positional app in interactive mode; choose apps from Add screen.")

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
