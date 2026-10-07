# scrcpy virtual-screen manager notes

## Audio isolation experiment (2026-10-03)

The manager lives under tools/scrcpy_virtual_screen_manager/.

Stock scrcpy 4.1 default audio source is output/REMOTE_SUBMIX, which is whole
device audio. Multiple scrcpy clients therefore each receive the same mix.
Playback capture is Android 13+ and supports AudioMix UID matching, but stock
scrcpy 4.1 does not expose per-virtual-display app isolation.

The local experiment keeps the stock 4.1 Windows client and patches only the
matching server. It hooks Controller START_APP, resolves the package UID through
FakeContext.get().getPackageManager(), and retargets AudioPlaybackCapture using
AudioMixingRule.RULE_MATCH_UID. This is deliberately narrower than upstream
Genymobile/scrcpy PR #6561, which polls the foreground app on each virtual
display and dynamically switches UIDs.

The manager auto-detects scrcpy_server/out/scrcpy-server-v4.1-audio-isolated.
For app-backed sessions only, it sets SCRCPY_SERVER_PATH and
--audio-source=playback. It also sets per-process SDL_APP_NAME to improve SDL3
Windows mixer labels.

Known limitations: Android 13+, app playback-capture opt-out, shared UIDs,
hidden AudioPolicy API/vendor compatibility, and a possible brief global-audio
window before START_APP retargeting.
