#!/bin/sh
# The audio demo, start to finish, on one device, with the evidence of every
# step: a WAV and the stop's answer for each capture, a drawing of each
# timeline, the test reports, and a transcript of every command with what it
# printed.
#
#   scripts/demo.sh <serial|udid> [out-dir]
#   ALLOW_PHONE=1 scripts/demo.sh <android-phone-serial> [out-dir]
#
# MOBIUM names the mobium binary (default: mobium on PATH). The device needs
# MobiumApp installed with its Audio Demo.
#
# Act 1  silence that says it is playing: the app and the platform both say
#        a player is playing; the capture hears nothing
# Act 2  hear it: a tone, then 440 Hz, a pause and 880 Hz, as a timeline
# Act 3  as a test: what was played passes; what was not fails, saying what
#        was heard, with the capture kept
# Act 4  the volume: one tone at media volume 15, 5, 1 and 0, then put back
# Act 5  interrupted: an incoming call, then a Clock timer's alarm
#
# An Android emulator runs all five. On an Android phone, whose sound
# nothing outside it hears, only the alarm of act 5 runs, and only with
# ALLOW_PHONE=1: it sets a 4-second timer in the phone's Clock and stops it
# by the timer's own Stop, never by force-stopping Clock, which would cancel
# the owner's alarms. On iOS the capture is refused, and the refusal is
# what is recorded.
set -u
DEV="${1:-}"
if [ -z "$DEV" ]; then echo "usage: $0 <serial|udid> [out-dir]" >&2; exit 2; fi
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MOBIUM="${MOBIUM:-mobium}"
APP=dev.mobium.mobiumapp
case "$DEV" in
  emulator-*) KIND=android-emulator ;;
  *-*-*-*-*) KIND=ios-simulator ;;
  ????????-????????????????) KIND=iphone ;;
  *)
    KIND=android-phone
    if [ "${ALLOW_PHONE:-}" != 1 ]; then
      echo "on a phone this sets, rings and removes a timer in its Clock: run it with ALLOW_PHONE=1" >&2; exit 2
    fi ;;
esac
OUT="${2:-$ROOT/evidence/$(date +%Y-%m-%d)-$KIND}"
mkdir -p "$OUT"
OUT="$(cd "$OUT" && pwd)"
T="$OUT/transcript.md"
: > "$T"
M="$MOBIUM --device $DEV"

# run prints a command and what it printed, to the screen and the
# transcript, and keeps its output in $out and its status in $rc.
run() {
  out=$($M "$@" 2>&1)
  rc=$?
  shown="mobium"
  for a in "$@"; do
    case "$a" in *" "*) shown="$shown \"$a\"" ;; *) shown="$shown $a" ;; esac
  done
  printf '$ %s\n%s\n\n' "$shown" "$out"
  printf '```\n$ %s\n%s\n```\n\n' "$shown" "$out" >> "$T"
  return $rc
}
say() { printf '\n== %s\n\n' "$1"; printf '## %s\n\n' "$1" >> "$T"; }
note() { printf '%s\n\n' "$1"; printf '%s\n\n' "$1" >> "$T"; }

# open_demo launches MobiumApp fresh and opens the Audio Demo.
open_demo() {
  $M terminate "$APP" >/dev/null 2>&1
  run launch "$APP"
  $M scroll-to "label=Audio Demo" --direction down >/dev/null 2>&1
  # Mobium's own error says why — a locked phone, an app not installed, a
  # build without the Audio Demo — so it is passed on rather than guessed at.
  run tap "label=Audio Demo" || { echo "could not open the Audio Demo: $out" >&2; exit 1; }
  $M wait testid=audioState >/dev/null
}

# ended waits for the Audio Demo to say its sound is over.
ended() {
  i=0
  while [ $i -lt 40 ]; do
    case "$($M text testid=audioState 2>/dev/null)" in finished:*|stopped:*) return 0 ;; esac
    sleep 0.25; i=$((i + 1))
  done
}

# stop_capture NAME [WAV]: stops the capture through scripts/stop.py, which
# keeps the structured answer as NAME.json and prints the message, shown and
# kept in the transcript as the command that made it.
stop_capture() {
  if [ -n "${2:-}" ]; then
    said=$(MOBIUM="$MOBIUM" python3 "$ROOT/scripts/stop.py" "$DEV" "$OUT/$1.json" "$OUT/$2" 2>&1)
    shown="mobium audio stop -o $2"
  else
    said=$(MOBIUM="$MOBIUM" python3 "$ROOT/scripts/stop.py" "$DEV" "$OUT/$1.json" 2>&1)
    shown="mobium audio stop"
  fi
  printf '$ %s\n%s\n\n' "$shown" "$said"
  printf '```\n$ %s\n%s\n```\n\n' "$shown" "$said" >> "$T"
}

# capture NAME BUTTON: captures while the Audio Demo plays BUTTON.
capture() {
  run audio start
  run tap "testid=$2"
  ended
  sleep 0.5
  stop_capture "$1" "$1.wav"
}

{
  printf '# Audio on %s\n\n' "$KIND"
  printf 'Recorded %s with `%s`, on %s.\n\n' "$(date '+%Y-%m-%d %H:%M %Z')" "$($MOBIUM --version 2>/dev/null | head -1)" "$KIND"
} >> "$T"

ACT1= ACT2= ACT3PASS= ACT3FAIL= ACT4= ACT5CALL= ACT5ALARM= REFUSED=

case "$KIND" in
  ios-*|iphone)
    say "On iOS"
    note "Neither a simulator's sound nor an iPhone's is captured yet, and the capture says so rather than recording nothing."
    run audio start
    REFUSED=$(printf "%s" "$out" | tail -1)
    ;;
esac

if [ "$KIND" = android-emulator ]; then
  say "Act 1 — silence that says it is playing"
  note "The Audio Demo's silence is a player that is started and plays two seconds of zeros. The app says it is playing; Android's audio service reports a player started, exactly as for a tone. Only the capture says what was heard."
  open_demo
  run audio start
  run tap testid=audioSilent
  sleep 0.5
  run text testid=audioState
  APPSAID="$out"
  uid=$(adb -s "$DEV" shell cmd package list packages -U "$APP" | sed -n 's/.*uid:\([0-9]*\).*/\1/p' | head -1)
  PLATFORM=$(adb -s "$DEV" shell dumpsys audio | sed -n '/players:/,/^$/p' | grep "u/pid:$uid/" | grep -o 'state:[a-z]*' | head -1)
  printf '$ adb shell dumpsys audio   # MobiumApp'"'"'s player\n%s\n\n' "$PLATFORM"
  printf '```\n$ adb shell dumpsys audio   # MobiumApp'"'"'s player\n%s\n```\n\n' "$PLATFORM" >> "$T"
  ended
  sleep 0.5
  stop_capture act1-silence act1-silence.wav
  ACT1="$said"
  note "The app said **$APPSAID**; the platform said **$PLATFORM**; the capture: **$ACT1**."

  say "Act 2 — hear it"
  note "A tone, then 440 Hz, a second of silence and 880 Hz. The answer is a timeline: sound and silence to a tenth of a second, each sound's pitch and level."
  capture act2-tone audioTone
  capture act2-sequence audioSequence
  ACT2="$said"

  say "Act 3 — as a test"
  note "tests/heard.test.json asserts at each stop what was played; tests/wrong.test.json expects what was not, and must fail, saying what was heard."
  CFG="$OUT/mobium.config.json"
  printf '{\n  "testDir": "%s/tests",\n  "projects": [{"name": "%s", "device": "%s"}]\n}\n' "$ROOT" "$KIND" "$DEV" > "$CFG"
  cd "$ROOT"
  run test --config "$CFG" tests/heard.test.json --reporter list,html --output "$OUT/report-heard"
  ACT3PASS=$(echo "$out" | grep -E '^[0-9]+ passed' | tail -1)
  run test --config "$CFG" tests/wrong.test.json --reporter list,html --output "$OUT/report-wrong"
  ACT3FAIL=$(echo "$out" | grep -E '^[0-9]+ passed' | tail -1)
  rm -f "$CFG"
  mv mobium-report/*.wav "$OUT/" 2>/dev/null
  note "Heard: **$ACT3PASS**. Wrong: **$ACT3FAIL**."

  say "Act 4 — the volume"
  note "The same tone at media volume 15, 5, 1 and 0. What arrives follows the volume; at 0 a playing app is silence, and the answer says the volume it was taken at. The volume is put back as it was found."
  open_demo
  was=$(adb -s "$DEV" shell cmd audio get-stream-volume 3 2>/dev/null | grep -o '[0-9]*' | tail -1)
  for v in 15 5 1 0; do
    adb -s "$DEV" shell cmd audio set-volume 3 "$v" >/dev/null
    note "Media volume set to $v."
    capture "act4-volume-$v" audioTone
    ACT4="$ACT4$v: $(python3 -c 'import json,sys
v = json.load(open(sys.argv[1])); t = [s for s in v.get("timeline") or [] if s["sound"] and s["to"] - s["from"] > 3e8]
print(("%.0f Hz at %.1f dBFS" % (t[0].get("hz", 0), t[0]["level"])) if t else "silence")' "$OUT/act4-volume-$v.json" 2>/dev/null); "
  done
  adb -s "$DEV" shell cmd audio set-volume 3 "${was:-5}" >/dev/null
  note "Put back to ${was:-5}. By volume: **$ACT4**"

  say "Act 5 — interrupted: a call"
  note "The tone plays until stopped; the emulator rings, and is hung up five seconds later."
  open_demo
  run audio start --app "$APP"
  run tap testid=audioLoop
  sleep 2
  run call ring
  sleep 5
  run call hang
  sleep 2.5
  run tap testid=audioStop
  ended
  stop_capture act5-call act5-call.wav
  ACT5CALL="$said"
fi

case "$KIND" in
  android-*)
    say "Act 5 — interrupted: an alarm"
    note "A 4-second Clock timer rings over the tone, and is stopped by its own Stop."
    open_demo
    run audio start --app "$APP"
    run tap testid=audioLoop
    adb -s "$DEV" shell am start -a android.intent.action.SET_TIMER --ei android.intent.extra.alarm.LENGTH 4 \
      --ez android.intent.extra.alarm.SKIP_UI true >/dev/null
    note "A 4-second timer set in Clock."
    i=0
    until adb -s "$DEV" shell dumpsys audio | sed -n '/players:/,/^$/p' | grep 'state:started' | grep -q USAGE_ALARM; do
      i=$((i + 1)); [ $i -lt 40 ] || break
      sleep 0.25
    done
    sleep 2
    if [ "$KIND" = android-phone ]; then
      adb -s "$DEV" shell am start -a android.intent.action.SHOW_TIMERS >/dev/null
      $M wait "label=Stop 4 seconds timer" --timeout 5s >/dev/null 2>&1
      run tap "label=Stop 4 seconds timer"
      run launch "$APP"
    else
      # An emulator's Clock holds nobody's alarms, and is stopped outright.
      adb -s "$DEV" shell am force-stop com.google.android.deskclock
      adb -s "$DEV" shell pm clear com.google.android.deskclock >/dev/null
      note "Clock stopped."
    fi
    run tap testid=audioStop
    if [ "$KIND" = android-phone ]; then stop_capture act5-alarm; else stop_capture act5-alarm act5-alarm.wav; fi
    ACT5ALARM="$said"
    $M terminate "$APP" >/dev/null 2>&1
    ;;
esac

python3 - "$OUT/summary.json" <<EOF
import json, sys
json.dump({
  "device": "$KIND",
  "act1": """$ACT1""",
  "act2": """$ACT2""",
  "act3": {"heard": "$ACT3PASS", "wrong": "$ACT3FAIL"},
  "act4": """$ACT4""",
  "act5": {"call": """$ACT5CALL""", "alarm": """$ACT5ALARM"""},
  "refused": """$REFUSED""",
}, open(sys.argv[1], "w"), indent=2)
EOF
python3 "$ROOT/scripts/timeline.py" "$OUT" >/dev/null
# A real phone's UDID or serial names the phone: it becomes the device's kind.
case "$KIND" in
  android-phone|iphone) python3 "$ROOT/scripts/scrub.py" "$OUT" --redact "$DEV=$KIND" >/dev/null ;;
  *) python3 "$ROOT/scripts/scrub.py" "$OUT" >/dev/null ;;
esac
echo "evidence: $OUT"
ls "$OUT"
