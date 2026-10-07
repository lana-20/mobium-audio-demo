"""Audio from Python: capture what MobiumApp's Audio Demo plays, assert it,
and read what interrupted it.

    MOBIUM_DEVICE=emulator-5554 python3 examples/hear.py

On an emulator the sequence is heard — 440 Hz, a second of silence, 880 Hz —
and a wrong expectation raises NotConfirmedError saying what was heard,
with the capture still saved. On an Android phone the sound is not
captured, only what interrupted the app; this script says so and stops.
"""
import os
import time

from mobium import NotConfirmedError, UnsupportedError, connect

APP = "dev.mobium.mobiumapp"


def audio_demo(device):
    """Launch MobiumApp fresh and open the Audio Demo."""
    device.terminate(APP)
    device.launch(APP)
    device.scroll_to("label=Audio Demo", direction="down")
    device.tap("label=Audio Demo")


def played(device, button, finished):
    """Tap one of the Audio Demo's buttons and wait for its sound to end.

    The wait names this sound's own line: "finished:" alone is met at once
    by the line the last sound left, and the capture would stop mid-tone.
    """
    device.tap(f"testid={button}")
    device.wait_for("testid=audioState", condition="text", text=f"finished: {finished}", timeout_ms=10000)
    time.sleep(0.5)


device = connect(device=os.environ.get("MOBIUM_DEVICE"))
try:
    audio_demo(device)

    # The sequence, asserted at the stop: two pitches, in order, each about
    # two seconds long.
    device.audio("start")
    played(device, "audioSequence", "440 Hz 2 s, silence 1 s, 880 Hz 2 s")
    try:
        heard = device.audio("stop", "sequence.wav", expect=[
            {"hz": 440, "min_ms": 1800, "max_ms": 2300},
            {"hz": 880, "min_ms": 1800, "max_ms": 2300},
        ])
    except UnsupportedError as e:
        print(f"no sound captured here: {e}")
        raise SystemExit(0)
    for s in heard["timeline"]:
        what = f"{s['hz']:.0f} Hz at {s['level']:.0f} dBFS" if s.get("hz") else ("sound" if s["sound"] else "silence")
        print(f"  {s['from'] / 1e9:4.1f}–{s['to'] / 1e9:4.1f}s  {what}")
    media = next(v for v in heard["volumes"] if v["stream"] == "media")
    print(f"heard as expected, at media volume {media['index']} of {media['max']}")

    # A wrong expectation fails, says what was heard, and keeps the capture.
    device.audio("start")
    played(device, "audioTone", "440 Hz for 2 s")
    try:
        device.audio("stop", "wrong.wav", expect=[{"hz": 880}])
    except NotConfirmedError as e:
        print(f"a wrong expectation: {e}")
finally:
    device.close()
