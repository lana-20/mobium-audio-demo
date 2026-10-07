#!/usr/bin/env python3
"""Builds the talk: writes deck/slides/*.html and deck/deck.json from the
evidence, then wraps them in a viewer as index.html, which Pages serves.

    python3 scripts/build_deck.py

Every figure and timeline on a slide is read from evidence/ when it is
built, and each slide's <aside> is its speaker notes (S shows them). The
sounds are the captures themselves, in deck/media/: the evidence's WAVs as
AAC, and a screen recording of the emulator during a call with the audio
Mobium captured at the same time laid under it.
"""
import html as htmlmod
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DECK = ROOT / "deck"
EMU = ROOT / "evidence" / "2026-10-07-android-emulator"
PHONE = ROOT / "evidence" / "2026-10-07-android-phone"

BG, INK, DIM, WELL, RULE = "#141A21", "#EDEAE3", "#94A0AB", "#0E1318", "#2A343E"
BRASS, RED, GREEN, BLUE, SLATE = "#E0A526", "#C4452F", "#4C8C6A", "#6F95C8", "#5E6A76"
MONO = "'Fira Code', 'Courier New', monospace"
FONTS = "https://fonts.googleapis.com/css2?family=Rubik:wght@300;400;500;600;700&family=Fira+Code:wght@400;500;600&display=swap"


def answer(run, name):
    return json.loads((run / f"{name}.json").read_text())


def section(sid, body, notes, pad="120px 128px 96px", gap=36, center=True, mark=True):
    just = "center" if center else "flex-start"
    return (f'<section id="{sid}" style="background:{BG}; color:{INK}; font-family:Rubik, Arial, sans-serif; '
            f'padding:{pad}; display:flex; flex-direction:column; justify-content:{just}; gap:{gap}px">\n'
            f'{body}\n'
            + (f'  <img src="deck/media/mark3d.png" alt="Mobium" style="position:absolute; right:48px; top:40px; width:64px; height:64px; object-fit:contain">\n' if mark else '')
            + f'  <aside>{htmlmod.escape(notes)}</aside>\n</section>\n')


def eyebrow(text, color=BRASS):
    return f'  <p style="font-family:{MONO}; font-size:26px; color:{color}; letter-spacing:2px; text-transform:uppercase">{text}</p>'


def h(text, size=72):
    return f'  <h2 style="font-size:{size}px; font-weight:600; line-height:1.08; letter-spacing:-1px">{text}</h2>'


def para(text, size=34, color="#BDC6CE", width=None):
    w = f" width:{width}px;" if width else ""
    return f'  <p style="font-size:{size}px; font-weight:300; line-height:1.42; color:{color};{w}">{text}</p>'


def code(text, size=28):
    return (f'  <pre style="font-family:{MONO}; font-size:{size}px; line-height:1.6; color:#BDC6CE; background:{WELL}; '
            f'border:1px solid {RULE}; border-radius:16px; padding:28px 34px; white-space:pre-wrap">{text}</pre>')


def player(src, label):
    return (f'  <div style="display:flex; align-items:center; gap:24px"><span style="font-family:{MONO}; font-size:24px; '
            f'color:{DIM}; letter-spacing:1px; text-transform:uppercase">{label}</span>'
            f'<audio controls preload="metadata" src="deck/media/{src}" style="width:620px"></audio></div>')


def tone(hz):
    if hz and abs(hz - 440) <= 9:
        return GREEN, "440 Hz"
    if hz and abs(hz - 880) <= 18:
        return BLUE, "880 Hz"
    return SLATE, ""


def lanes(a, width=1520):
    """A capture's answer drawn to scale: what was heard, then each kind of
    interruption that lasted a quarter of a second or more."""
    length = a["duration"] / 1e9
    x = lambda ns: min(max(ns / 1e9, 0), length) / length * 100
    def lane(label, bars):
        return (f'<div style="display:grid; grid-template-columns:160px 1fr; gap:24px; align-items:center">'
                f'<span style="font-family:{MONO}; font-size:24px; color:{DIM}">{label}</span>'
                f'<div style="position:relative; height:76px; background:{WELL}; border:1px solid {RULE}; border-radius:10px">{bars}</div></div>')
    def bar(a_, b_, color, text=""):
        return (f'<div style="position:absolute; top:9px; bottom:9px; left:{x(a_):.2f}%; width:calc({x(b_) - x(a_):.2f}% + 1px); '
                f'background:{color}; border-radius:6px; display:flex; align-items:center; justify-content:center; '
                f'font-family:{MONO}; font-size:24px; font-weight:600; color:{BG}; overflow:hidden; white-space:nowrap">{text}</div>')
    heard = ""
    for s in a["timeline"]:
        if s["sound"]:
            color, name = tone(s.get("hz"))
            heard += bar(s["from"], s["to"], color, name if (s["to"] - s["from"]) / 1e9 / length > 0.1 else "")
    rows = [lane("heard", heard)]
    colors = {"muted": RED, "ringtone": BRASS, "alarm": BRASS}
    for kind in dict.fromkeys(c["kind"] for c in a.get("interruptions") or []):
        bars = "".join(bar(c["from"], c["to"], colors.get(kind, BRASS), "for the call" if c.get("reason") == "call" else "")
                       for c in a["interruptions"] if c["kind"] == kind and c["to"] - c["from"] >= 2.5e8)
        if bars:
            rows.append(lane(kind, bars))
    step = 2 if length > 6 else 1
    ticks = "".join(f'<span>{t} s</span>' for t in range(0, int(length) + 1, step))
    rows.append(f'<div style="display:grid; grid-template-columns:160px 1fr; gap:24px"><span></span>'
                f'<div style="display:flex; justify-content:space-between; font-family:{MONO}; font-size:20px; color:{DIM}">{ticks}</div></div>')
    return f'  <div style="display:grid; gap:18px; width:{width}px">' + "".join(rows) + "</div>"


def part(sid, n, title, line, notes):
    body = (f'  <p style="font-family:{MONO}; font-size:30px; color:{BRASS}; letter-spacing:3px; text-transform:uppercase">Part {n}</p>\n'
            f'  <h1 style="font-size:132px; font-weight:600; line-height:1.02; letter-spacing:-2px">{title}</h1>\n'
            f'  <div style="width:180px; height:5px; background:{RED}"></div>\n'
            + para(line, size=40, width=1300))
    return section(sid, body, notes)


def slides():
    seq, call, alarm = answer(EMU, "act2-sequence"), answer(EMU, "act5-call"), answer(EMU, "act5-alarm")
    phone = answer(PHONE, "act5-alarm")
    summary = json.loads((EMU / "summary.json").read_text())
    def level(v):
        s = [x for x in answer(EMU, f"act4-volume-{v}")["timeline"] if x["sound"] and x["to"] - x["from"] > 3e8]
        return f"{s[0]['level']:.0f} dBFS" if s else "silence"
    vol = {v: level(v) for v in (15, 5, 1, 0)}
    span = lambda c: f"{c['from'] / 1e9:.1f}–{c['to'] / 1e9:.1f} s"
    mute = next(c for c in call["interruptions"] if c["kind"] == "muted")
    ring = next(c for c in call["interruptions"] if c["kind"] == "ringtone")
    emu_alarm = next(c for c in alarm["interruptions"] if c["kind"] == "alarm")
    pix_alarm = next(c for c in phone["interruptions"] if c["kind"] == "alarm")
    out = []

    out.append(("cover", section("cover", f"""  <p style="font-family:{MONO}; font-size:24px; color:{BRASS}; letter-spacing:2px; text-transform:uppercase">Audio testing &nbsp;·&nbsp; Mobium</p>
  <h1 style="font-size:132px; font-weight:600; line-height:1.04; letter-spacing:-2px">Hear the App</h1>
  <div style="width:180px; height:5px; background:{RED}"></div>
  <video src="deck/media/mobium-logo.mp4" poster="deck/media/mobium-logo.jpg" aria-label="The Mobium logo turns into a blue butterfly and back" style="position:absolute; right:128px; top:560px; width:360px; height:360px; object-fit:cover; border-radius:26px" autoplay muted loop playsinline></video>
{para("An app can say it is playing and play nothing. How a test hears what it played, asserts it, and learns what cut across it — measured on an Android emulator and a Pixel 8 Pro.", size=38, width=1150)}
  <p style="position:absolute; left:128px; bottom:64px; font-family:{MONO}; font-size:24px; color:{DIM}">Lana Begunova &nbsp;·&nbsp; SDET &mdash; AI | UI | API &nbsp;·&nbsp; Seattle</p>""",
        "Go straight to the cold open: three sources, one silence. The introduction comes after it, in one line. The tile on the right is Mobium's logo turning into a butterfly and back; let it loop.", pad="128px 128px 160px", gap=40, mark=False)))

    rows = "".join(
        f'<div style="display:flex; justify-content:space-between; align-items:baseline; font-family:{MONO}; font-size:40px; '
        f'padding:28px 36px; background:{WELL}; border:1px solid {RULE}; border-radius:14px"><span>{a}</span>'
        f'<em style="font-style:normal; font-size:26px; color:{DIM}">{b}</em></div>'
        for a, b in [("playing: silence for 2 s", "the app says"),
                     (f'state: <b style="color:{GREEN}">started</b>', "Android says"),
                     (f'<b style="color:{RED}">silence throughout</b>', "Mobium heard")])
    out.append(("open", section("open", f"""{eyebrow("The cold open")}
{h("Three answers. One silence.", 84)}
  <div style="display:grid; gap:20px; width:1400px">{rows}</div>
{player("act1-silence.m4a", "what it played")}""",
        "MobiumApp's Audio Demo plays two seconds of zeros: a player that is started, and silent. The app's own line says playing. Android's audio service, asked the ordinary way, says the player is started, exactly what it says for a tone. Press play: that is the capture, and the only thing on it is the tap's own click near the start. Then introduce yourself in one line.")))

    out.append(("premise", section("premise", f"""{eyebrow("The premise")}
{h("Sound is an output. Test it like one.", 80)}
{para("A notification chime, a voice prompt, a beep that confirms a scan, music that should pause when a call comes in. Tests assert on what is on screen and let the speaker go unheard.", size=38, width=1500)}
  <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:28px; width:1600px; margin-top:12px">
    {''.join(f'<div style="background:{WELL}; border:1px solid {RULE}; border-radius:14px; padding:32px"><p style="font-family:{MONO}; font-size:26px; color:{BRASS}; text-transform:uppercase; letter-spacing:2px">{a}</p><p style="font-size:30px; font-weight:300; line-height:1.4; color:#BDC6CE; margin-top:14px">{b}</p></div>' for a, b in [("Hear it", "what was played, when, at what pitch"), ("Assert it", "in a test, failing with what was heard"), ("Interrupted", "what cut across the app, and when")])}
  </div>""",
        "Three parts, and a fourth on real phones. Everything on the slides was measured on devices; the evidence is in the repository.")))

    out.append(("part1", part("part1", 1, "Hear it", "A timeline of what the device played: sound and silence to a tenth of a second, each sound's pitch and level.",
        "Part 1: what Mobium hears, and from where.")))

    out.append(("hear", section("hear", f"""{eyebrow("440 Hz, a second of silence, 880 Hz")}
{h("A timeline, not a waveform.", 76)}
{code('<span style="color:#5E6A76">$</span> mobium audio start\n<span style="color:#5E6A76">$</span> mobium tap testid=audioSequence\n<span style="color:#5E6A76">$</span> mobium audio stop -o sequence.wav')}
{lanes(seq)}
{player("act2-sequence.m4a", "the capture")}""",
        f"The answer to the stop: {summary['act2']}. The level is minus 42 dBFS because the emulator's media volume is 5 of 15; Part 2 comes back to that.")))

    out.append(("how", section("how", f"""{eyebrow("Where the sound comes from")}
{h("Nothing installed. Nothing on the speakers.", 76)}
  <div style="display:grid; gap:26px; width:1550px">
    {''.join(f'<div style="padding-left:30px; border-left:6px solid {RULE}"><p style="font-size:38px; font-weight:500">{a}</p><p style="font-size:30px; font-weight:300; color:{DIM}; margin-top:8px; line-height:1.4">{b}</p></div>' for a, b in [("The emulator's own audio stream", "read over its control port, which it opens for this machine only, with a token. No sound device on the computer, no app on the device."), ("Silent on the machine", "booted headless with its audio off, the emulator still hands its sound to the capture."), ("Read in tenths of a second", "loudness, and the pitch when one frequency holds most of the sound. A click, speech, noise: sound with no one pitch.")])}
  </div>""",
        "The emulator streams its audio in packets of 20 to 30 milliseconds. Mobium reads it with Go's standard library, places it by the clock so a pause in the stream is silence where it fell, and writes a WAV and a timeline.")))

    out.append(("part2", part("part2", 2, "Assert it", "The sounds to hear, in order, each a pitch with an optional length. Anything else fails, saying what was heard.",
        "Part 2: turning the timeline into a test.")))

    out.append(("assert", section("assert", f"""{eyebrow("At the stop")}
{h("Pitch and length, in order.", 76)}
{code(f'<span style="color:#5E6A76">$</span> mobium audio stop -o seq.wav <span style="color:{BRASS}">--expect 440:1.8-2.3,880:1.8-2.3</span>\n<span style="color:#9AD3B1">saved seq.wav: … 440 Hz … 880 Hz …</span>\n\n<span style="color:#5E6A76">$</span> mobium audio stop -o tone.wav <span style="color:{BRASS}">--expect 880</span>\n<span style="color:#E2735C">error: expected 880 Hz; heard 440 Hz for 2.1s (0.3–2.4s)\n— the capture is saved at tone.wav</span>', size=30)}
{para("A wrong expectation fails, says what was heard, and keeps the capture as the evidence. --expect silence asserts nothing was heard; a sound of a fifth of a second or less, like a tap's click, does not count.", size=32, width=1550)}""",
        "The assertion is part of the stop, so it is the same from the command line, in a test file, and from every client. The capture is saved even when the expectation fails: that is when you want to listen to it.")))

    out.append(("test", section("test", f"""{eyebrow("In a test file")}
{h("One step. Five clients.", 76)}
{code(f'{{"audio": {{"action": "stop", "path": "mobium-report/sequence.wav", "expect": [\n  {{"hz": 440, "min_ms": 1800, "max_ms": 2300}},\n  {{"hz": 880, "min_ms": 1800, "max_ms": 2300}}\n]}}}}', size=28)}
{code(f'<span style="color:#5E6A76">$</span> mobium test tests/heard.test.json   <span style="color:#9AD3B1">{summary["act3"]["heard"]}</span>\n<span style="color:#5E6A76">$</span> mobium test tests/wrong.test.json   <span style="color:#E2735C">{summary["act3"]["wrong"]}</span>', size=28)}
{para("The same from Python, Java, JavaScript, Go and .NET: a wrong expectation raises NotConfirmed, saying what was heard.", size=32)}""",
        "heard.test.json asserts what was played; wrong.test.json expects what was not, and must fail, each test saying what it heard. Both are in the repository and run in under twenty seconds each.")))

    vrows = "".join(f'<tr><td style="padding:22px 28px; border-bottom:1px solid {RULE}">{v} of 15</td><td style="padding:22px 28px; border-bottom:1px solid {RULE}; font-family:{MONO}; color:{RED if vol[v] == "silence" else INK}">{vol[v]}</td></tr>' for v in (15, 5, 1, 0))
    out.append(("volume", section("volume", f"""{eyebrow("The volume")}
{h("What arrives follows the volume.", 76)}
  <table style="border-collapse:collapse; font-size:38px; width:900px"><thead><tr><th style="text-align:left; padding:18px 28px; font-family:{MONO}; font-size:24px; color:{DIM}; letter-spacing:2px; text-transform:uppercase; border-bottom:1px solid {RULE}">Media volume</th><th style="text-align:left; padding:18px 28px; font-family:{MONO}; font-size:24px; color:{DIM}; letter-spacing:2px; text-transform:uppercase; border-bottom:1px solid {RULE}">The same tone, heard at</th></tr></thead><tbody>{vrows}</tbody></table>
{para("So a test asserts pitch and length, never level — and every answer says the volume it was taken at: “at media volume 0 of 15, where nothing played as media is heard”.", size=32, width=1550)}""",
        "Act 4 of the demo sets the emulator's media volume and puts it back. A silent capture that says volume 0 is a test environment to fix, not an app to blame.")))

    out.append(("part3", part("part3", 3, "Interrupted", "A call, an alarm, a notification: what cut across the app, read from Android's own audio service.",
        "Part 3: the moment an app's audio is most likely to go wrong.")))

    out.append(("call-video", section("call-video", f"""  <div style="display:flex; gap:64px; align-items:center">
    <div style="flex:1; display:flex; flex-direction:column; gap:30px">
{eyebrow("Pixel 7 emulator · Android 15")}
{h("A call came in. Listen.", 76)}
{para("The tone plays; the emulator rings for five seconds; the tone comes back. The sound is what Mobium captured, laid under the screen recording.", size=32)}
{code('<span style="color:#5E6A76">$</span> mobium call ring\n<span style="color:#5E6A76">$</span> mobium call hang\n<span style="color:#5E6A76">$</span> mobium audio stop -o call.wav\n<span style="color:' + BRASS + '">interrupted: muted for a call 3.7–8.5s,\n  a ringtone played 3.9–8.6s</span>', size=26)}
    </div>
    <video controls preload="metadata" poster="deck/media/call-poster.jpg" src="deck/media/call-heard.mp4" style="height:740px; margin-top:40px; border:1px solid {RULE}; border-radius:18px; background:{WELL}"></video>
  </div>""",
        "Press play, sound on. The tone, then the ring, and no tone while it rings: Android silenced the app for the call and gave it back after. The app's own line said playing throughout. The screen recording and the capture were started together and aligned by the ring's first moment, 0.7 seconds apart.")))

    out.append(("call", section("call", f"""{eyebrow("The same, drawn")}
{h("The app never knew.", 76)}
{lanes(call)}
{code(f'<span style="color:{BRASS}">interrupted:</span> muted for a call {span(mute)}, a ringtone played {span(ring)}', size=28)}
{player("act5-call.m4a", "the capture")}""",
        "From the demo's act 5. The red lane is the app muted for the call, from Android's audio service; the amber lane the ringtone's own player. Between them the timeline holds the ring's pitches and no 440 Hz.")))

    out.append(("any", section("any", f"""{eyebrow("Any interruption")}
{h("Any sound that cuts across the app.", 76)}
  <div style="display:grid; gap:24px; width:1600px">
    {''.join(f'<div style="padding-left:30px; border-left:6px solid {RULE}"><p style="font-size:36px; font-weight:500">{a}</p><p style="font-size:30px; font-weight:300; color:{DIM}; margin-top:8px; line-height:1.4">{b}</p></div>' for a, b in [("The app muted", "for a call, or by the device's or its own volume — with Android's reason."), ("Another app's sound over it", "a ringtone, an alarm, a notification, a voice call, the assistant, navigation, another app's media — each named by what it is for."), ("A Clock timer's alarm over the tone", f"emulator: an alarm played {span(emu_alarm)} &nbsp;·&nbsp; Pixel 8 Pro: an alarm played {span(pix_alarm)}")])}
  </div>
{player("act5-alarm.m4a", "the alarm, heard")}""",
        "The alarm does not silence the Audio Demo, which asks for no audio focus: its tone plays on under the alarm's louder melody. An app that holds audio focus would pause itself; either way the interruption is reported. A touch's click is not an interruption.")))

    out.append(("part4", part("part4", 4, "On a real phone", "Nothing outside a phone hears what it plays. What interrupted the app, it can still tell.",
        "Part 4: the limits, and what is left when the sound is out of reach.")))

    out.append(("phone", section("phone", f"""{eyebrow("Pixel 8 Pro · Android 17")}
{h("A phone's sound stays on the phone.", 76)}
{code('<span style="color:#5E6A76">$</span> mobium audio start\nrecording what interrupts the app\'s audio — a phone\'s sound is not captured\n<span style="color:#5E6A76">$</span> mobium audio stop\n<span style="color:' + BRASS + '">interrupted: an alarm played ' + span(pix_alarm) + '</span>', size=28)}
  <div style="display:grid; gap:22px; width:1600px">
    {''.join(f'<div style="padding-left:30px; border-left:6px solid {RULE}"><p style="font-size:34px; font-weight:500">{a}</p><p style="font-size:28px; font-weight:300; color:{DIM}; margin-top:6px; line-height:1.4">{b}</p></div>' for a, b in [("Any Android phone adb reaches", "a device farm's included, with nothing installed on it."), ("A ring needs a call from outside", "which only a farm with a line can place. An emulator rings on demand.")])}
  </div>""",
        "Measured on a Pixel 8 Pro with the owner's permission. Capturing from the shell heard one app's own samples, but a call's mute is the player's own volume, which no such capture sees, and the system's ringtone is kept out of capture altogether. The audio service's log has both, so that is the answer on a phone.")))

    out.append(("limits", section("limits", f"""{eyebrow("What it cannot do")}
{h("Said, not approximated.", 76)}
  <div style="display:grid; gap:22px; width:1600px">
    {''.join(f'<div style="padding-left:30px; border-left:6px solid {RULE}"><p style="font-size:34px; font-weight:500">{a}</p><p style="font-size:28px; font-weight:300; color:{DIM}; margin-top:6px; line-height:1.4">{b}</p></div>' for a, b in [("iOS", "refused, saying why: a simulator's sound plays through the Mac, and an iPhone's stays on it."), ("A phone's sound", "not captured; its interruptions are."), ("Level", "follows the device's volume, so it is reported, not asserted."), ("The system's own sounds", "are in the capture: with touch sounds on, a tap is a tenth of a second of sound.")])}
  </div>""",
        "Each limit is a refusal with a reason, or a number in the answer, never a silent pass.")))

    out.append(("close", section("close", f"""{eyebrow("Try it")}
{h("Hear your app in a few minutes.", 84)}
{code('<span style="color:#5E6A76">$</span> go install github.com/mobiumdev/mobium/cmd/mobium@latest\n<span style="color:#5E6A76">$</span> mobium audio start\n<span style="color:#5E6A76">$</span> mobium audio stop -o heard.wav <span style="color:' + BRASS + '">--expect 440</span>', size=30)}
  <div style="display:grid; gap:18px; font-family:{MONO}; font-size:32px">
    <a href="https://github.com/mobiumdev/mobium" style="color:{INK}; text-decoration:none">github.com/mobiumdev/mobium</a>
    <a href="https://github.com/lana-20/mobium-audio-demo" style="color:{INK}; text-decoration:none">github.com/lana-20/mobium-audio-demo &nbsp;<span style="color:{DIM}; font-size:24px">quick start, tutorial, evidence</span></a>
    <a href="https://lana-20.github.io/mobium-audio-demo/carousel/" style="color:{INK}; text-decoration:none">lana-20.github.io/mobium-audio-demo/carousel &nbsp;<span style="color:{DIM}; font-size:24px">the ten-slide version</span></a>
  </div>""",
        "The quick start installs Mobium, builds MobiumApp and hears the Audio Demo in about ten minutes. Every output in it was run from scratch.")))
    return out


def main():
    built = slides()
    (DECK / "slides").mkdir(parents=True, exist_ok=True)
    for old in (DECK / "slides").glob("*.html"):
        old.unlink()
    for sid, html in built:
        (DECK / "slides" / f"{sid}.html").write_text(html)
    title = "Hear the App: Audio Testing with Mobium"
    (DECK / "deck.json").write_text(json.dumps({"title": title, "order": [s for s, _ in built]}, indent=2) + "\n")

    sections, notes = [], []
    for sid, html in built:
        a = re.search(r"<aside>(.*?)</aside>", html, re.S)
        notes.append(htmlmod.unescape(a.group(1)).strip() if a else "")
        sections.append(f'<div class="slide" data-id="{sid}">{html}</div>')
    page = TEMPLATE.format(title=htmlmod.escape(title), font_links=f'<link rel="stylesheet" href="{FONTS}">',
                           slides="\n".join(sections), notes=json.dumps(notes), count=len(built))
    (ROOT / "index.html").write_text(page)
    missing = [m for m in re.findall(r'(?:src|poster)="(deck/media/[^"]+)"', page) if not (ROOT / m).exists()]
    if missing:
        print("error: missing media: " + ", ".join(sorted(set(missing))), file=sys.stderr)
        return 1
    print(f"wrote index.html - {len(built)} slides")
    return 0

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{font_links}
<style>
  html, body {{ margin:0; height:100%; background:#0B0E11; overflow:hidden; }}
  body {{ font-family: Rubik, Arial, sans-serif; }}
  #stage {{ position:fixed; inset:0; overflow:hidden; }}
  .slide {{ position:absolute; inset:0; visibility:hidden; }}
  .slide.is-active {{ visibility:visible; }}
  /* The slide format assumes a border-box canvas with no default margins:
     padding sits INSIDE 1920x1080, and spacing comes from flex/grid gap only.
     Without this reset a section lays out at 2176x1368 and spills off-screen. */
  .slide > section, .slide > section * {{ box-sizing:border-box; margin:0; }}
  /* Centered by absolute positioning, not by grid: a 1920px item makes an auto
     grid track 1920px wide, so place-items centers inside the TRACK and the
     slide drifts off the viewport. translate(-50%,-50%) then scale is stable. */
  .slide > section {{
    position:absolute; left:50%; top:50%; width:1920px; height:1080px; overflow:hidden;
    transform-origin:center center; box-shadow:0 24px 80px rgba(0,0,0,.55);
  }}
  .slide > section > aside {{ display:none; }}
  #bar {{
    position:fixed; left:0; right:0; bottom:0; height:3px; background:rgba(255,255,255,.08);
  }}
  #bar > i {{ display:block; height:100%; background:#E0A526; width:0; transition:width .18s ease; }}
  #hud {{
    position:fixed; right:18px; bottom:16px; font-family:'Fira Code', ui-monospace, monospace;
    font-size:13px; color:#7C8890; letter-spacing:1px; user-select:none;
  }}
  #help {{
    position:fixed; left:18px; bottom:16px; font-family:'Fira Code', ui-monospace, monospace;
    font-size:12px; color:#4A545B; letter-spacing:.5px; user-select:none;
  }}
  #notes {{
    position:fixed; left:0; right:0; bottom:0; max-height:38vh; overflow:auto;
    background:#12181E; color:#C7D0D8; border-top:1px solid #26313A;
    padding:20px 26px 26px; font-size:16px; line-height:1.55; display:none;
  }}
  #notes.on {{ display:block; }}
  #notes b {{ display:block; color:#E0A526; font-family:'Fira Code', ui-monospace, monospace;
    font-size:12px; letter-spacing:1.5px; text-transform:uppercase; padding-bottom:6px; }}
  @media print {{
    html, body {{ background:#fff; overflow:visible; height:auto; }}
    #stage {{ position:static; display:block; }}
    #bar, #hud, #help, #notes {{ display:none !important; }}
    .slide {{ position:static; visibility:visible !important; page-break-after:always;
              display:block; width:1920px; height:1080px; }}
    .slide > section {{ box-shadow:none; transform:none !important;
                        position:relative; left:auto; top:auto; }}
    @page {{ size:1920px 1080px; margin:0; }}
  }}
</style>
</head>
<body>
<div id="stage">
{slides}
</div>
<div id="bar"><i></i></div>
<div id="hud"></div>
<div id="help">&larr; &rarr; move &nbsp;·&nbsp; S notes &nbsp;·&nbsp; F full screen</div>
<div id="notes"></div>
<script>
(function () {{
  var NOTES = {notes};
  var slides = Array.prototype.slice.call(document.querySelectorAll('.slide'));
  var hud = document.getElementById('hud');
  var bar = document.querySelector('#bar > i');
  var notesEl = document.getElementById('notes');
  var i = 0, showNotes = false;

  function fit() {{
    var s = Math.min(window.innerWidth / 1920, window.innerHeight / 1080);
    slides.forEach(function (el) {{
      el.firstElementChild.style.transform = 'translate(-50%, -50%) scale(' + s + ')';
    }});
  }}
  function render() {{
    slides.forEach(function (el, n) {{ el.classList.toggle('is-active', n === i); }});
    slides[i].querySelectorAll('video[autoplay]').forEach(function (m) {{ m.play().catch(function () {{}}); }});
    hud.textContent = (i + 1) + ' / ' + {count};
    bar.style.width = ((i + 1) / {count} * 100) + '%';
    notesEl.innerHTML = '';
    if (NOTES[i]) {{
      var b = document.createElement('b'); b.textContent = 'Speaker notes';
      var p = document.createElement('div'); p.textContent = NOTES[i];
      notesEl.appendChild(b); notesEl.appendChild(p);
    }}
    notesEl.classList.toggle('on', showNotes && !!NOTES[i]);
    if (location.hash.slice(1) !== String(i + 1)) {{
      history.replaceState(null, '', '#' + (i + 1));
    }}
  }}
  function go(n) {{
    // Leaving a slide stops what it was playing.
    slides[i].querySelectorAll('audio, video').forEach(function (m) {{ m.pause(); }});
    i = Math.max(0, Math.min({count} - 1, n)); render();
  }}

  document.addEventListener('keydown', function (e) {{
    if (e.key === 'ArrowRight' || e.key === 'PageDown' || e.key === ' ') {{ go(i + 1); e.preventDefault(); }}
    else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {{ go(i - 1); e.preventDefault(); }}
    else if (e.key === 'Home') {{ go(0); }}
    else if (e.key === 'End') {{ go({count} - 1); }}
    else if (e.key === 's' || e.key === 'S') {{ showNotes = !showNotes; render(); }}
    else if (e.key === 'f' || e.key === 'F') {{
      if (document.fullscreenElement) {{ document.exitFullscreen(); }}
      else {{ document.documentElement.requestFullscreen(); }}
    }}
  }});
  document.addEventListener('click', function (e) {{
    if (e.target.closest('#notes') || e.target.closest('a') || e.target.closest('audio') || e.target.closest('video')) {{ return; }}
    go(e.clientX < window.innerWidth * 0.25 ? i - 1 : i + 1);
  }});
  window.addEventListener('resize', fit);

  var start = parseInt(location.hash.slice(1), 10);
  if (start > 0 && start <= {count}) {{ i = start - 1; }}
  fit(); render();
}})();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    raise SystemExit(main())
