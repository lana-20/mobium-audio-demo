# Audio on android-phone

Recorded 2026-10-07 04:35 PDT with `mobium version 0.1.0-dev`, on android-phone.

## Act 5 — interrupted: an alarm

A 4-second Clock timer rings over the tone, and is stopped by its own Stop.

```
$ mobium launch dev.mobium.mobiumapp
error: launched dev.mobium.mobiumapp, but the device is locked, so it is behind the lock screen and nothing after this would reach it — run `mobium lock unlock` (app_lock with state "unlock"), which unlocks a device with no PIN, pattern or password, or unlock it by hand
```

```
$ mobium tap "label=Audio Demo"
tapped label=Audio Demo at (504, 2130)
```

```
$ mobium audio start --app dev.mobium.mobiumapp
recording what interrupts the app's audio — a phone's sound is not captured; stop it with action "stop"
```

```
$ mobium tap testid=audioLoop
tapped testid=audioLoop at (504, 943)
```

A 4-second timer set in Clock.

```
$ mobium tap "label=Stop 4 seconds timer"
tapped label=Stop 4 seconds timer at (252, 634)
```

```
$ mobium launch dev.mobium.mobiumapp
launched dev.mobium.mobiumapp
```

```
$ mobium tap testid=audioStop
tapped testid=audioStop at (504, 1347)
```

```
$ mobium audio stop
dev.mobium.mobiumapp's audio over 12.214s — its sound is not captured on a phone; interrupted: an alarm played 5.3–10.5s, muted, the device's volume at its lowest 2 times, each under 0.25s
```

