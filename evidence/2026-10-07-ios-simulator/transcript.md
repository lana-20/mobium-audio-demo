# Audio on ios-simulator

Recorded 2026-10-07 04:36 PDT with `mobium version 0.1.0-dev`, on ios-simulator.

## On iOS

Neither a simulator's sound nor an iPhone's is captured yet, and the capture says so rather than recording nothing.

```
$ mobium audio start
waiting for WebDriverAgent to start...
the simulator is on its home screen: a new session starts WebDriverAgent, whose runner takes the foreground and leaves it to the home screen, not to the app that was in front — app_launch brings an app back...
error: a simulator's audio is not captured yet — it plays through the Mac's own audio device for simulators, which Mobium does not read. Capture on an Android emulator
```

