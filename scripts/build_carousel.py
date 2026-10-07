#!/usr/bin/env python3
"""Builds the LinkedIn carousel: ten 1080 x 1350 slides about Mobium's audio
capture, one per page when printed.

    python3 scripts/build_carousel.py [--fragment PATH]

Writes carousel/index.html (a whole page, for GitHub Pages) and, with
--fragment, the same slides without the document skeleton, for a host that
supplies its own. carousel/mobium-audio.pdf is printed from index.html by
headless Chrome. Every figure on a slide is read from the evidence when it
is built: the timelines are drawn from each capture's own answer.
"""
import argparse
import base64
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "carousel"
MEDIA = OUT / "media"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def data_uri(name):
    path = MEDIA / name
    kind = "image/png" if name.endswith(".png") else "image/jpeg"
    return f"data:{kind};base64,{base64.b64encode(path.read_bytes()).decode()}"


TITLE = "Hear the App: Mobium's Audio Capture"

STYLE = """
/* Layout: ten 4:5 slides, sized in container units so one design serves a
   phone screen, a desktop column and a 1080 x 1350 printed page. */
:root {
  --ink: #0E1426;        /* slide ground: the logo's own dark setting */
  --well: #0A0F1D;       /* code and screenshot wells */
  --rule: #253049;
  --paper: #EDEAE3;      /* text */
  --dim: #94A0AB;
  --brass: #E0A526;      /* the one accent */
  --go: #6FBF95;         /* current, passed */
  --stop: #E2735C;       /* stale, failed */
  --display: "Rubik", "Helvetica Neue", Arial, sans-serif;
  --mono: "Fira Code", "SF Mono", Menlo, Consolas, monospace;
  color-scheme: dark;
}
* { box-sizing: border-box; }
html, body { background: var(--ink); color: var(--paper); }
body { margin: 0; font-family: var(--display); padding-block: 24px 48px; padding-inline: 16px; }
.deck { display: grid; gap: 24px; justify-items: center; }
.slide {
  container-type: inline-size;
  width: min(540px, 100%);
  aspect-ratio: 4 / 5;
  background: var(--ink);
  border: 1px solid var(--rule);
  border-radius: 10px;
  overflow: hidden;
  position: relative;
}
.in {
  position: absolute; inset: 0;
  padding: 8cqw 8cqw 7cqw;
  display: flex; flex-direction: column; gap: 3.4cqw;
}
.top { display: flex; justify-content: space-between; align-items: center; }
.eyebrow { font-family: var(--mono); font-size: 2.3cqw; letter-spacing: 0.32cqw; text-transform: uppercase; color: var(--brass); }
.count { font-family: var(--mono); font-size: 2.1cqw; color: var(--dim); font-variant-numeric: tabular-nums; }
h1, h2 { margin: 0; font-weight: 600; letter-spacing: -0.15cqw; text-wrap: balance; }
h1 { font-size: 9.6cqw; line-height: 1.02; }
h2 { font-size: 6.6cqw; line-height: 1.08; }
p { margin: 0; font-size: 3.15cqw; line-height: 1.42; color: var(--paper); font-weight: 300; text-wrap: pretty; }
p.dim { color: var(--dim); }
b { font-weight: 600; }
.foot { margin-top: auto; display: flex; justify-content: space-between; align-items: flex-end; gap: 3cqw; }
.mark { width: 7cqw; height: 7cqw; object-fit: contain; }
.sig { font-family: var(--mono); font-size: 2.1cqw; color: var(--dim); text-align: right; line-height: 1.5; }
pre {
  margin: 0; background: var(--well); border: 1px solid var(--rule); border-radius: 1.6cqw;
  padding: 3cqw 3.4cqw; font-family: var(--mono); font-size: 2.55cqw; line-height: 1.6;
  color: #BDC6CE; white-space: pre-wrap; overflow-wrap: anywhere;
}
pre .p { color: #5E6A76; }
pre .c { color: #6E7A86; }
pre .k { color: var(--brass); }
pre .s { color: #9AD3B1; }
pre .go { color: var(--go); font-weight: 500; }
pre .stop { color: var(--stop); font-weight: 500; }
.verdict { font-family: var(--mono); font-size: 3.3cqw; }
.verdict .stop { color: var(--stop); } .verdict .go { color: var(--go); }
.shots { display: grid; grid-template-columns: 1fr 1fr; gap: 3cqw; min-height: 0; flex: 1; }
.shot { display: flex; flex-direction: column; gap: 1.4cqw; min-height: 0; }
.shot img { width: 100%; flex: 1; min-height: 0; object-fit: cover; object-position: top; border-radius: 1.6cqw; border: 1px solid var(--rule); background: #fff; }
.shot span { font-family: var(--mono); font-size: 2.2cqw; letter-spacing: 0.2cqw; text-transform: uppercase; }

/* 1: cover */
.cover h1 .late { color: var(--brass); }
.cover h1 { font-size: 8cqw; }
.cover .row { padding: 1.9cqw 3cqw; }
/* The logo: the glossy mark over the wordmark, left-aligned with the text. */
.logo { display: flex; flex-direction: column; align-items: center; gap: 1.4cqw; width: 24cqw; }
.logo .glyph { width: 100%; height: auto; display: block; }
.logo .word { width: 82%; height: auto; display: block; }
.cover .rows { display: grid; gap: 1.6cqw; margin-top: 2cqw; }
.cover .row { display: flex; justify-content: space-between; align-items: baseline; font-family: var(--mono); font-size: 3.2cqw; padding: 2.4cqw 3cqw; border-radius: 1.4cqw; background: var(--well); border: 1px solid var(--rule); }
.cover .row em { font-style: normal; font-size: 2.3cqw; color: var(--dim); }

/* 2: the four checks */
.checks { display: grid; grid-template-columns: 1fr 1fr; gap: 1.8cqw; }
.check { display: flex; justify-content: space-between; align-items: center; padding: 2.4cqw 3cqw; background: var(--well); border: 1px solid var(--rule); border-radius: 1.4cqw; font-family: var(--mono); font-size: 2.8cqw; }
.check b { color: var(--go); font-weight: 500; font-size: 2.3cqw; letter-spacing: 0.2cqw; text-transform: uppercase; }

/* timelines, drawn to scale from a capture's answer */
.tl { display: grid; gap: 2.2cqw; margin-block: 1cqw; }
.tl .seg { position: absolute; top: 0.9cqw; bottom: 0.9cqw; border-radius: 0.5cqw; display: flex; align-items: center; justify-content: center; font-size: 2.2cqw; color: var(--ink); font-weight: 600; white-space: nowrap; overflow: hidden; }
.shot1 { display: grid; grid-template-columns: 38% 1fr; gap: 4cqw; align-items: start; min-height: 0; flex: 1; }
.shot1 img { width: 100%; border-radius: 1.6cqw; border: 1px solid var(--rule); background: #fff; }
/* 3: the race, drawn to one time scale: 0 to 2.0 s across the track */
.race { display: grid; gap: 3cqw; margin-block: 3cqw; }
.lane { display: grid; grid-template-columns: 17cqw 1fr; align-items: center; gap: 2cqw; font-family: var(--mono); font-size: 2.2cqw; color: var(--dim); }
.track { position: relative; height: 8.5cqw; background: var(--well); border: 1px solid var(--rule); border-radius: 1cqw; }
.bar { position: absolute; top: 0.9cqw; bottom: 0.9cqw; border-radius: 0.6cqw; display: flex; align-items: center; padding-left: 1.6cqw; font-size: 2.4cqw; color: var(--ink); font-weight: 500; white-space: nowrap; overflow: hidden; }
.tick { position: absolute; top: -0.6cqw; bottom: -0.6cqw; width: 0.5cqw; border-radius: 0.3cqw; }
.axis { display: grid; grid-template-columns: 17cqw 1fr; gap: 2cqw; font-family: var(--mono); font-size: 1.9cqw; color: var(--dim); }
.axis .scale { display: flex; justify-content: space-between; }

/* 6: results */
table { border-collapse: collapse; width: 100%; font-size: 2.7cqw; }
th, td { text-align: left; padding: 2cqw 1.6cqw; border-bottom: 1px solid var(--rule); }
th { font-family: var(--mono); font-weight: 400; font-size: 2cqw; letter-spacing: 0.2cqw; text-transform: uppercase; color: var(--dim); }
td.n { font-family: var(--mono); font-variant-numeric: tabular-nums; white-space: nowrap; }
td.stop { color: var(--stop); } td.go { color: var(--go); }
tr:last-child td { border-bottom: 0; }

/* 7, 9: lists */
.list { display: grid; gap: 2.6cqw; }
.item { display: grid; grid-template-columns: 1fr; gap: 0.8cqw; padding-left: 3cqw; border-left: 0.5cqw solid var(--rule); }
.item b { font-size: 3.3cqw; font-weight: 500; }
.item span { font-size: 2.8cqw; font-weight: 300; color: var(--dim); line-height: 1.4; }

/* 10: call to action */
.cta .links { display: grid; gap: 1.6cqw; }
.cta pre { font-size: 2.3cqw; }
.cta .link { font-family: var(--mono); font-size: 2.9cqw; color: var(--paper); padding: 2cqw 3cqw; background: var(--well); border: 1px solid var(--rule); border-radius: 1.4cqw; display: grid; gap: 0.6cqw; }
.cta .link em { font-style: normal; font-size: 2.1cqw; color: var(--dim); letter-spacing: 0.15cqw; text-transform: uppercase; }
a { color: inherit; text-decoration: none; }
a:focus-visible { outline: 2px solid var(--brass); outline-offset: 2px; }

@page { size: 1080px 1350px; margin: 0; }
@media print {
  body { padding: 0; }
  .deck { display: block; }
  .slide { width: 1080px; border: 0; border-radius: 0; break-after: page; }
}
"""


EVIDENCE = ROOT / "evidence"
EMU = EVIDENCE / "2026-10-07-android-emulator"
PHONE = EVIDENCE / "2026-10-07-android-phone"


def answer(run, name):
    return json.loads((run / f"{name}.json").read_text())


def slide(n, eyebrow, body, extra=""):
    return f"""<section class="slide {extra}" aria-label="Slide {n} of 10">
  <div class="in">
    <div class="top"><span class="eyebrow">{eyebrow}</span><span class="count">{n:02d} / 10</span></div>
{body}
  </div>
</section>"""


def foot(right="mobium &middot; audio"):
    return f"""    <div class="foot"><span></span><span class="sig">{right}</span></div>"""


def tone_color(hz):
    if hz and abs(hz - 440) <= 9:
        return "var(--go)", "440 Hz"
    if hz and abs(hz - 880) <= 18:
        return "#8FB4E8", "880 Hz"
    return "#5E6A76", ""


def lanes(a, label_rows=True):
    """A capture's answer as lanes on one time scale: what was heard, then
    each kind of interruption, all from the answer itself."""
    length = a["duration"] / 1e9
    pct = lambda ns: f"{min(max(ns / 1e9, 0), length) / length * 100:.2f}%"
    heard = []
    for s in a["timeline"]:
        if not s["sound"]:
            continue
        color, name = tone_color(s.get("hz"))
        wide = (s["to"] - s["from"]) / 1e9 / length > 0.12
        heard.append(f'<div class="seg" style="left:{pct(s["from"])};width:calc({pct(s["to"] - s["from"])} + 1px);'
                     f'background:{color}">{name if wide else ""}</div>')
    rows = [f'<div class="lane"><span>heard</span><div class="track">{"".join(heard)}</div></div>']
    names = {"muted": ("muted", "var(--stop)"), "ringtone": ("ringtone", "var(--brass)"),
             "alarm": ("alarm", "var(--brass)")}
    for kind in dict.fromkeys(c["kind"] for c in a.get("interruptions") or []):
        name, color = names.get(kind, (kind, "var(--brass)"))
        bars = "".join(
            f'<div class="seg" style="left:{pct(c["from"])};width:{pct(c["to"] - c["from"])};background:{color}">'
            f'{"for the call" if c.get("reason") == "call" else ""}</div>'
            for c in a["interruptions"] if c["kind"] == kind and c["to"] - c["from"] >= 2.5e8)
        if bars:
            rows.append(f'<div class="lane"><span>{name}</span><div class="track">{bars}</div></div>')
    step = 2 if length > 6 else 1
    ticks = "".join(f"<span>{t} s</span>" for t in range(0, int(length) + 1, step))
    rows.append(f'<div class="axis"><span></span><div class="scale">{ticks}</div></div>')
    return '<div class="race tl">' + "".join(rows) + "</div>"


def slides():
    glyph, word = data_uri("mark3d.png"), data_uri("wordmark.png")
    silence_shot = data_uri("playing-silence.jpg")
    logo_html = lambda width: (f'<div class="logo" style="width:{width}cqw" role="img" aria-label="Mobium">'
                               f'<img class="glyph" src="{glyph}" alt=""><img class="word" src="{word}" alt=""></div>')
    seq, call, alarm = answer(EMU, "act2-sequence"), answer(EMU, "act5-call"), answer(EMU, "act5-alarm")
    phone = answer(PHONE, "act5-alarm")
    level = lambda v: [s for s in answer(EMU, f"act4-volume-{v}")["timeline"]
                       if s["sound"] and s["to"] - s["from"] > 3e8]
    vol = {v: (f"{level(v)[0]['level']:.0f} dBFS" if level(v) else "silence") for v in (15, 5, 1, 0)}
    mute = next(c for c in call["interruptions"] if c["kind"] == "muted")
    ring = next(c for c in call["interruptions"] if c["kind"] == "ringtone")
    emu_alarm = next(c for c in alarm["interruptions"] if c["kind"] == "alarm")
    pix_alarm = next(c for c in phone["interruptions"] if c["kind"] == "alarm")
    span = lambda c: f"{c['from'] / 1e9:.1f}&ndash;{c['to'] / 1e9:.1f} s"
    out = []

    out.append(slide(1, "Mobium &middot; audio", f"""    {logo_html(18)}
    <h1>The app said it was playing.<br><span class="late">Nothing was heard.</span></h1>
    <p>How to test what a mobile app plays: hear it, assert it, and see what cut across it. Measured on an Android emulator and a Pixel 8 Pro.</p>
    <div class="rows">
      <div class="row"><span>playing: silence for 2 s</span><em>the app</em></div>
      <div class="row"><span>state: <b style="color:var(--go)">started</b></span><em>Android</em></div>
      <div class="row"><span><b style="color:var(--stop)">silence throughout</b></span><em>the capture</em></div>
    </div>
{foot("swipe &rarr;")}""", "cover"))

    out.append(slide(2, "The problem", f"""    <h2>Everyone said it was playing.</h2>
    <div class="shot1">
      <img src="{silence_shot}" alt="MobiumApp's Audio Demo: playing: silence for 2 s (media)">
      <div style="display:grid;gap:3cqw">
        <p>MobiumApp's Audio Demo plays two seconds of zeros: a player that is started, and silent.</p>
        <p>The app's own line says <b>playing</b>. Android's audio service says the player is <b>started</b> &mdash; exactly what it says for a tone.</p>
        <p>Neither can tell you whether anything was heard. Only the sound can.</p>
      </div>
    </div>
{foot("Pixel 7 emulator, Android 15")}"""))

    out.append(slide(3, "Hear it", f"""    <h2>A timeline, not a waveform.</h2>
<pre><span class="p">$</span> mobium audio start
<span class="p">$</span> mobium tap testid=audioSequence
<span class="p">$</span> mobium audio stop -o sequence.wav</pre>
    {lanes(seq)}
    <p>Sound and silence to a tenth of a second, each sound's pitch and level, read from the emulator's own audio. Nothing is installed on the device.</p>
{foot("440 Hz, a second of silence, 880 Hz")}"""))

    out.append(slide(4, "Assert it", f"""    <h2>Pitch and length, in order.</h2>
<pre><span class="p">$</span> mobium audio stop -o seq.wav <span class="k">--expect 440:1.8-2.3,880:1.8-2.3</span>
<span class="go">saved seq.wav: &hellip; 440 Hz &hellip; 880 Hz &hellip;</span>

<span class="p">$</span> mobium audio stop -o tone.wav <span class="k">--expect 880</span>
<span class="stop">error: expected 880 Hz; heard 440 Hz for 2.1s
(0.3&ndash;2.4s) &mdash; the capture is saved at tone.wav</span></pre>
    <p>A wrong expectation fails, says what was heard, and keeps the capture as the evidence. <b>--expect silence</b> asserts nothing was heard; a tap's click, a tenth of a second, does not count.</p>
{foot()}"""))

    out.append(slide(5, "As a test", f"""    <h2>One step in a test file.</h2>
<pre>{{<span class="s">"audio"</span>: {{<span class="s">"action"</span>: <span class="s">"stop"</span>, <span class="s">"expect"</span>: [
  {{<span class="s">"hz"</span>: 440, <span class="s">"min_ms"</span>: 1800, <span class="s">"max_ms"</span>: 2300}},
  {{<span class="s">"hz"</span>: 880, <span class="s">"min_ms"</span>: 1800, <span class="s">"max_ms"</span>: 2300}}
]}}}}</pre>
<pre><span class="p">$</span> mobium test tests/heard.test.json
<span class="go">2 passed</span>
<span class="p">$</span> mobium test tests/wrong.test.json
<span class="stop">0 passed, 2 failed</span>   <span class="c"># each saying what was heard</span></pre>
    <p class="dim">The same from Python, Java, JavaScript, Go and .NET.</p>
{foot()}"""))

    out.append(slide(6, "The volume", f"""    <h2>What arrives follows the volume.</h2>
    <p>The same tone, at four media volumes:</p>
    <table>
      <thead><tr><th>Media volume</th><th>Heard at</th></tr></thead>
      <tbody>
        <tr><td>15 of 15</td><td class="n">{vol[15]}</td></tr>
        <tr><td>5 of 15</td><td class="n">{vol[5]}</td></tr>
        <tr><td>1 of 15</td><td class="n">{vol[1]}</td></tr>
        <tr><td>0 of 15</td><td class="n stop">{vol[0]}</td></tr>
      </tbody>
    </table>
    <p>So a test asserts pitch and length, never level &mdash; and every answer says the volume it was taken at: <b>&ldquo;at media volume 0 of 15, where nothing played as media is heard&rdquo;</b>.</p>
{foot()}"""))

    out.append(slide(7, "Interrupted", f"""    <h2>A call came in. The app never knew.</h2>
    {lanes(call)}
    <p>Android silenced the app for as long as the phone rang and gave it back after. The app said it was playing throughout. The answer says what happened:</p>
<pre><span class="k">interrupted:</span> muted for a call {span(mute).replace("&ndash;", "–")},
             a ringtone played {span(ring).replace("&ndash;", "–")}</pre>
{foot("mobium call ring &middot; mobium call hang")}"""))

    out.append(slide(8, "Any interruption", f"""    <h2>Any sound that cuts across the app.</h2>
    <div class="list">
      <div class="item"><b>The app muted</b><span>for a call, or by the device's or its own volume &mdash; with Android's reason.</span></div>
      <div class="item"><b>Another app's sound over it</b><span>a ringtone, an alarm, a notification, a voice call, the assistant, navigation, another app's media &mdash; each named by what it is for.</span></div>
      <div class="item"><b>A Clock timer's alarm over the tone</b><span>emulator: <b>an alarm played {span(emu_alarm)}</b><br>Pixel 8 Pro: <b>an alarm played {span(pix_alarm)}</b></span></div>
    </div>
    <p class="dim">Read from Android's audio service. A touch's click is not an interruption.</p>
{foot()}"""))

    out.append(slide(9, "On a real phone", f"""    <h2>A phone's sound stays on the phone.</h2>
    <p>Nothing outside a phone hears what it plays. On an Android phone a capture records what interrupted the app instead &mdash; the same answer, with nothing installed:</p>
<pre><span class="p">$</span> mobium audio stop
its sound is not captured on a phone;
<span class="k">interrupted:</span> an alarm played {span(pix_alarm).replace("&ndash;", "–")}</pre>
    <div class="list">
      <div class="item"><b>Any phone adb reaches</b><span>a device farm's included. Making one ring takes a call from outside, which only a farm with a line can place.</span></div>
      <div class="item"><b>An emulator hears everything</b><span>and rings on demand, with nothing else to set up.</span></div>
    </div>
{foot("Pixel 8 Pro, Android 17")}"""))

    out.append(slide(10, "Try it", f"""    {logo_html(16)}
    <h2>Hear your app in a few minutes.</h2>
<pre><span class="p">$</span> go install github.com/mobiumdev/mobium/cmd/mobium@latest
<span class="p">$</span> mobium audio start
<span class="p">$</span> mobium audio stop -o heard.wav <span class="k">--expect 440</span></pre>
    <div class="links">
      <a class="link" href="https://github.com/mobiumdev/mobium"><em>Mobium</em>github.com/mobiumdev/mobium</a>
      <a class="link" href="https://github.com/lana-20/mobium-audio-demo"><em>Quick start, tutorial, evidence</em>github.com/lana-20/mobium-audio-demo</a>
    </div>
{foot("Lana Begunova<br>mobile automation for AI agents and humans")}""", "cta"))
    return "\n".join(out)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fragment", help="also write the slides without the document skeleton here")
    args = ap.parse_args()
    fonts = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
             '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
             '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500&family=Rubik:wght@300;400;500;600&display=swap">')
    body = f'<main class="deck">\n{slides()}\n</main>'
    fragment = f"<title>{TITLE}</title>\n{fonts}\n<style>{STYLE}</style>\n{body}\n"
    page = ("<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
            f"{fragment.replace(body, '')}</head>\n<body>\n{body}\n</body>\n</html>\n")
    (OUT / "index.html").write_text(page)
    if args.fragment:
        pathlib.Path(args.fragment).write_text(fragment)
    pdf = OUT / "mobium-audio.pdf"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    "--virtual-time-budget=5000", f"--print-to-pdf={pdf}",
                    (OUT / "index.html").as_uri()], check=True, capture_output=True)
    print(f"carousel: {OUT / 'index.html'}, {pdf}")


if __name__ == "__main__":
    main()
