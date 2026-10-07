#!/usr/bin/env python3
"""Patch a clean scrcpy v4.1 checkout for manager-specific per-app audio isolation."""

from __future__ import annotations

import argparse
from pathlib import Path


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(
            f"{label}: expected exactly one upstream match in {path}, found {count}"
        )
    path.write_text(text.replace(old, new), encoding="utf-8")


def patch_audio_playback_capture(root: Path) -> None:
    path = root / "server/src/main/java/com/genymobile/scrcpy/audio/AudioPlaybackCapture.java"

    replace_once(
        path,
        """    private final boolean keepPlayingOnDevice;

    private AudioRecord recorder;
    private AudioRecordReader reader;

    public AudioPlaybackCapture(boolean keepPlayingOnDevice) {
        this.keepPlayingOnDevice = keepPlayingOnDevice;
    }
""",
        """    private final boolean keepPlayingOnDevice;

    private final Object restartLock = new Object();
    private int targetUid = -1;
    private boolean restartRequested;
    private Object currentAudioPolicy;

    private AudioRecord recorder;
    private AudioRecordReader reader;

    public AudioPlaybackCapture(boolean keepPlayingOnDevice) {
        this.keepPlayingOnDevice = keepPlayingOnDevice;
    }

    public void setTargetUid(int uid) {
        synchronized (restartLock) {
            if (targetUid != uid) {
                Ln.i("Audio isolation target UID: " + uid);
                targetUid = uid;
                restartRequested = true;
            }
        }
    }
""",
        "add UID target state",
    )

    replace_once(
        path,
        """            AudioAttributes attributes = new AudioAttributes.Builder().setUsage(AudioAttributes.USAGE_MEDIA).build();

            // audioMixingRuleBuilder.addMixRule(AudioMixingRule.RULE_MATCH_ATTRIBUTE_USAGE, attributes);
            int ruleMatchAttributeUsageConstant = audioMixingRuleClass.getField("RULE_MATCH_ATTRIBUTE_USAGE").getInt(null);
            Method addMixRuleMethod = audioMixingRuleBuilderClass.getMethod("addMixRule", int.class, Object.class);
            addMixRuleMethod.invoke(audioMixingRuleBuilder, ruleMatchAttributeUsageConstant, attributes);
""",
        """            int ruleMatchAttributeUsageConstant = audioMixingRuleClass.getField("RULE_MATCH_ATTRIBUTE_USAGE").getInt(null);
            Method addMixRuleMethod = audioMixingRuleBuilderClass.getMethod("addMixRule", int.class, Object.class);

            if (targetUid >= 0) {
                int ruleMatchUidConstant;
                try {
                    ruleMatchUidConstant = audioMixingRuleClass.getField("RULE_MATCH_UID").getInt(null);
                } catch (ReflectiveOperationException e) {
                    // Android's hidden AudioMixingRule.RULE_MATCH_UID value.
                    ruleMatchUidConstant = 4;
                }
                addMixRuleMethod.invoke(audioMixingRuleBuilder, ruleMatchUidConstant, Integer.valueOf(targetUid));
            }

            // Games commonly use USAGE_GAME instead of USAGE_MEDIA. Cover every
            // accepted usage and let the UID criterion provide the isolation.
            for (int usage = 0; usage <= 16; ++usage) {
                try {
                    AudioAttributes attributes = new AudioAttributes.Builder().setUsage(usage).build();
                    addMixRuleMethod.invoke(audioMixingRuleBuilder, ruleMatchAttributeUsageConstant, attributes);
                } catch (ReflectiveOperationException | IllegalArgumentException e) {
                    // Some Android releases reject individual usage constants.
                }
            }
""",
        "add UID + all-usage AudioMixingRule",
    )

    replace_once(
        path,
        """            if (result != 0) {
                throw new RuntimeException("registerAudioPolicy() returned " + result);
            }

            // audioPolicy.createAudioRecordSink(audioPolicy);
""",
        """            if (result != 0) {
                throw new RuntimeException("registerAudioPolicy() returned " + result);
            }
            currentAudioPolicy = audioPolicy;

            // audioPolicy.createAudioRecordSink(audioPolicy);
""",
        "retain registered AudioPolicy",
    )

    replace_once(
        path,
        """    @Override
    public void start() throws AudioCaptureException {
        recorder = createAudioRecord();
        recorder.startRecording();
        reader = new AudioRecordReader(recorder);
    }

    @Override
    public void stop() {
        if (recorder != null) {
            // Will call .stop() if necessary, without throwing an IllegalStateException
            recorder.release();
        }
    }

    @Override
    @TargetApi(AndroidVersions.API_24_ANDROID_7_0)
    public int read(ByteBuffer outDirectBuffer, MediaCodec.BufferInfo outBufferInfo) {
        return reader.read(outDirectBuffer, outBufferInfo);
    }
""",
        """    private void unregisterAudioPolicy() {
        if (currentAudioPolicy == null) {
            return;
        }

        try {
            Class<?> audioPolicyClass = Class.forName("android.media.audiopolicy.AudioPolicy");
            Method unregisterMethod = AudioManager.class.getDeclaredMethod(
                    "unregisterAudioPolicyAsyncStatic", audioPolicyClass);
            unregisterMethod.setAccessible(true);
            unregisterMethod.invoke(null, currentAudioPolicy);
        } catch (Exception e) {
            Ln.w("Could not unregister audio policy", e);
        } finally {
            currentAudioPolicy = null;
        }
    }

    private void restartRecorderLocked() throws AudioCaptureException {
        if (recorder != null) {
            recorder.release();
            recorder = null;
            reader = null;
        }
        unregisterAudioPolicy();
        recorder = createAudioRecord();
        recorder.startRecording();
        reader = new AudioRecordReader(recorder);
        restartRequested = false;
    }

    @Override
    public void start() throws AudioCaptureException {
        synchronized (restartLock) {
            restartRecorderLocked();
        }
    }

    @Override
    public void stop() {
        synchronized (restartLock) {
            if (recorder != null) {
                // Will call .stop() if necessary, without throwing an IllegalStateException
                recorder.release();
                recorder = null;
                reader = null;
            }
            unregisterAudioPolicy();
            restartRequested = false;
        }
    }

    @Override
    @TargetApi(AndroidVersions.API_24_ANDROID_7_0)
    public int read(ByteBuffer outDirectBuffer, MediaCodec.BufferInfo outBufferInfo) {
        AudioRecordReader activeReader;
        synchronized (restartLock) {
            if (restartRequested) {
                try {
                    restartRecorderLocked();
                } catch (AudioCaptureException e) {
                    Ln.e("Could not retarget isolated audio capture", e);
                    return -1;
                }
            }
            activeReader = reader;
        }
        return activeReader != null ? activeReader.read(outDirectBuffer, outBufferInfo) : -1;
    }
""",
        "restart playback capture when UID changes",
    )


def patch_controller(root: Path) -> None:
    path = root / "server/src/main/java/com/genymobile/scrcpy/control/Controller.java"

    replace_once(
        path,
        """import com.genymobile.scrcpy.CleanUp;
import com.genymobile.scrcpy.Options;
""",
        """import com.genymobile.scrcpy.CleanUp;
import com.genymobile.scrcpy.FakeContext;
import com.genymobile.scrcpy.Options;
import com.genymobile.scrcpy.audio.AudioPlaybackCapture;
""",
        "controller audio imports",
    )

    replace_once(
        path,
        """import android.content.Intent;
import android.net.Uri;
""",
        """import android.content.Intent;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageManager;
import android.net.Uri;
""",
        "controller package imports",
    )

    replace_once(
        path,
        """    // Used for resetting video encoding on RESET_VIDEO message or for sending camera controls
    private SurfaceCapture surfaceCapture;
""",
        """    // Used for resetting video encoding on RESET_VIDEO message or for sending camera controls
    private SurfaceCapture surfaceCapture;

    // Manager-specific v4.1 patch: populated only for playback audio on a new display.
    private AudioPlaybackCapture audioPlaybackCapture;
""",
        "controller audio capture field",
    )

    replace_once(
        path,
        """    public void setSurfaceCapture(SurfaceCapture surfaceCapture) {
        this.surfaceCapture = surfaceCapture;
    }
""",
        """    public void setSurfaceCapture(SurfaceCapture surfaceCapture) {
        this.surfaceCapture = surfaceCapture;
    }

    public void setAudioPlaybackCapture(AudioPlaybackCapture audioPlaybackCapture) {
        this.audioPlaybackCapture = audioPlaybackCapture;
    }
""",
        "controller audio capture setter",
    )

    replace_once(
        path,
        """        int startAppDisplayId = getStartAppDisplayId();
""",
        """        if (audioPlaybackCapture != null) {
            try {
                PackageManager packageManager = FakeContext.get().getPackageManager();
                ApplicationInfo applicationInfo = packageManager.getApplicationInfo(app.getPackageName(), 0);
                Ln.i("Audio isolation package: " + app.getPackageName() + " (uid=" + applicationInfo.uid + ")");
                audioPlaybackCapture.setTargetUid(applicationInfo.uid);
            } catch (PackageManager.NameNotFoundException e) {
                Ln.w("Could not resolve UID for audio isolation: " + app.getPackageName());
            }
        }

        int startAppDisplayId = getStartAppDisplayId();
""",
        "retarget audio before starting app",
    )


def patch_server(root: Path) -> None:
    path = root / "server/src/main/java/com/genymobile/scrcpy/Server.java"

    replace_once(
        path,
        """                if (audioSource.isDirect()) {
                    audioCapture = new AudioDirectCapture(audioSource);
                } else {
                    audioCapture = new AudioPlaybackCapture(options.getAudioDup());
                }

                Streamer audioStreamer""",
        """                if (audioSource.isDirect()) {
                    audioCapture = new AudioDirectCapture(audioSource);
                } else {
                    AudioPlaybackCapture playbackCapture = new AudioPlaybackCapture(options.getAudioDup());
                    audioCapture = playbackCapture;
                    if (controller != null && options.getNewDisplay() != null) {
                        controller.setAudioPlaybackCapture(playbackCapture);
                    }
                }

                Streamer audioStreamer""",
        "connect playback capture to virtual-display controller",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    args = parser.parse_args()

    root = args.source.resolve()
    build_gradle = root / "server/build.gradle"
    if not build_gradle.is_file() or 'versionName "4.1"' not in build_gradle.read_text(encoding="utf-8"):
        raise RuntimeError(f"{root} is not a clean scrcpy v4.1 source tree")

    patch_audio_playback_capture(root)
    patch_controller(root)
    patch_server(root)
    print("Patched scrcpy v4.1 server for package/UID audio isolation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
