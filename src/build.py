"""Render every drawing once, make a contact sheet, and cut the video to the song.

    uv run src/build.py            # drawings + contact sheet + out/baby-shark.mp4
    uv run src/build.py --sheet    # drawings + contact sheet only
"""

import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
from paint import FONT_PATH  # noqa: E402
from scenes import SCENES  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
FRAMES = OUT / "frames"
SONG = ROOT / "reference" / "song.mp3"
DURATION = 136.057

# Start of each sung line (4 per section), from src/timing/onsets.py on the vocal stem;
# the few lines hidden inside continuous singing are interpolated at the 2.09 s line spacing.
LINES = {
    "baby": [27.95, 30.20, 32.29, 34.39],
    "mommy": [36.20, 38.53, 40.64, 42.70],
    "daddy": [44.67, 46.86, 48.97, 51.03],
    "grandma": [52.97, 55.24, 57.32, 59.41],
    "grandpa": [61.40, 63.59, 65.67, 67.76],
    "hunt": [69.63, 71.28, 73.37, 75.46],
    "run": [77.99, 79.56, 81.46, 83.37],
    "safe": [87.51, 89.37, 91.46, 93.55],
    "end": [95.60, 97.66, 99.74, 101.84],
    "outro": [108.23, 110.47, 112.56, 114.66],
}
LEAD = 0.05  # cut a hair before the syllable


def timeline():
    cuts = [(0.0, "title"), (5.55, "title_by_me"), (8.0, "ocean"), (12.2, "ocean_wet"),
            (17.55, "steve_intro"), (22.73, "steve_house")]
    for name, starts in LINES.items():
        if name == "outro":
            cuts.append((103.95, "save_dialog"))
        cuts += [(t - LEAD, f"{name}_{k + 1}") for k, t in enumerate(starts)]
    cuts += [(116.0, "card_1"), (122.5, "card_2"), (129.5, "card_3")]
    return cuts


def render():
    FRAMES.mkdir(parents=True, exist_ok=True)
    names = [n for _, n in timeline()]
    for n in names:
        print("drawing", n, flush=True)
        SCENES[n]().save(FRAMES / f"{n}.png")
    return names


def contact_sheet(names, cols=6, tw=320):
    th = tw * 9 // 16
    rows = (len(names) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (tw + 8) + 8, rows * (th + 30) + 8), (60, 60, 60))
    f = ImageFont.truetype(FONT_PATH, 14)
    for i, n in enumerate(names):
        im = Image.open(FRAMES / f"{n}.png").resize((tw, th), Image.LANCZOS)
        x, y = 8 + (i % cols) * (tw + 8), 8 + (i // cols) * (th + 30)
        sheet.paste(im, (x, y))
        ImageDraw.Draw(sheet).text((x, y + th + 4), n, fill=(255, 255, 255), font=f)
    sheet.save(OUT / "contact-sheet.png")


def video():
    cuts = timeline()
    lines = []
    for (t, n), nxt in zip(cuts, cuts[1:] + [(DURATION, None)]):
        lines += [f"file 'frames/{n}.png'", f"duration {nxt[0] - t:.3f}"]
    lines.append(f"file 'frames/{cuts[-1][1]}.png'")
    (OUT / "concat.txt").write_text("\n".join(lines) + "\n")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(OUT / "concat.txt"),
                    "-i", str(SONG), "-vf", "fps=30,format=yuv420p", "-c:v", "libx264", "-tune", "stillimage",
                    "-crf", "20", "-c:a", "aac", "-b:a", "192k", "-shortest", str(OUT / "baby-shark.mp4")],
                   check=True)
    (OUT / "timeline.txt").write_text("\n".join(f"{t:7.2f}  {n}" for t, n in cuts) + "\n")


if __name__ == "__main__":
    names = render()
    contact_sheet(names)
    if "--sheet" not in sys.argv:
        video()
