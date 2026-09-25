Make a music video for `reference/song.mp3` (Pinkfong's "Baby Shark", 2:16) that looks like a bored teenager drew it in MS Paint with a mouse in 2010. Work autonomously; use any tools you need.

The lyrics barely give you anything: a shark family introduced one by one, then "let's go hunt", "run away", "safe at last", "it's the end". Invent the story. Transcribe the song with timestamps (e.g. whisper) so you know where each section falls, then write a short storyboard that gives every "doo doo doo" repeat something new to look at: the family's personalities, what they hunt, who they run from, what "safe at last" and "the end" turn out to mean. Deadpan and absurd beats cute. A running gag or a story that escalates across the repeats works better than a new random joke each time.

For the look, read `reference/style.md` and the four example drawings in `reference/frames/`, which come from an MS Paint video for a different song. Treat them as hints about the spirit, not a spec. The one firm rule: it must look half-assed. Resist making it polished, designed or pretty. Some approaches that tend to get there:

- Draw with simulated Paint tools rather than vector art: a thick brush fed by jittery, mouse-like stroke paths; perfect ellipses and rectangles for props; a real pixel flood fill for the bucket; a seeded spray can.
- Hard cuts timed to the song, mostly static slides. Reusing a drawing with a small change (a new speech bubble, one more shark) is in character.
- Keep every drawing deterministic (fixed seeds), render each once, and assemble the video with ffmpeg, muxing in the song.

Check your work: make a contact sheet of all drawings, look at it, and redo anything that looks too clean or too designed. Then pull stills at 10 random timestamps from the final video and confirm each matches that part of the song. Deliver `out/baby-shark.mp4`, the storyboard, and the source.
