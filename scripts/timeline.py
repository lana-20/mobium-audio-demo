#!/usr/bin/env python3
"""Draws each capture's answer in a run as an SVG beside its JSON: the
timeline Mobium heard — sound in color by pitch, labeled, silence blank —
and under it what interrupted the app, each in its own row. Standard
library only.

    scripts/timeline.py evidence/<run> [...]
"""
import html
import json
import pathlib
import sys

W, LEFT, RIGHT = 960, 96, 24
ROW, GAP = 34, 10
INK, MUTED, RULE = "#1d2433", "#6b7385", "#d9dde5"
SOUND_NO_PITCH = "#9aa3b5"

TITLES = {
    "act1-silence": "Act 1 — silence that says it is playing",
    "act2-tone": "Act 2 — a tone",
    "act2-sequence": "Act 2 — 440 Hz, a pause, 880 Hz",
    "act4-volume-15": "Act 4 — the tone at media volume 15",
    "act4-volume-5": "Act 4 — the tone at media volume 5",
    "act4-volume-1": "Act 4 — the tone at media volume 1",
    "act4-volume-0": "Act 4 — the tone at media volume 0",
    "act5-call": "Act 5 — an incoming call over the tone",
    "act5-alarm": "Act 5 — a Clock timer's alarm over the tone",
}

KIND = {
    "muted": "muted",
    "ringtone": "ringtone",
    "alarm": "alarm",
    "notification": "notification",
    "voice_call": "voice call",
    "assistant": "assistant",
    "navigation": "navigation",
    "media": "other media",
    "sound": "other sound",
}


def color(hz):
    """A pitch's color: low warm, high cool, so 440 and 880 differ at a glance."""
    if not hz:
        return SOUND_NO_PITCH
    import math
    t = max(0.0, min(1.0, (math.log2(hz) - math.log2(200)) / (math.log2(1600) - math.log2(200))))
    hue = 20 + t * 200
    return f"hsl({hue:.0f}, 70%, 48%)"


def secs(ns):
    return ns / 1e9


def draw(answer, title):
    timeline = answer.get("timeline") or []
    cut = answer.get("interruptions") or []
    length = secs(answer.get("duration") or 0)
    if not length:
        ends = [secs(s["to"]) for s in timeline] + [secs(c["to"]) for c in cut]
        length = max(ends or [1.0])
    span = W - LEFT - RIGHT
    x = lambda t: LEFT + span * min(max(t, 0), length) / length
    rows = 1 if timeline else 0
    rows += len({c["kind"] for c in cut})
    h = 56 + max(rows, 1) * (ROW + GAP) + 34
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" '
           f'font-family="-apple-system, Helvetica, Arial, sans-serif">',
           f'<rect width="{W}" height="{h}" fill="#fff"/>',
           f'<text x="{LEFT}" y="28" font-size="16" font-weight="600" fill="{INK}">{html.escape(title)}</text>']
    y = 48
    if timeline:
        out.append(f'<text x="{LEFT - 10}" y="{y + ROW / 2 + 5}" font-size="13" text-anchor="end" fill="{MUTED}">heard</text>')
        out.append(f'<rect x="{LEFT}" y="{y}" width="{span}" height="{ROW}" fill="none" stroke="{RULE}"/>')
        for s in timeline:
            if not s["sound"]:
                continue
            a, b = x(secs(s["from"])), x(secs(s["to"]))
            hz = s.get("hz") or 0
            out.append(f'<rect x="{a:.1f}" y="{y}" width="{max(b - a, 1.5):.1f}" height="{ROW}" fill="{color(hz)}"/>')
            if b - a > 52:
                label = f"{hz:.0f} Hz" if hz else "sound"
                out.append(f'<text x="{(a + b) / 2:.1f}" y="{y + ROW / 2 + 5}" font-size="13" text-anchor="middle" '
                           f'fill="#fff" font-weight="600">{label}</text>')
        y += ROW + GAP
    elif not cut:
        out.append(f'<text x="{LEFT}" y="{y + ROW / 2 + 5}" font-size="13" fill="{MUTED}">nothing heard, nothing interrupted</text>')
        y += ROW + GAP
    for kind in dict.fromkeys(c["kind"] for c in cut):
        name = KIND.get(kind, kind)
        out.append(f'<text x="{LEFT - 10}" y="{y + ROW / 2 + 5}" font-size="13" text-anchor="end" fill="{MUTED}">{name}</text>')
        for c in cut:
            if c["kind"] != kind:
                continue
            a, b = x(secs(c["from"])), x(secs(c["to"]))
            fill = "#c43d3d" if kind == "muted" else "#e0a526"
            out.append(f'<rect x="{a:.1f}" y="{y + 6}" width="{max(b - a, 2):.1f}" height="{ROW - 12}" fill="{fill}" '
                       f'opacity="{0.55 if c.get("open") else 0.9}"/>')
        y += ROW + GAP
    # Seconds along the bottom.
    step = 1 if length <= 12 else 5 if length <= 60 else 10
    t = 0
    while t <= length + 1e-9:
        out.append(f'<line x1="{x(t):.1f}" y1="{y - GAP}" x2="{x(t):.1f}" y2="{y - GAP + 5}" stroke="{MUTED}"/>')
        out.append(f'<text x="{x(t):.1f}" y="{y + 12}" font-size="11" text-anchor="middle" fill="{MUTED}">{t:g}s</text>')
        t += step
    vols = {v["stream"]: v for v in answer.get("volumes") or []}
    if "media" in vols:
        m = vols["media"]
        out.append(f'<text x="{W - RIGHT}" y="28" font-size="12" text-anchor="end" fill="{MUTED}">'
                   f'media volume {m["index"]} of {m["max"]}{", muted" if m.get("muted") else ""}</text>')
    out.append("</svg>")
    return "\n".join(out)


def main(runs):
    n = 0
    for run in map(pathlib.Path, runs):
        for f in sorted(run.glob("*.json")):
            if f.name == "summary.json":
                continue
            try:
                answer = json.loads(f.read_text())
            except (ValueError, OSError):
                continue
            if not isinstance(answer, dict) or not ("timeline" in answer or "interruptions" in answer):
                continue
            f.with_suffix(".svg").write_text(draw(answer, TITLES.get(f.stem, f.stem)))
            n += 1
    print(f"drew {n} timelines")


main(sys.argv[1:])
