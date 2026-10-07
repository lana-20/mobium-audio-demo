# Tutorial: audio, from a test to your own app

The [quick start](QUICKSTART.md) heard MobiumApp's Audio Demo from the command
line. This takes it further: from Python, what a capture's answer holds,
what the volume does to it, an alarm cutting across the app, writing audio
tests for your own app, running them in CI, and proving it all on your own
devices.

Every command and output below was run on 7 October 2026 on a Pixel 7
emulator (Android 15), with Mobium installed by `go install …@latest` and the
Python client by `pip` from GitHub, as the quick start sets them up. Paths
in the outputs are shortened to `~`.

## Contents

- [1. From Python](#1-from-python)
- [2. What the answer holds](#2-what-the-answer-holds)
- [3. The volume](#3-the-volume)
- [4. An alarm](#4-an-alarm)
- [5. Your own app](#5-your-own-app)
- [6. In CI](#6-in-ci)
- [7. Proving it on your devices](#7-proving-it-on-your-devices)

## 1. From Python

The Python client isn't on PyPI yet; pip installs it straight from GitHub:

```sh
python3 -m venv .venv
.venv/bin/pip install "mobium @ git+https://github.com/mobiumdev/mobium.git#subdirectory=clients/python"
MOBIUM_DEVICE=emulator-5554 .venv/bin/python examples/hear.py
```

[`examples/hear.py`](../examples/hear.py) opens the Audio Demo, captures the
sequence, asserts it at the stop, prints the timeline, then expects what was
not played:

```
   0.0– 0.7s  silence
   0.7– 0.8s  sound
   0.8– 2.9s  440 Hz at -42 dBFS
   2.9– 3.8s  silence
   3.8– 5.9s  880 Hz at -42 dBFS
   5.9– 6.9s  silence
heard as expected, at media volume 5 of 15
a wrong expectation: expected 880 Hz; heard 440 Hz for 2.1s (0.3–2.4s) — at media volume 5 of 15 — the capture is saved at ~/mobium-audio-demo/wrong.wav
```

The assertion is one argument:

```python
device.audio("stop", "sequence.wav", expect=[
    {"hz": 440, "min_ms": 1800, "max_ms": 2300},
    {"hz": 880, "min_ms": 1800, "max_ms": 2300},
])
```

A wrong one raises `NotConfirmedError`, saying what was heard; the capture is
saved either way. On an Android phone the stop raises `UnsupportedError`
for an `expect`, since a phone's sound is not captured.

**Wait for this sound's own line.** The script waits for the Audio Demo to
say `finished: 440 Hz for 2 s` — not just `finished:`, which the last sound
left on the screen, so a wait for it is met at once and the capture stops
mid-tone. Its first draft did that, and heard 0.4 s of a 2 s tone.

## 2. What the answer holds

`--json` gives the stop's answer whole. A capture of the tone with an
incoming call over it, shortened where the timeline repeats:

```sh
mobium audio start --app dev.mobium.mobiumapp
mobium tap testid=audioLoop
mobium call ring
mobium call hang
mobium tap testid=audioStop
mobium --json audio stop -o call.wav
```

```json
{
  "app": "dev.mobium.mobiumapp",
  "bytes": 1017956,
  "device": "emulator-5554",
  "duration": 10603000000,
  "interruptions": [
    {"from": 2963899653, "kind": "muted", "reason": "call", "to": 7886899653},
    {"from": 3192899653, "kind": "ringtone", "to": 7905899653, "usage": "USAGE_NOTIFICATION_RINGTONE"}
  ],
  "path": "~/mobium-audio-demo/call.wav",
  "timeline": [
    {"from": 0, "sound": false, "to": 700000000},
    {"from": 700000000, "hz": 781, "level": -47.3, "sound": true, "to": 800000000},
    {"from": 800000000, "hz": 440, "level": -41.8, "sound": true, "to": 3100000000},
    {"from": 3100000000, "sound": false, "to": 3300000000},
    {"from": 3300000000, "hz": 1047, "level": -26.3, "sound": true, "to": 3400000000},
    …
    {"from": 8000000000, "hz": 440, "level": -41.6, "sound": true, "to": 10600000000}
  ],
  "volumes": [
    {"index": 5, "max": 15, "min": 0, "stream": "media"},
    {"index": 6, "max": 7, "min": 1, "stream": "alarm"}
  ]
}
```

Times are nanoseconds since the capture started.

- **`timeline`** is what was heard, in tenths of a second: `sound` or not,
  and for a sound its `level` in dBFS (0 is full scale) and its `hz` when
  one frequency holds most of it. The 781 Hz tenth at 0.7 s is the tap's
  click; the 1047 Hz and the pitches after it are the ringtone.
- **`interruptions`** is what Android's audio service says cut across `app`:
  here the app muted for the call, and a ringtone. `kind` is `muted` — with
  a `reason`: `call`, `streamVolume` (the device's volume at its lowest),
  `clientVolume` (the player's own) — or what another app's player was for:
  `ringtone`, `alarm`, `notification`, `voice_call`, `assistant`,
  `navigation`, `media`. `open` marks one still going at the stop.
- **`volumes`** are the media and alarm volumes at the stop, each on the
  device's own scale (`volumesAtStart` too, when they changed).

## 3. The volume

What arrives follows the media volume. At its lowest a playing app is
silence — and the answer says so:

```sh
adb shell cmd audio set-volume 3 0
mobium audio start
mobium tap testid=audioTone
mobium audio stop -o quiet.wav
adb shell cmd audio set-volume 3 5
```

```
saved ~/mobium-audio-demo/quiet.wav: 3.769s of audio: 0.0–0.6s silence, 0.6–0.7s sound, no one pitch (-47 dBFS), 0.7–3.8s silence — at media volume 0 of 15, muted, where nothing played as media is heard; interrupted: muted, the device's volume at its lowest 0.6–2.6s
```

The click is still heard: it plays on the system's stream, not media.
Android also logs the app's player muted by the volume for as long as it
played, which is the `interrupted` part. The demo's act 4 heard the same
tone at -9 dBFS at volume 15, -42 at 5, -63 at 1 and nothing at 0; so a
test asserts pitch and length, and a silent result that says *volume 0* is
a test environment to fix, not an app to blame.

`adb shell cmd media_session volume --set` also exists. It exits 0 and
changes nothing; `cmd audio set-volume` is the one that sets it.

## 4. An alarm

Another app's sound over the app is an interruption too. The Clock app's
timer, set from adb for four seconds, rings with the system's alarm sound
while the tone plays; on an emulator Clock is then stopped outright, since
nobody's alarms are there:

```sh
mobium audio start --app dev.mobium.mobiumapp
mobium tap testid=audioLoop
adb shell am start -a android.intent.action.SET_TIMER --ei android.intent.extra.alarm.LENGTH 4 --ez android.intent.extra.alarm.SKIP_UI true
adb shell am force-stop com.google.android.deskclock
mobium tap testid=audioStop
mobium audio stop -o alarm.wav
```

```
saved ~/mobium-audio-demo/alarm.wav: 8.327s of audio: 0.0–0.7s silence, 0.7–0.8s sound, no one pitch (-47 dBFS), 0.8–4.9s 440 Hz (-42 dBFS), 4.9–5.1s 528 Hz (-19 dBFS), 5.1–5.2s sound, no one pitch (-22 dBFS), 5.2–5.3s 593 Hz (-18 dBFS), 5.3–5.7s sound, no one pitch (-17 dBFS), 5.7–5.8s 259 Hz (-17 dBFS), 5.8–5.9s sound, no one pitch (-19 dBFS), 5.9–6.0s 331 Hz (-18 dBFS), 6.0–6.3s 390 Hz (-20 dBFS), 6.3–6.4s sound, no one pitch (-20 dBFS), 6.4–6.8s 521 Hz (-18 dBFS), 6.8–6.9s sound, no one pitch (-18 dBFS), 6.9–7.0s 587 Hz (-25 dBFS), 7.0–7.3s sound, no one pitch (-20 dBFS), 7.3–8.3s 440 Hz (-42 dBFS) — at media volume 5 of 15; interrupted: an alarm played 4.9–7.2s
```

Unlike the call, the alarm did not silence the app: the Audio Demo asks for
no audio focus, so Android left its tone playing under the alarm, which the
capture heard as the alarm's louder melody, 17 to 25 dB above the tone.
`interrupted` names the alarm by what its player said it was for. On a real
phone, stop the timer from Clock's own Stop rather than force-stopping
Clock, which would cancel the phone owner's alarms; the
[quick start](QUICKSTART.md#on-an-android-phone) shows the same alarm on a
Pixel.

This was recorded with Mobium `v0.0.0-20261007121812-439e89a6d02c`, the
commit after the rest of this page, which reads a tap's click as a sound
with no pitch where it once came out as "12 Hz".

## 5. Your own app

Nothing is added to an app to hear it: an emulator's audio comes from the
emulator, whatever the app is written in. What helps is knowing what to
assert.

- **Pitch and length, in order.** A beep, a chime, a tone: `--expect
  880:0.1-0.3`. A sound of 200 ms or less does not count by default, so a
  short beep needs `--ignore-ms` lowered under it: `--expect 880:0.1-0.3
  --ignore-ms 50`. `0` is a sound with no one pitch — noise, a click, much
  of speech — and matches only that: a recording that is partly tonal reads
  as several sounds, so assert a spoken prompt by when sound starts and
  stops rather than by one `0`.
- **Silence is an assertion too.** `--expect silence` after muting, after
  pausing, after a call ends: nothing longer than 200 ms.
- **Clicks and the system's sounds.** With touch sounds on, every tap is a
  tenth of a second of sound; `ignore_ms` (default 200) is how short a
  sound may be and not count. Turn touch sounds off on a test emulator if
  you would rather they were not there:
  `adb shell settings put system sound_effects_enabled 0`.
- **Name the app.** `audio start --app <package>` reads the interruptions
  for that app; without it, the app in front at the start.
- **Wait for the app's own word.** Stop a capture after the app says its
  sound is over, by a line only that sound leaves — see section 1.

## 6. In CI

An Android emulator in CI hears exactly as one on your desk:

```sh
mobium boot <avd>          # headless; the emulator's -no-audio silences the machine, not the capture
mobium test tests/          # audio steps and their expects run as any other step
```

The capture needs no sound device on the CI machine and nothing installed
on the emulator: it reads the emulator's own audio over its control port,
opened for that machine only, with a token. An incoming call is
`mobium call ring` / `mobium call hang`; an alarm, the Clock app's timer
from adb, as in section 4.

On real phones in a device farm the sound is not captured, but what
interrupted the app is — the same `interruptions`, from the same audio
service, with nothing installed on the phone. Making a phone ring takes a
call from outside it, which only a farm with a line can place.

## 7. Proving it on your devices

[`scripts/demo.sh`](../scripts/demo.sh) runs five acts on a device and keeps
the evidence of each — the WAVs, each stop's answer as JSON, a drawing of
each timeline, the test reports, and a transcript of every command:

```sh
scripts/demo.sh emulator-5554
ALLOW_PHONE=1 scripts/demo.sh <phone-serial>
python3 scripts/summarize.py
```

On a phone only the alarm runs, and only with `ALLOW_PHONE=1`: it sets a
4-second timer in the phone's Clock and stops it with the timer's own Stop,
which removes it — never by force-stopping Clock, which would cancel the
phone owner's alarms. [`evidence/README.md`](../evidence/README.md) has every
run's results, generated from the runs.
