"""Print vocal phrase onsets from the demucs vocal stem; build.py's LINES come from this.

    uvx --python 3.11 --with 'torchaudio<2.9' --with soundfile demucs --two-stems vocals -o out/sep reference/song.mp3
    uv run --with librosa src/timing/onsets.py out/sep/htdemucs/song/vocals.wav
"""

import sys

import librosa
import numpy as np

y, sr = librosa.load(sys.argv[1], sr=16000)
r = librosa.feature.rms(y=y, frame_length=640, hop_length=160)[0]
gap, starts = 0, []
for i, loud in enumerate(r > 0.06):
    if not loud:
        gap += 1
        continue
    if gap >= 4:  # at least 40 ms of quiet before it
        starts.append(round(i * 0.01, 2))
    gap = 0
print(" ".join(f"{s:.2f}" for s in starts))
