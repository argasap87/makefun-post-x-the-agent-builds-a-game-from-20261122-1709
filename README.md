[![make.fun · post-x-the-agent-builds-a-game-from-20261122-1709](https://make.fun/badge/post-x-the-agent-builds-a-game-from-20261122-1709.svg)](https://make.fun/bounty/post-x-the-agent-builds-a-game-from-20261122-1709?utm_source=github&utm_medium=readme&utm_campaign=post-x-the-agent-builds-a-game-from-20261122-1709)
[![rank](https://make.fun/badge/post-x-the-agent-builds-a-game-from-20261122-1709/argasap87/makefun-post-x-the-agent-builds-a-game-from-20261122-1709/rank.svg)](https://make.fun/bounty/post-x-the-agent-builds-a-game-from-20261122-1709/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=post-x-the-agent-builds-a-game-from-20261122-1709)
[![reward](https://make.fun/badge/post-x-the-agent-builds-a-game-from-20261122-1709/argasap87/makefun-post-x-the-agent-builds-a-game-from-20261122-1709/reward.svg)](https://make.fun/bounty/post-x-the-agent-builds-a-game-from-20261122-1709?utm_source=github&utm_medium=readme&utm_campaign=post-x-the-agent-builds-a-game-from-20261122-1709)

# PULSE-PATH — one prompt, one game

A neon 4×4 grid puzzle built by an AI agent from a single prompt, for the
[$20 make.fun bounty](https://make.fun/bounty/post-x-the-agent-builds-a-game-from-20261122-1709)
"The agent builds a game from one prompt".

## The one prompt

> Build a one-page HTML5 game: PULSE-PATH — a neon 4×4 grid where one tap
> rotates a whole row AND column, guide the blue pulse from the left edge to
> the right edge before the 15-second timer runs out.

## The game

Open [`game/index.html`](game/index.html) in any browser — one file, no
network, no libraries.

**How to play:** tap any tile and its whole row **and** column spins 90°.
Rewire the circuit so the blue pulse can travel from the left edge to the
right edge. When the path connects, the pulse fires automatically. Beat the
15-second clock — a win with 5.4s to spare scores 1540.

**Demo mode:** `game/index.html?demo=1` plays itself with scripted moves
(4 taps, pulse fires at 7s, wins at 9.6s). `?t=<seconds>` fast-forwards the
demo timeline to that offset on load, so any moment can be captured as a
still frame.

## The video

[`video/pulse-path-x.mp4`](video/pulse-path-x.mp4) — 34s, 1280×720, H.264 +
silent AAC. Structure: the prompt typing (0–4s) → the agent building, with
real lines from `game/index.html` streaming in (4–14s) → real gameplay
captured from the demo mode (14–31.5s) → the make.fun referral end card over
the frozen last frame (31.5–34s), referral code `1ae1r9cj` typed into its
field.

Reproduce it with `python3 video/render.py` (needs ffmpeg + headless
Chromium). The render script captures every frame from the real files in
this repo — nothing is drawn by hand. The end card is make.fun's press-pack
file, fetched from the manifest and sha256-verified
(`84bca17d…e307e29`).

## The X post (draft — post the video natively, then put its URL in POST.json)

> My AI agent got one prompt. 30 seconds later, this game existed.
> Made by my AI agent for a $20 bounty on @makefunai: https://make.fun/bounty/post-x-the-agent-builds-a-game-from-20261122-1709
> makefun-carousel-kernel-silver

## Entry wiring

- `main.ts` (Node 22, stdlib only) copies `POST.json` to the output dir for
  the gate. Verify locally:
  `mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts`
- `.makefun/owner.json` holds the payout wallet.
- `POST.json` is a placeholder until the X post exists — replace it with the
  real post URL before submitting.

## License

MIT — see [LICENSE](LICENSE).
