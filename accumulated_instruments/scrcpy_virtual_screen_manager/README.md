# scrcpy virtual screen manager

This directory contains the multi-screen scrcpy manager and its optional patched
scrcpy 4.1 server experiment.

## Run

From the repository root on Windows:

    python .\accumulated_instruments\scrcpy_virtual_screen_manager\scrcpy_virtual_screen_manager.py

The ordinary manager still works with the stock scrcpy server. If the optional
audio-isolation server has been built, app-backed managed screens automatically
use it while the hidden device-state controller remains ordinary scrcpy.

## Experimental per-app audio isolation

Stock scrcpy 4.1 captures the whole Android output by default. Its alternative
playback capture can be filtered by Android UID, but stock scrcpy does not expose
per-virtual-display UID selection.

This experiment keeps the stock Windows scrcpy 4.1 client and patches only the
matching Android server. It is inspired by upstream scrcpy PR #6561, but is
intentionally narrower for this manager:

- each managed virtual display already launches one known package;
- the normal START_APP control message therefore identifies the package;
- the patched Controller resolves that package's Android UID;
- AudioPlaybackCapture rebuilds its AudioMix with RULE_MATCH_UID;
- no foreground-app polling thread and no custom C client are required.

Build it with:

    .\accumulated_instruments\scrcpy_virtual_screen_manager\scrcpy_server\build.ps1

The build helper clones the official scrcpy v4.1 tag into an ignored local
directory, applies patch_v4_1.py, builds only the Android server, and writes:

    scrcpy_server\out\scrcpy-server-v4.1-audio-isolated

The Python manager auto-detects that artifact. To use another copy explicitly,
set SCRCPY_AUDIO_ISOLATION_SERVER to its path.

### Limitations

This is deliberately experimental.

- Playback capture requires Android 13 or newer.
- Android applications may opt out of playback capture; those apps can become
  silent instead of isolated.
- Packages sharing one Android UID cannot be separated from each other by UID.
- There may be a brief whole-device-audio interval before the START_APP control
  message arrives and the server retargets capture.
- The server is version-locked to the stock scrcpy 4.1 client.
- The patch uses Android hidden AudioPolicy APIs and may fail on vendor ROMs.

When isolation is active, app sessions receive --audio-source=playback and
SCRCPY_SERVER_PATH only for that child process. The manager also sets a unique
SDL_APP_NAME for every scrcpy child so SDL3/Windows volume controls have a chance
to display the same useful per-screen label as the window title.

Upstream references:

- Genymobile/scrcpy issue #5802: per-app audio for virtual displays
- Genymobile/scrcpy PR #6561: audio isolation for virtual displays
- scrcpy v4.1 doc/audio.md: output vs playback capture semantics
