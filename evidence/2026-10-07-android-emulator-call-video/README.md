# The call, recorded and heard

The deck's call video, on the Pixel 7 emulator (Android 15): the screen
recorded with `mobium record` and the sound captured with `mobium audio`,
started together, while the Audio Demo played its tone until stopped and
the emulator rang for five seconds.

```
$ mobium record start
$ mobium audio start --app dev.mobium.mobiumapp
$ mobium tap testid=audioLoop
$ mobium call ring
$ mobium call hang
$ mobium tap testid=audioStop
$ mobium audio stop -o call.wav
… interrupted: muted for a call 3.7–8.5s, a ringtone played 3.9–8.6s
$ mobium record stop -o call.mp4
… 67 frames, 15.327s of video, recorded over 13.854s
```

The two are aligned by the ring's first moment: the phone icon appears in
the status bar 4.6 s into the video, and the ringtone 3.9 s into the
capture, so the capture is laid 0.7 s late under the video in
`deck/media/call-heard.mp4`. `call.mp4` is the recording and `call.wav` the
capture, as Mobium saved them.
