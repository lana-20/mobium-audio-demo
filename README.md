# Hear the app

What an app played, heard and asserted — and what cut across it, a call or
an alarm — with [Mobium](https://github.com/mobiumdev/mobium)'s audio
capture, on [MobiumApp](https://github.com/mobiumdev/mobium-app), on an
Android emulator and a real Android phone.

| | |
| --- | --- |
| **[Quick start](docs/QUICKSTART.md)** | install Mobium, put MobiumApp on an emulator, and hear a silence the app calls playing, a sequence as a timeline, the same asserted, and a call cutting across it |
| **[Tutorial](docs/TUTORIAL.md)** | from Python, what the answer holds, the volume, an alarm, your own app, CI, and proving it on your devices |
| **[Evidence](evidence/README.md)** | every run behind the numbers here: transcripts, WAVs, each capture's answer and a drawing of it, the test reports |
| **[Tests](tests/)** | `heard.test.json` asserts what was played; `wrong.test.json` must fail, saying what was heard |
| **[From Python](examples/hear.py)** | the same capture and assertion from a script |

Every command and output in the quick start and the tutorial was run from
scratch — Mobium installed with `go install`, MobiumApp and this repository
freshly cloned — and is shown as it printed.

Everything here runs. `scripts/demo.sh` drives one device through five
acts and keeps the evidence of each; `scripts/summarize.py` writes
[`evidence/README.md`](evidence/README.md) from the runs, so no number on
this page is typed by hand.

## The problem

MobiumApp's Audio Demo plays known sounds. One of them is silence: a
player that is started and plays two seconds of zeros.

```
$ mobium tap testid=audioSilent
$ mobium text testid=audioState
playing: silence for 2 s (media)
$ adb shell dumpsys audio   # MobiumApp's player
state:started
```

The app says it is playing. Android's audio service says a player has
started — exactly what it says for a tone. Neither can tell you whether
anything was heard. Only the sound can.

```
$ mobium audio start
$ mobium tap testid=audioSilent
$ mobium audio stop -o silence.wav
saved silence.wav: 3.487s of audio: 0.0–0.3s silence, 0.3–0.4s sound, no one pitch (-47 dBFS), 0.4–3.5s silence — at media volume 5 of 15
```

The tenth of a second of sound is the tap's own click: touch sounds are on,
and the capture holds everything the device played.

## The five acts

| Act | What happens | What it shows |
| --- | --- | --- |
| 1. Silence that says it is playing | the Audio Demo's silence | the app and the platform say playing; the capture hears silence |
| 2. Hear it | a tone, then 440 Hz, a second of silence and 880 Hz | a timeline: sound and silence to a tenth of a second, each sound's pitch and level |
| 3. As a test | [`tests/heard.test.json`](tests/heard.test.json) and [`tests/wrong.test.json`](tests/wrong.test.json) | what was played passes; what was not fails, saying what was heard, with the capture kept |
| 4. The volume | the tone at media volume 15, 5, 1 and 0, then put back | -9, -42 and -63 dBFS, then silence — and the answer says the volume it was taken at |
| 5. Interrupted | an incoming call, then a Clock timer's alarm | the tone silenced while the call rings and given back; the answer says *muted for a call*, *a ringtone*, *an alarm* |

The figures are the emulator run's; [`evidence/README.md`](evidence/README.md)
has every run's.

## Asserting it

A capture is asserted where it stops: the sounds to hear, in order, each a
pitch with an optional length, and `[]` for silence.

```json
{"audio": {"action": "stop", "path": "mobium-report/sequence.wav", "expect": [
  {"hz": 440, "min_ms": 1800, "max_ms": 2300},
  {"hz": 880, "min_ms": 1800, "max_ms": 2300}
]}}
```

Expect what was not played and the step fails, saying so, with the
capture saved as the evidence:

```
FAIL  [android-emulator · emulator-5554] wrong.test.json › 880 Hz expected, 440 Hz played (7.7s)
      step 4 (app_audio): [not_confirmed] step 4 of 4 (app_audio) failed: expected 880 Hz; heard 440 Hz for 2.1s (0.3–2.4s) — at media volume 5 of 15 — the capture is saved at mobium-report/wrong-pitch.wav; steps 1-3 ran before it, and nothing after
```

Assert pitch and length, never level: the level follows the device's
media volume, and at its lowest an app that plays is heard as silence.
Sounds of 200 ms or less do not count against an expectation — a tap's
click is 100.

## Interrupted

An incoming call over the tone, on the emulator:

![The tone, the ring, and the tone again; under it, the app muted for the call and a ringtone playing](evidence/2026-10-07-android-emulator/act5-call.svg)

Android silenced the app for as long as the phone rang and gave it back
after the hang-up. The app said it was playing throughout. The capture's
answer says what happened, read from Android's audio service:

```
interrupted: muted for a call 2.5–7.4s, a ringtone played 2.7–7.5s
```

Any sound counts: an alarm, a notification, a voice call, the assistant,
navigation, another app's media — each named by what it is for — and the
app muted for any reason, with Android's. A touch's click does not.

## On a real phone

Nothing outside a phone hears what it plays. On an Android phone
`mobium audio start` records what interrupted the app instead — the same
audio service, the same answer — with nothing put on the phone:

```
$ mobium audio stop
dev.mobium.mobiumapp's audio over 12.214s — its sound is not captured on a phone; interrupted: an alarm played 5.3–10.5s, muted, the device's volume at its lowest 2 times, each under 0.25s
```

That is a Pixel 8 Pro with a Clock timer ringing over the tone. So a test
on any Android phone adb reaches — a device farm's included — can say a
call or an alarm cut across the app. Making a phone ring takes a call
from outside it, which only a farm with a line can place; an emulator
rings with `mobium call ring`.

On iOS the capture is refused, saying why.

## Run it

```sh
go install github.com/mobiumdev/mobium/cmd/mobium@latest
scripts/demo.sh emulator-5554                    # all five acts
ALLOW_PHONE=1 scripts/demo.sh <phone-serial>     # the alarm, on a phone
python3 scripts/summarize.py                     # evidence/README.md
```

MobiumApp must be installed with its Audio Demo; see
[MobiumApp](https://github.com/mobiumdev/mobium-app). On a phone, the demo
sets a 4-second timer in Clock and stops it with the timer's own Stop,
which removes it; it never force-stops Clock, which would cancel the
phone owner's alarms. Evidence names no phone: `scripts/scrub.py` replaces
a phone's serial with its kind and takes this machine's paths out.
