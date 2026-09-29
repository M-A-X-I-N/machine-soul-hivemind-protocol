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
  for the lifetime of the interactive manager.
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

No third-party Python packages are required.
"""

from __future__ import annotations

import argparse
from collections import deque
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
import threading
import time
from typing import Iterable, Sequence


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
LOG_BUFFER_LINES = 500

SIZE_PATTERN = re.compile(r"^(?P<width>[1-9][0-9]*)[xX](?P<height>[1-9][0-9]*)$")
BITRATE_PATTERN = re.compile(r"^(?P<number>[1-9][0-9]*)(?P<suffix>[kKmM]?)$")

EXIT_OK = 0
EXIT_DEPENDENCY = 3
EXIT_RUNTIME = 4


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
                "--verbosity=warn",
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
        "--verbosity=warn",
    ]


def printable_command(command: Sequence[str]) -> str:
    """Render argv for diagnostics only; this string is never executed."""
    if os.name == "nt":
        return subprocess.list2cmdline(list(command))
    return shlex.join(command)


# =============================================================================
# CHILD-PROCESS SUPERVISION
# =============================================================================


class ObservedProcess:
    """
    One scrcpy process with bounded in-memory log capture.

    stdout and stderr are merged and drained continuously by a daemon reader
    thread. This avoids both terminal-menu corruption and pipe-buffer deadlocks.
    """

    def __init__(self, command: Sequence[str], *, label: str) -> None:
        self.command = list(command)
        self.label = label
        self._lines: deque[str] = deque(maxlen=LOG_BUFFER_LINES)
        self._lock = threading.Lock()
        self._process: subprocess.Popen[str] | None = None
        self._reader: threading.Thread | None = None

    @property
    def pid(self) -> int | None:
        process = self._process
        return None if process is None else process.pid

    def start(self) -> None:
        if self._process is not None:
            raise LaunchError(f"{self.label} was already started.")

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
        for line in stream:
            with self._lock:
                self._lines.append(line.rstrip("\r\n"))

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

    def tail(self, line_count: int = 40) -> list[str]:
        with self._lock:
            lines = list(self._lines)
        return lines[-line_count:]

    def request_stop(self) -> bool:
        """
        Ask scrcpy to exit cleanly; force termination only as a fallback.

        Returning False means a forced fallback was required. This matters most
        for the device-state controller because normal scrcpy shutdown performs
        stay-awake restoration.
        """
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
# INTERACTIVE MANAGER
# =============================================================================


class VirtualScreenManager:
    """90s-terminal-style manager for multiple scrcpy virtual displays."""

    def __init__(self, scrcpy: str, defaults: ScreenDefaults) -> None:
        self.scrcpy = scrcpy
        self.defaults = defaults
        self.screens: dict[int, ManagedScreen] = {}
        self.next_screen_id = 1
        self.controller: ObservedProcess | None = None

    def run(self) -> int:
        """Run until the operator exits or input terminates."""
        try:
            while True:
                self._clear_terminal()
                self._render()

                try:
                    choice = input("\nCOMMAND> ").strip().lower()
                except EOFError:
                    choice = "q"

                if choice in {"1", "a", "add"}:
                    self._action_add()
                elif choice in {"2", "k", "kill"}:
                    self._action_kill()
                elif choice in {"3", "x", "kill-all", "killall"}:
                    self._action_kill_all()
                elif choice in {"4", "d", "defaults"}:
                    self._action_defaults()
                elif choice in {"5", "l", "log", "logs"}:
                    self._action_log()
                elif choice in {"6", "c", "clear"}:
                    self._action_clear_exited()
                elif choice in {"r", "refresh", ""}:
                    continue
                elif choice in {"h", "help", "?"}:
                    self._action_help()
                elif choice in {"q", "quit", "exit"}:
                    return EXIT_OK
                else:
                    self._pause(f"Unknown command: {choice!r}")
        except KeyboardInterrupt:
            return EXIT_OK
        finally:
            self._shutdown()

    def _ensure_controller(self) -> None:
        """
        Lazily start the single process that owns device-global state.

        Laziness means opening the manager without creating a screen does not
        mutate the phone at all.
        """
        if self.controller is not None and self.controller.poll() is None:
            return

        command = command_for_device_state_controller(self.scrcpy)
        controller = ObservedProcess(command, label="device-state controller")
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
            process = ObservedProcess(command, label=f"screen {screen_id:02d}")
            process.start()
            process.startup_probe()

            self.screens[screen_id] = ManagedScreen(
                screen_id=screen_id,
                request=request,
                bitrate=bitrate,
                process=process,
            )
            self.next_screen_id += 1

            self._pause(
                f"Screen {screen_id:02d} launched successfully.\n"
                f"{printable_command(command)}"
            )
        except (ConfigurationError, LaunchError) as exc:
            self._pause(f"ADD FAILED\n{exc}")

    def _action_kill(self) -> None:
        screen = self._prompt_screen("Kill screen ID")
        if screen is None:
            return

        graceful = screen.process.request_stop()
        suffix = "" if graceful else "\nForced termination fallback was required."
        self._pause(f"Stop requested for screen {screen.screen_id:02d}.{suffix}")

    def _action_kill_all(self) -> None:
        running = [screen for screen in self.screens.values() if screen.process.poll() is None]
        if not running:
            self._pause("No running managed screens.")
            return

        if not self._prompt_yes_no(f"Stop all {len(running)} running screens?", default=False):
            return

        forced = []
        for screen in running:
            if not screen.process.request_stop():
                forced.append(screen.screen_id)

        message = f"Stop requested for {len(running)} screen(s)."
        if forced:
            joined = ", ".join(f"{value:02d}" for value in forced)
            message += f"\nForced termination was required for: {joined}"
        self._pause(message)

    def _action_defaults(self) -> None:
        try:
            size = self._prompt_size("Default size", self.defaults.size)
            max_fps = self._prompt_fps("Default max FPS", self.defaults.max_fps)
            bitrate = self._prompt_bitrate("Default bitrate", self.defaults.bitrate_spec)
            self.defaults = ScreenDefaults(size=size, max_fps=max_fps, bitrate_spec=bitrate)
            self._pause("New-screen defaults updated.")
        except ConfigurationError as exc:
            self._pause(f"DEFAULT UPDATE FAILED\n{exc}")

    def _action_log(self) -> None:
        screen = self._prompt_screen("Show log for screen ID")
        if screen is None:
            return

        lines = screen.process.tail(80)
        body = "\n".join(lines) if lines else "(no captured output)"
        self._pause(
            f"LOG / SCREEN {screen.screen_id:02d} / {screen.status}\n"
            f"{'-' * 72}\n{body}"
        )

    def _action_clear_exited(self) -> None:
        exited = [
            screen_id
            for screen_id, screen in self.screens.items()
            if screen.process.poll() is not None
        ]
        for screen_id in exited:
            del self.screens[screen_id]
        self._pause(f"Cleared {len(exited)} exited screen record(s).")

    def _action_help(self) -> None:
        controller_text = (
            "Interactive mode uses one hidden control-only scrcpy process to own "
            "--stay-awake, --turn-screen-off and --keep-active. Managed screen "
            "processes receive --no-power-on and do not receive those shared-state flags."
        )
        self._pause(
            "HELP\n"
            "====\n"
            "A / Add       Create another virtual display.\n"
            "K / Kill      Stop one managed display.\n"
            "X / Kill all  Stop all managed display processes.\n"
            "D / Defaults  Change defaults for future displays.\n"
            "L / Log       Inspect captured scrcpy output for one display.\n"
            "C / Clear     Remove exited display records from the table.\n"
            "R / Refresh   Redraw status.\n"
            "Q / Quit      Stop displays, stop controller, exit.\n\n"
            f"{controller_text}\n\n"
            "A bare virtual display is supported by scrcpy, but some Android "
            "devices do not expose a launcher there; such a display may appear "
            "empty until an app is explicitly started."
        )

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

    def _render(self) -> None:
        running = sum(screen.process.poll() is None for screen in self.screens.values())
        controller_status = self._controller_status()

        print("+============================================================================+")
        print("|  SCRCPY VIRTUAL DISPLAY CONTROL / INTERACTIVE MODE                         |")
        print("+============================================================================+")
        print(f"  Managed screens : {len(self.screens)} total / {running} running")
        print(
            "  New-screen defaults : "
            f"size={self.defaults.size}  fps={self.defaults.max_fps}  "
            f"bitrate={self.defaults.bitrate_spec}"
        )
        print(f"  Device controller   : {controller_status}")
        print()
        print("[SCREENS]")
        print()

        if not self.screens:
            print("  (none)")
        else:
            print(" ID  STATUS    PID      AGE      SIZE       FPS  BITRATE      APP")
            print(" --  --------  -------  -------  ---------  ---  -----------  ------------------------------")
            for screen_id in sorted(self.screens):
                screen = self.screens[screen_id]
                pid = screen.process.pid or 0
                age = self._format_age(screen.age_seconds)
                app = screen.request.app or "(bare virtual display)"
                print(
                    f" {screen.screen_id:02d}  "
                    f"{screen.status:<8}  "
                    f"{pid:<7}  "
                    f"{age:<7}  "
                    f"{str(screen.request.size):<9}  "
                    f"{screen.request.max_fps:>3}  "
                    f"{screen.bitrate.display_value:<11}  "
                    f"{app}"
                )

        print()
        print("[CONTROL]")
        print("  [1/A] Add screen")
        print("  [2/K] Kill screen")
        print("  [3/X] Kill all screens")
        print("  [4/D] Edit new-screen defaults")
        print("  [5/L] Show screen log")
        print("  [6/C] Clear exited screen records")
        print("  [R]   Refresh")
        print("  [H]   Help / architecture notes")
        print("  [Q]   Quit manager")

    def _controller_status(self) -> str:
        if self.controller is None:
            return "STANDBY (starts with first screen)"
        code = self.controller.poll()
        if code is None:
            return f"RUNNING pid={self.controller.pid}"
        return f"EXIT {code} (will restart before next Add)"

    def _prompt_screen(self, prompt: str) -> ManagedScreen | None:
        if not self.screens:
            self._pause("No managed screens exist.")
            return None

        text = input(f"{prompt} [blank = cancel]: ").strip()
        if not text:
            return None
        if not text.isdigit():
            self._pause(f"Invalid screen ID: {text!r}")
            return None

        screen = self.screens.get(int(text))
        if screen is None:
            self._pause(f"No screen has ID {text}.")
            return None
        return screen

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

    @staticmethod
    def _pause(message: str) -> None:
        print()
        print(message)
        try:
            input("\nPress Enter to continue...")
        except EOFError:
            pass

    @staticmethod
    def _clear_terminal() -> None:
        if not sys.stdout.isatty():
            return
        os.system("cls" if os.name == "nt" else "clear")


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
