# Baby Shark, MS Paint edition

A one-shot prompt for Claude Code to make a half-assed MS Paint music video for
Pinkfong's [Baby Shark](https://www.youtube.com/watch?v=XqZsoesa55w), with a
story it invents because the lyrics barely have one.

- [`prompt.md`](prompt.md): the prompt.
- [`storyboard.md`](storyboard.md): the story Claude invented, with a drawing per sung line.
- [`src/`](src/): a fake MS Paint (`paint.py`), the cast (`characters.py`), every
  drawing (`scenes.py`) and the cut list (`build.py`).
- [`reference/style.md`](reference/style.md) and [`reference/frames/`](reference/frames/):
  style hints from [a 2010 MS Paint video for "Mi agüita amarilla"](https://www.youtube.com/watch?v=S0qt3w1Qo0g).

## Rebuilding the ignored media

```sh
yt-dlp -x --audio-format mp3 --audio-quality 2 -o "reference/song.%(ext)s" XqZsoesa55w
```

## Building the video

```sh
uv run src/build.py            # out/frames/, out/contact-sheet.png, out/baby-shark.mp4
uv run src/build.py --sheet    # drawings and contact sheet only
```

Needs `ffmpeg`. [`src/timing/onsets.py`](src/timing/onsets.py) explains how the
per-line cut times were measured.
