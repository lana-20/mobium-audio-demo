# Quick start: hear what the app played

Install Mobium, put MobiumApp on an emulator, and hear its Audio Demo: a
silence the app calls playing, a sequence of tones as a timeline, the same
asserted — passing and failing — and an incoming call cutting across it.

Every command and output below was run from scratch on 7 October 2026, on a
Mac with a Pixel 7 emulator (Android 15): Mobium installed with `go install`,
MobiumApp cloned and built fresh, this repository freshly cloned. Paths in
the outputs are shortened to `~`. A real Android phone works too, with less
to hear; [its steps are at the end](#on-an-android-phone).

## Contents

- [1. What you need](#1-what-you-need)
- [2. Install Mobium](#2-install-mobium)
- [3. Put MobiumApp on the emulator](#3-put-mobiumapp-on-the-emulator)
- [4. Silence that says it is playing](#4-silence-that-says-it-is-playing)
- [5. Hear it](#5-hear-it)
- [6. Assert it](#6-assert-it)
- [7. Interrupted](#7-interrupted)
- [On an Android phone](#on-an-android-phone)
- [On iOS](#on-ios)
- [Next](#next)

## 1. What you need

- **Go 1.24 or later**, to install Mobium.
- **An Android emulator**, running. Any recent one; this was a Pixel 7 image,
  Android 15. Android Studio's Device Manager makes one, or `avdmanager` on
  the command line. Mobium hears the emulator through its own control port,
  which the emulator opens by default for this machine only — nothing to
  set up, and its sound need not reach your speakers.
- **Node 20 or later and JDK 17 or later**, to build MobiumApp. This run used
  Node 24 and JDK 21.
- **git**.

## 2. Install Mobium

```sh
go install github.com/mobiumdev/mobium/cmd/mobium@latest
mobium --version
```

```
mobium version v0.0.0-20261007113950-7b2543c995d4
```

That took 11 seconds. (Mobium has no tagged release yet, so `@latest` is the
newest commit on `main`.) `mobium` lands in `$(go env GOPATH)/bin`, which
should be on your `PATH`. Check that it sees the emulator:

```sh
mobium devices
```

```
emulator-5554                          device     (android emulator, model: sdk_gphone64_arm64, navigation: gestures)
```

## 3. Put MobiumApp on the emulator

MobiumApp is Mobium's own app under test. Its Audio Demo plays known sounds,
generated, at a quarter of full volume. Build it as a Release build, which
bundles its JavaScript, so it runs without a development server:

```sh
git clone https://github.com/mobiumdev/mobium-app.git
cd mobium-app
npm install
npx expo prebuild --platform android
npx expo run:android --variant release
```

The last command builds the app, installs it on the emulator and opens it —
and then stays, showing the app's logs: press **Ctrl-C** once it says
*Logs for your project will appear below*. A first build takes a few
minutes while Gradle downloads its dependencies. With more than one device
attached it asks which; name the emulator with `--device <avd-name>`.

Then this repository, for its tests:

```sh
cd ..
git clone https://github.com/lana-20/mobium-audio-demo.git
cd mobium-audio-demo
```

## 4. Silence that says it is playing

Open the Audio Demo and play its silence: a player that is started and
plays two seconds of zeros.

```sh
mobium launch dev.mobium.mobiumapp
mobium tap "label=Audio Demo"
mobium tap testid=audioSilent
mobium text testid=audioState
```

```
playing: silence for 2 s (media)
```

The app says it is playing, and Android's audio service would say the same
of its player — exactly what it says for a tone. Now capture it:

```sh
mobium audio start
mobium tap testid=audioSilent
mobium audio stop -o silence.wav
```

```
saved ~/mobium-audio-demo/silence.wav: 3.282s of audio: 0.0–0.3s silence, 0.3–0.4s sound, no one pitch (-47 dBFS), 0.4–3.3s silence — at media volume 5 of 15
```

Silence. The tenth of a second of sound at 0.3 s is the tap's own click:
the emulator has touch sounds on, and the capture holds everything the
device played.

## 5. Hear it

The sequence: 440 Hz for two seconds, a second of silence, 880 Hz for two.

```sh
mobium audio start
mobium tap testid=audioSequence
mobium audio stop -o sequence.wav
```

```
saved ~/mobium-audio-demo/sequence.wav: 6.787s of audio: 0.0–0.3s silence, 0.3–2.4s 440 Hz (-42 dBFS), 2.4–3.3s silence, 3.3–5.4s 880 Hz (-42 dBFS), 5.4–6.8s silence — at media volume 5 of 15
```

Each sound, when it was, its pitch and its level. The app wrote its tones at
-15 dBFS; they arrived at -42 because the emulator's media volume is 5 of
15 — which is why the answer says the volume, and why a test asserts pitch
and length, never level. `sequence.wav` is the capture itself, 48 kHz mono.

## 6. Assert it

`--expect` makes the stop an assertion: the sounds to hear, in order, each a
pitch with an optional length in seconds.

```sh
mobium audio start
mobium tap testid=audioSequence
mobium audio stop -o sequence.wav --expect 440:1.8-2.3,880:1.8-2.3
```

```
saved ~/mobium-audio-demo/sequence.wav: 6.79s of audio: 0.0–0.3s silence, 0.3–2.4s 440 Hz (-42 dBFS), 2.4–3.3s silence, 3.3–5.4s 880 Hz (-42 dBFS), 5.4–6.8s silence — at media volume 5 of 15
```

Expect what was not played:

```sh
mobium audio start
mobium tap testid=audioTone
mobium audio stop -o tone.wav --expect 880
```

```
error: expected 880 Hz; heard 440 Hz for 2.1s (0.3–2.4s) — at media volume 5 of 15 — the capture is saved at ~/mobium-audio-demo/tone.wav
```

It fails, says what was heard, and keeps the capture. `--expect silence`
asserts nothing was heard; sounds of 200 ms or less — a tap's click — do
not count.

The same in a test file is a step:

```sh
mobium test tests/heard.test.json
```

```
  ok    [android · emulator-5554] heard.test.json › the sequence is heard in order (9.7s)
  ok    [android · emulator-5554] heard.test.json › silence is heard as silence (7.5s)
2 passed (17.2s)
```

```sh
mobium test tests/wrong.test.json
```

```
  FAIL  [android · emulator-5554] wrong.test.json › 880 Hz expected, 440 Hz played (8.1s)
        step 4 (app_audio): [not_confirmed] step 4 of 4 (app_audio) failed: expected 880 Hz; heard 440 Hz for 2.0s (0.4–2.4s) — at media volume 5 of 15 — the capture is saved at ~/mobium-audio-demo/mobium-report/wrong-pitch.wav; steps 1-3 ran before it, and nothing after
  FAIL  [android · emulator-5554] wrong.test.json › silence expected, a tone played (7s)
        step 4 (app_audio): [not_confirmed] step 4 of 4 (app_audio) failed: expected silence; heard 440 Hz for 2.1s (0.3–2.4s) — at media volume 5 of 15 — the capture is saved at ~/mobium-audio-demo/mobium-report/wrong-silence.wav; steps 1-3 ran before it, and nothing after
0 passed, 2 failed (15.1s)
error: 2 of 2 tests failed
```

## 7. Interrupted

Play the tone until stopped, ring the emulator, hang up:

```sh
mobium audio start --app dev.mobium.mobiumapp
mobium tap testid=audioLoop
mobium call ring
mobium call hang
mobium tap testid=audioStop
mobium audio stop -o call.wav
```

```
ringing a call from 5551234
ended a call from 5551234
```

The stop's answer ends:

```
— at media volume 5 of 15; interrupted: muted for a call 2.7–7.5s, a ringtone played 2.9–7.6s
```

Between those times the timeline holds the ring's own pitches and no
440 Hz: Android silenced the app for as long as the phone rang and gave it
back after. The app said it was playing throughout. `interrupted` comes
from Android's audio service: the app muted, for a call or by a volume,
and any other app's sound over it — a ringtone, an alarm, a notification,
another app's media — each named by what it is for.

## On an Android phone

Nothing outside a phone hears what it plays, so on an Android phone a
capture records what interrupted the app, and nothing is put on the phone.
On a Pixel 8 Pro (Android 17), with MobiumApp installed, the tone playing
and a 4-second Clock timer ringing over it, stopped with its own Stop in Clock:

```sh
mobium audio start
mobium tap testid=audioLoop
# a Clock timer rings; stop it
mobium tap testid=audioStop
mobium audio stop
```

```
recording what interrupts the app's audio — a phone's sound is not captured; stop it with action "stop"
```

```
dev.mobium.mobiumapp's audio over 12.171s — its sound is not captured on a phone; interrupted: an alarm played 5.3–10.5s, muted, the device's volume at its lowest 2 times, each under 0.25s
```

The two brief mutes are Android's: it muted the app's media for 40 ms each
time the alarm's sound began again. `--expect` is refused on a phone, saying
why:

```
error: a phone's sound is not captured, so there is nothing to hold expect against — only what interrupted the app, in the result's interruptions. Assert what was heard on an emulator
```

## On iOS

The capture is refused on an iOS simulator and an iPhone, saying why:

```
error: a simulator's audio is not captured yet — it plays through the Mac's own audio device for simulators, which Mobium does not read. Capture on an Android emulator
```

## Next

- [The tutorial](TUTORIAL.md): the same from Python, what the answer holds,
  the volume, an alarm, writing your own app's audio tests, and running it
  in CI.
- [`scripts/demo.sh`](../scripts/demo.sh) runs all of this on a device and
  keeps the evidence; [`evidence/README.md`](../evidence/README.md) has
  every run's.
