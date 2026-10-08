# Audio on android-emulator

Recorded 2026-10-07 19:13 PDT with `mobium version v0.0.0-20261008020356-5b57d8f0eb84`, on android-emulator.

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
saved evidence/2026-10-07-android-emulator/act1-silence.wav: 3.512s of audio: 0.0–0.3s silence, 0.3–0.4s sound, no one pitch (-47 dBFS), 0.4–3.5s silence — at media volume 5 of 15
```

The app said **playing: silence for 2 s (media)**; the platform said **state:started**; the capture: **saved evidence/2026-10-07-android-emulator/act1-silence.wav: 3.512s of audio: 0.0–0.3s silence, 0.3–0.4s sound, no one pitch (-47 dBFS), 0.4–3.5s silence — at media volume 5 of 15**.

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
saved evidence/2026-10-07-android-emulator/act2-tone.wav: 3.462s of audio: 0.0–0.3s silence, 0.3–2.4s 440 Hz (-42 dBFS), 2.4–3.5s silence — at media volume 5 of 15
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
saved evidence/2026-10-07-android-emulator/act2-sequence.wav: 6.485s of audio: 0.0–0.3s silence, 0.3–2.4s 440 Hz (-42 dBFS), 2.4–3.3s silence, 3.3–5.4s 880 Hz (-42 dBFS), 5.4–6.5s silence — at media volume 5 of 15
```

## Act 3 — as a test

tests/heard.test.json asserts at each stop what was played; tests/wrong.test.json expects what was not, and must fail, saying what was heard.

```
$ mobium test --config evidence/2026-10-07-android-emulator/mobium.config.json tests/heard.test.json --reporter list,html --output evidence/2026-10-07-android-emulator/report-heard
waiting for the UiAutomator2 server to start...
  ok    [android-emulator · emulator-5554] heard.test.json › the sequence is heard in order (10.5s)
  ok    [android-emulator · emulator-5554] heard.test.json › silence is heard as silence (6.8s)
2 passed (17.3s)
html report: evidence/2026-10-07-android-emulator/report-heard/index.html
```

```
$ mobium test --config evidence/2026-10-07-android-emulator/mobium.config.json tests/wrong.test.json --reporter list,html --output evidence/2026-10-07-android-emulator/report-wrong
waiting for the UiAutomator2 server to start...
  FAIL  [android-emulator · emulator-5554] wrong.test.json › 880 Hz expected, 440 Hz played (7.5s)
        step 4 (app_audio): [not_confirmed] step 4 of 4 (app_audio) failed: expected 880 Hz; heard 440 Hz for 2.1s (0.3–2.4s) — at media volume 5 of 15 — the capture is saved at mobium-report/wrong-pitch.wav; steps 1-3 ran before it, and nothing after
  FAIL  [android-emulator · emulator-5554] wrong.test.json › silence expected, a tone played (7s)
        step 4 (app_audio): [not_confirmed] step 4 of 4 (app_audio) failed: expected silence; heard 440 Hz for 2.0s (0.4–2.4s) — at media volume 5 of 15 — the capture is saved at mobium-report/wrong-silence.wav; steps 1-3 ran before it, and nothing after
0 passed, 2 failed (14.5s)
html report: evidence/2026-10-07-android-emulator/report-wrong/index.html
error: 2 of 2 tests failed
```

Heard: **2 passed (17.3s)**. Wrong: **0 passed, 2 failed (14.5s)**.

## Act 4 — the volume

The same tone at media volume 15, 5, 1 and 0. What arrives follows the volume; at 0 a playing app is silence, and the answer says the volume it was taken at. The volume is put back as it was found.

```
$ mobium launch dev.mobium.mobiumapp
launched dev.mobium.mobiumapp
```

```
$ mobium tap "label=Audio Demo"
tapped label=Audio Demo at (540, 2267)
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
saved evidence/2026-10-07-android-emulator/act4-volume-15.wav: 3.902s of audio: 0.0–0.7s silence, 0.7–2.8s 440 Hz (-9 dBFS), 2.8–3.9s silence — at media volume 15 of 15
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
saved evidence/2026-10-07-android-emulator/act4-volume-5.wav: 3.48s of audio: 0.0–0.3s silence, 0.3–2.4s 440 Hz (-42 dBFS), 2.4–3.5s silence — at media volume 5 of 15
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
saved evidence/2026-10-07-android-emulator/act4-volume-1.wav: 3.472s of audio: 0.0–0.3s silence, 0.3–0.4s sound, no one pitch (-47 dBFS), 0.4–2.4s 440 Hz (-62 dBFS), 2.4–3.5s silence — at media volume 1 of 15
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
saved evidence/2026-10-07-android-emulator/act4-volume-0.wav: 3.477s of audio: 0.0–0.3s silence, 0.3–0.4s sound, no one pitch (-47 dBFS), 0.4–3.5s silence — at media volume 0 of 15, muted, where nothing played as media is heard; interrupted: muted, the device's volume at its lowest 0.3–2.3s
```

Put back to 5. By volume: **15: 440 Hz at -9.3 dBFS; 5: 440 Hz at -41.8 dBFS; 1: 440 Hz at -62.5 dBFS; 0: silence; **

## Act 5 — interrupted: a call

The tone plays until stopped; the emulator rings, and is hung up five seconds later.

```
$ mobium launch dev.mobium.mobiumapp
launched dev.mobium.mobiumapp
```

```
$ mobium tap "label=Audio Demo"
tapped label=Audio Demo at (540, 2325)
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
saved evidence/2026-10-07-android-emulator/act5-call.wav: 14.134s of audio: 0.0–0.8s silence, 0.8–0.9s sound, no one pitch (-47 dBFS), 0.9–3.2s 440 Hz (-42 dBFS), 3.2–3.3s silence, 3.3–3.4s sound, no one pitch (-70 dBFS), 3.4–3.7s 1052 Hz (-24 dBFS), 3.7–3.8s 1240 Hz (-23 dBFS), 3.8–3.9s sound, no one pitch (-24 dBFS), 3.9–4.2s 1240 Hz (-23 dBFS), 4.2–5.2s 1050 Hz (-30 dBFS), 5.2–7.2s silence, 7.2–7.3s 1047 Hz (-26 dBFS), 7.3–7.4s 1240 Hz (-24 dBFS), 7.4–7.5s sound, no one pitch (-25 dBFS), 7.5–7.6s 1046 Hz (-22 dBFS), 7.6–7.7s sound, no one pitch (-26 dBFS), 7.7–8.0s 1046 Hz (-24 dBFS), 8.0–8.1s 1239 Hz (-24 dBFS), 8.1–10.8s 440 Hz (-42 dBFS), 10.8–10.9s sound, no one pitch (-45 dBFS), 10.9–14.1s silence — at media volume 5 of 15; interrupted: muted for a call 3.0–8.0s, a ringtone played 3.3–8.0s
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
saved evidence/2026-10-07-android-emulator/act5-alarm.wav: 7.941s of audio: 0.0–0.3s silence, 0.3–0.4s sound, no one pitch (-47 dBFS), 0.4–4.5s 440 Hz (-42 dBFS), 4.5–4.7s 529 Hz (-19 dBFS), 4.7–4.8s sound, no one pitch (-22 dBFS), 4.8–4.9s 593 Hz (-18 dBFS), 4.9–5.7s sound, no one pitch (-18 dBFS), 5.7–5.9s 391 Hz (-20 dBFS), 5.9–6.1s sound, no one pitch (-20 dBFS), 6.1–6.4s 521 Hz (-18 dBFS), 6.4–6.5s sound, no one pitch (-18 dBFS), 6.5–6.6s 587 Hz (-24 dBFS), 6.6–7.9s 440 Hz (-40 dBFS) — at media volume 5 of 15; interrupted: an alarm played 4.4–6.5s
```

