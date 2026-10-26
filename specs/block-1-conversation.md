# Fifth feature: the block's conversation is spoken

## Why

The basement's conversation is already spoken. On the basketball court (`block`) the crew's lines were still silent.

## What

- The five lines of `SCENES["block"]["dialogue"]` get their recordings (from the project author, "Audio Sources/Conversations/Hit the Block 1"), as `static/audio/voices/block/<number>_<speaker>.mp3`: `00_portals`, `01_needle`, `02_meyhem`, `03_bible`, `04_reekz`.
- They play like the basement's: Portals' line when the block appears, the next one on the click to the next bubble; the background sound is quieter while someone speaks.
- Listed in `static/audio/CREDITS.md`.

## Done when

1. Every line of the block conversation has its recording, numbered and named after its speaker.
2. Portals speaks when the block appears.
3. A scene without recordings (Rico's) stays silent.
