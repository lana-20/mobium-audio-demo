# Audio on android-emulator

Recorded 2026-10-07 04:33 PDT with `mobium version 0.1.0-dev`, on android-emulator.

## Act 1 — silence that says it is playing

The Audio Demo's silence is a player that is started and plays two seconds of zeros. The app says it is playing; Android's audio service reports a player started, exactly as for a tone. Only the capture says what was heard.

```
$ mobium launch dev.mobium.mobiumapp
launched dev.mobium.mobiumapp
```

```
$ mobium tap "label=Audio Demo"
tapped label=Audio Demo at (540, 2267)
```

```
$ mobium audio start
capturing audio — stop it with action "stop" and a path
```

```
$ mobium tap testid=audioSilent
tapped testid=audioSilent at (540, 1258)
```

```
$ mobium text testid=audioState
playing: silence for 2 s (media)
```

```
$ adb shell dumpsys audio   # MobiumApp's player
state:started
```

```
$ mobium audio stop -o act1-silence.wav
saved evidence/2026-10-07-android-emulator/act1-silence.wav: 3.487s of audio: 0.0–0.3s silence, 0.3–0.4s sound, no one pitch (-47 dBFS), 0.4–3.5s silence — at media volume 5 of 15
```

The app said **playing: silence for 2 s (media)**; the platform said **state:started**; the capture: **saved evidence/2026-10-07-android-emulator/act1-silence.wav: 3.487s of audio: 0.0–0.3s silence, 0.3–0.4s sound, no one pitch (-47 dBFS), 0.4–3.5s silence — at media volume 5 of 15**.

## Act 2 — hear it

A tone, then 440 Hz, a second of silence and 880 Hz. The answer is a timeline: sound and silence to a tenth of a second, each sound's pitch and level.

```
$ mobium audio start
capturing audio — stop it with action "stop" and a path
```

```
$ mobium tap testid=audioTone
tapped testid=audioTone at (540, 788)
```

```
$ mobium audio stop -o act2-tone.wav
saved evidence/2026-10-07-android-emulator/act2-tone.wav: 3.452s of audio: 0.0–0.3s silence, 0.3–2.4s 440 Hz (-42 dBFS), 2.4–3.5s silence — at media volume 5 of 15
```

```
$ mobium audio start
capturing audio — stop it with action "stop" and a path
```

```
$ mobium tap testid=audioSequence
tapped testid=audioSequence at (540, 944)
```

```
$ mobium audio stop -o act2-sequence.wav
saved evidence/2026-10-07-android-emulator/act2-sequence.wav: 6.443s of audio: 0.0–0.3s silence, 0.3–2.4s 440 Hz (-42 dBFS), 2.4–3.3s silence, 3.3–5.4s 880 Hz (-42 dBFS), 5.4–6.4s silence — at media volume 5 of 15
```

## Act 3 — as a test

tests/heard.test.json asserts at each stop what was played; tests/wrong.test.json expects what was not, and must fail, saying what was heard.

```
$ mobium test --config evidence/2026-10-07-android-emulator/mobium.config.json tests/heard.test.json --reporter list,html --output evidence/2026-10-07-android-emulator/report-heard
waiting for the UiAutomator2 server to start...
  ok    [android-emulator · emulator-5554] heard.test.json › the sequence is heard in order (9.4s)
  ok    [android-emulator · emulator-5554] heard.test.json › silence is heard as silence (7.1s)
2 passed (16.4s)
html report: evidence/2026-10-07-android-emulator/report-heard/index.html
```

```
$ mobium test --config evidence/2026-10-07-android-emulator/mobium.config.json tests/wrong.test.json --reporter list,html --output evidence/2026-10-07-android-emulator/report-wrong
waiting for the UiAutomator2 server to start...
  FAIL  [android-emulator · emulator-5554] wrong.test.json › 880 Hz expected, 440 Hz played (7.7s)
        step 4 (app_audio): [not_confirmed] step 4 of 4 (app_audio) failed: expected 880 Hz; heard 440 Hz for 2.1s (0.3–2.4s) — at media volume 5 of 15 — the capture is saved at mobium-report/wrong-pitch.wav; steps 1-3 ran before it, and nothing after
  FAIL  [android-emulator · emulator-5554] wrong.test.json › silence expected, a tone played (6.9s)
        step 4 (app_audio): [not_confirmed] step 4 of 4 (app_audio) failed: expected silence; heard 440 Hz for 2.1s (0.3–2.4s) — at media volume 5 of 15 — the capture is saved at mobium-report/wrong-silence.wav; steps 1-3 ran before it, and nothing after
0 passed, 2 failed (14.5s)
html report: evidence/2026-10-07-android-emulator/report-wrong/index.html
error: 2 of 2 tests failed
```

Heard: **2 passed (16.4s)**. Wrong: **0 passed, 2 failed (14.5s)**.

## Act 4 — the volume

The same tone at media volume 15, 5, 1 and 0. What arrives follows the volume; at 0 a playing app is silence, and the answer says the volume it was taken at. The volume is put back as it was found.

```
$ mobium launch dev.mobium.mobiumapp
launched dev.mobium.mobiumapp
```

```
$ mobium tap "label=Audio Demo"
tapped label=Audio Demo at (540, 2269)
```

Media volume set to 15.

```
$ mobium audio start
capturing audio — stop it with action "stop" and a path
```

```
$ mobium tap testid=audioTone
tapped testid=audioTone at (540, 788)
```

```
$ mobium audio stop -o act4-volume-15.wav
saved evidence/2026-10-07-android-emulator/act4-volume-15.wav: 3.485s of audio: 0.0–0.3s silence, 0.3–0.4s sound, no one pitch (-26 dBFS), 0.4–2.4s 440 Hz (-9 dBFS), 2.4–3.5s silence — at media volume 15 of 15
```

Media volume set to 5.

```
$ mobium audio start
capturing audio — stop it with action "stop" and a path
```

```
$ mobium tap testid=audioTone
tapped testid=audioTone at (540, 788)
```

```
$ mobium audio stop -o act4-volume-5.wav
saved evidence/2026-10-07-android-emulator/act4-volume-5.wav: 3.452s of audio: 0.0–0.3s silence, 0.3–2.4s 440 Hz (-42 dBFS), 2.4–3.5s silence — at media volume 5 of 15
```

Media volume set to 1.

```
$ mobium audio start
capturing audio — stop it with action "stop" and a path
```

```
$ mobium tap testid=audioTone
tapped testid=audioTone at (540, 788)
```

```
$ mobium audio stop -o act4-volume-1.wav
saved evidence/2026-10-07-android-emulator/act4-volume-1.wav: 3.459s of audio: 0.0–0.3s silence, 0.3–0.4s sound, no one pitch (-47 dBFS), 0.4–2.4s 440 Hz (-62 dBFS), 2.4–3.5s silence — at media volume 1 of 15
```

Media volume set to 0.

```
$ mobium audio start
capturing audio — stop it with action "stop" and a path
```

```
$ mobium tap testid=audioTone
tapped testid=audioTone at (540, 788)
```

```
$ mobium audio stop -o act4-volume-0.wav
saved evidence/2026-10-07-android-emulator/act4-volume-0.wav: 3.435s of audio: 0.0–0.3s silence, 0.3–0.4s sound, no one pitch (-47 dBFS), 0.4–3.4s silence — at media volume 0 of 15, muted, where nothing played as media is heard; interrupted: muted, the device's volume at its lowest 0.3–2.3s
```

Put back to 5. By volume: **15: 440 Hz at -9.1 dBFS; 5: 440 Hz at -41.8 dBFS; 1: 440 Hz at -62.5 dBFS; 0: silence; **

## Act 5 — interrupted: a call

The tone plays until stopped; the emulator rings, and is hung up five seconds later.

```
$ mobium launch dev.mobium.mobiumapp
launched dev.mobium.mobiumapp
```

```
$ mobium tap "label=Audio Demo"
tapped label=Audio Demo at (540, 2267)
```

```
$ mobium audio start --app dev.mobium.mobiumapp
capturing audio — stop it with action "stop" and a path
```

```
$ mobium tap testid=audioLoop
tapped testid=audioLoop at (540, 1101)
```

```
$ mobium call ring
ringing a call from 5551234
```

```
$ mobium call hang
ended a call from 5551234
```

```
$ mobium tap testid=audioStop
tapped testid=audioStop at (540, 1571)
```

```
$ mobium audio stop -o act5-call.wav
saved evidence/2026-10-07-android-emulator/act5-call.wav: 10.794s of audio: 0.0–0.3s silence, 0.3–0.4s sound, no one pitch (-47 dBFS), 0.4–2.7s 440 Hz (-42 dBFS), 2.7–2.8s silence, 2.8–2.9s 1047 Hz (-36 dBFS), 2.9–3.0s 1241 Hz (-22 dBFS), 3.0–3.2s 1051 Hz (-24 dBFS), 3.2–3.3s sound, no one pitch (-23 dBFS), 3.3–3.5s 1055 Hz (-25 dBFS), 3.5–3.8s 1240 Hz (-23 dBFS), 3.8–4.6s 1051 Hz (-31 dBFS), 4.6–6.7s silence, 6.7–7.0s 1055 Hz (-24 dBFS), 7.0–7.5s 1241 Hz (-23 dBFS), 7.5–7.6s 1043 Hz (-28 dBFS), 7.6–10.2s 440 Hz (-42 dBFS), 10.2–10.3s sound, no one pitch (-43 dBFS), 10.3–10.8s silence — at media volume 5 of 15; interrupted: muted for a call 2.5–7.4s, a ringtone played 2.7–7.5s
```

## Act 5 — interrupted: an alarm

A 4-second Clock timer rings over the tone, and is stopped by its own Stop.

```
$ mobium launch dev.mobium.mobiumapp
launched dev.mobium.mobiumapp
```

```
$ mobium tap "label=Audio Demo"
tapped label=Audio Demo at (540, 2267)
```

```
$ mobium audio start --app dev.mobium.mobiumapp
capturing audio — stop it with action "stop" and a path
```

```
$ mobium tap testid=audioLoop
tapped testid=audioLoop at (540, 1101)
```

A 4-second timer set in Clock.

Clock stopped.

```
$ mobium tap testid=audioStop
tapped testid=audioStop at (540, 1571)
```

```
$ mobium audio stop -o act5-alarm.wav
saved evidence/2026-10-07-android-emulator/act5-alarm.wav: 7.924s of audio: 0.0–0.3s silence, 0.3–0.4s sound, no one pitch (-47 dBFS), 0.4–4.5s 440 Hz (-42 dBFS), 4.5–4.7s 527 Hz (-19 dBFS), 4.7–4.8s sound, no one pitch (-22 dBFS), 4.8–4.9s 592 Hz (-17 dBFS), 4.9–5.0s sound, no one pitch (-19 dBFS), 5.0–5.1s 528 Hz (-16 dBFS), 5.1–5.2s 788 Hz (-15 dBFS), 5.2–5.3s sound, no one pitch (-19 dBFS), 5.3–5.4s 259 Hz (-17 dBFS), 5.4–5.5s 298 Hz (-19 dBFS), 5.5–5.6s 330 Hz (-18 dBFS), 5.6–5.7s 391 Hz (-19 dBFS), 5.7–5.8s sound, no one pitch (-22 dBFS), 5.8–5.9s 391 Hz (-19 dBFS), 5.9–6.0s 439 Hz (-20 dBFS), 6.0–6.1s 522 Hz (-19 dBFS), 6.1–6.2s sound, no one pitch (-15 dBFS), 6.2–6.3s 523 Hz (-19 dBFS), 6.3–6.4s sound, no one pitch (-21 dBFS), 6.4–6.7s 591 Hz (-20 dBFS), 6.7–6.8s 790 Hz (-18 dBFS), 6.8–7.9s 440 Hz (-40 dBFS) — at media volume 5 of 15; interrupted: an alarm played 4.4–6.7s
```

