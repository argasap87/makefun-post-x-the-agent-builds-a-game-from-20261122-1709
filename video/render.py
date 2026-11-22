#!/usr/bin/env python3
"""Render video/pulse-path-x.mp4 for the PULSE-PATH make.fun entry.

Structure (34.0s, 1280x720, 10 fps):
  0.0-4.0s   the one prompt typing (slides/prompt.html, ?t= driven)
  4.0-14.0s  agent building — real game code streaming (slides/build.html)
 14.0-31.5s  REAL gameplay — game/index.html?demo=1&t=, one shot per 0.1s
 31.5-34.0s  make.fun referral end card (press pack, sha256-verified)
             over the frozen last gameplay frame (blurred + desaturated),
             fading in over 0.8s, referral code typed into its field.

Everything is captured from the real files in this repo with headless
Chromium; nothing is drawn by hand. Re-run:  python3 video/render.py
Requires: ffmpeg, headless Chromium (Playwright build in ~/.cache or
/opt/meta-chromium/chrome), video/card.webm (fetched + verified separately).
"""
import json
import os
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VIDEO = REPO / "video"
FRAMES = VIDEO / ".frames"
CHROME_CANDIDATES = [
    Path.home() / ".cache/ms-playwright/chromium_headless_shell-1255/chrome-headless-shell-linux64/chrome-headless-shell",
    Path.home() / ".cache/ms-playwright/chromium-1255/chrome-linux64/chrome",
    Path("/opt/meta-chromium/chrome"),
]
CARD_URL = "https://make.fun/press/referral-card/16x9/makefun-card-16x9-transparent.webm"
CARD_SHA256 = "84bca17df5ea3d8d96a28e354587bb72079b813e41a5268bb325b6c9ee307e29"
REFERRAL_CODE = "1ae1r9cj"
W, H, FPS = 1280, 720, 10

# segment lengths (seconds)
PROMPT_LEN, BUILD_LEN, GAME_LEN, CARD_LEN = 4.0, 10.0, 17.5, 2.5


def find_chrome():
    for c in CHROME_CANDIDATES:
        if c.exists():
            return str(c)
    raise SystemExit("no headless Chromium found")


def sh(cmd, **kw):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        print("FAILED:", cmd, file=sys.stderr)
        print(r.stdout[-2000:], r.stderr[-2000:], file=sys.stderr)
        raise SystemExit(1)
    return r.stdout


def shot(chrome, url, out, profile):
    cmd = [
        chrome, "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
        f"--user-data-dir={profile}", f"--window-size={W},{H}",
        f"--screenshot={out}", url,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    if not Path(out).exists():
        raise RuntimeError(f"screenshot failed for {url}: {r.stderr[-500:]}")


def main():
    chrome = find_chrome()
    print("chrome:", chrome)
    if not (VIDEO / "card.webm").exists():
        print("video/card.webm missing — fetch it first and verify sha256", file=sys.stderr)
        raise SystemExit(1)
    # verify card hash every render
    got = sh(f"sha256sum {VIDEO / 'card.webm'}").split()[0]
    assert got == CARD_SHA256, f"card sha256 mismatch: {got}"
    print("card sha256 OK")

    # ---- build slide: inject REAL lines from game/index.html ----
    lines = (REPO / "game/index.html").read_text().splitlines()
    code = [ln[:58].rstrip() for ln in lines[94:169] if ln.strip()][:70]
    build_html = (VIDEO / "slides/build.html").read_text()
    build_gen = FRAMES / "build_gen.html"
    FRAMES.mkdir(parents=True, exist_ok=True)
    build_gen.write_text(build_html.replace(
        "/*__CODE_LINES__*/[]", json.dumps(code)))

    # ---- screenshot jobs: (url, outfile) ----
    jobs = []
    for i in range(int(PROMPT_LEN * FPS)):
        t = i / FPS
        jobs.append((f"file://{VIDEO}/slides/prompt.html?t={t:.1f}",
                     FRAMES / "prompt" / f"f{i:04d}.png"))
    for i in range(int(BUILD_LEN * FPS)):
        t = i / FPS
        jobs.append((f"file://{build_gen}?t={t:.1f}",
                     FRAMES / "build" / f"f{i:04d}.png"))
    for i in range(int(GAME_LEN * FPS)):
        t = i / FPS
        jobs.append((f"file://{REPO}/game/index.html?demo=1&t={t:.1f}",
                     FRAMES / "game" / f"f{i:04d}.png"))
    for _, out in jobs:
        out.parent.mkdir(parents=True, exist_ok=True)
    expected = {FRAMES / "prompt": int(PROMPT_LEN * FPS),
                FRAMES / "build": int(BUILD_LEN * FPS),
                FRAMES / "game": int(GAME_LEN * FPS)}
    have_all = all(d.exists() and len(list(d.glob("f*.png"))) >= n
                   for d, n in expected.items())
    if have_all:
        print("frames already captured — skipping screenshots")
    else:
        print(f"{len(jobs)} screenshots…")

        def run(job):
            url, out = job
            profile = FRAMES / "profiles" / out.parent.name / out.stem
            shot(chrome, url, str(out), str(profile))
            return out.name

        with ThreadPoolExecutor(max_workers=6) as ex:
            done = list(ex.map(run, jobs))
        print(f"captured {len(done)} frames")
        shutil.rmtree(FRAMES / "profiles", ignore_errors=True)

    # ---- main body: prompt + build + gameplay ----
    sh(
        f"ffmpeg -v error -y -framerate {FPS} -i {FRAMES}/prompt/f%04d.png "
        f"-framerate {FPS} -i {FRAMES}/build/f%04d.png "
        f"-framerate {FPS} -i {FRAMES}/game/f%04d.png "
        f"-filter_complex '[0:v][1:v][2:v]concat=n=3:v=1:a=0[v]' -map '[v]' "
        f"-c:v libx264 -pix_fmt yuv420p -r {FPS} {VIDEO}/.main.mp4"
    )
    dur = float(sh(
        f"ffprobe -v error -show_entries format=duration -of csv=p=0 {VIDEO}/.main.mp4"))
    print(f"main body: {dur:.1f}s (expect 31.5)")
    assert abs(dur - 31.5) < 0.2, f"main body duration wrong: {dur}"

    # ---- end card over frozen last frame ----
    sh(f"ffmpeg -v error -y -sseof -0.05 -i {VIDEO}/.main.mp4 -frames:v 1 -update 1 {FRAMES}/last.png")
    font = VIDEO / "JetBrainsMono-Bold.ttf"
    if not font.exists():
        font = Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf")
    # field box in the 1920x1080 card, scaled to 720p: x=288 y=463 w=606 h=51;
    # font 62px at 1920 -> 41px at 720. Text left-aligned in the field,
    # vertically centred on it; fades in once the card is at rest (~1.2s).
    # List-form argv (no shell) so the drawtext expressions need no quoting.
    fc = (
        "[0:v]loop=loop=-1:size=1:start=0,trim=0:2.5,fps=10,"
        "gblur=sigma=28,eq=saturation=0.35[bg];"
        "[1:v]scale=1280:720,fps=10,format=rgba,"
        "fade=t=in:st=0:d=0.8:alpha=1[card];"
        "[bg][card]overlay=0:0,"
        "drawtext=fontfile=" + str(font) + ":text=" + REFERRAL_CODE + ":fontsize=41:"
        "fontcolor=#191419:x=308:y=463+(51-text_h)/2:"
        "alpha='if(gt(t,1.2),min(1,(t-1.2)/0.3),0)'[v]"
    )
    r = subprocess.run([
        "ffmpeg", "-v", "error", "-y",
        "-loop", "1", "-i", str(FRAMES / "last.png"),
        "-i", str(VIDEO / "card.webm"),
        "-filter_complex", fc, "-map", "[v]", "-t", str(CARD_LEN),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS),
        str(VIDEO / ".end.mp4"),
    ], capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-2000:], r.stderr[-2000:], file=sys.stderr)
        raise SystemExit(1)

    # ---- join + silent audio ----
    sh(
        f"ffmpeg -v error -y -i {VIDEO}/.main.mp4 -i {VIDEO}/.end.mp4 "
        f"-f lavfi -i anullsrc=r=48000:cl=stereo "
        f"-filter_complex '[0:v][1:v]concat=n=2:v=1:a=0[v]' -map '[v]' -map 2:a "
        f"-c:v libx264 -pix_fmt yuv420p -crf 20 -preset medium "
        f"-c:a aac -b:a 96k -shortest -movflags +faststart {VIDEO}/pulse-path-x.mp4"
    )
    for tmp in (".main.mp4", ".end.mp4"):
        os.remove(VIDEO / tmp)
    info = sh(
        f"ffprobe -v error -show_entries format=duration,size "
        f"-of default=noprint_wrappers=1 {VIDEO}/pulse-path-x.mp4")
    print(info)
    print("wrote", VIDEO / "pulse-path-x.mp4")


if __name__ == "__main__":
    main()
