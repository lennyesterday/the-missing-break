# Seventh feature: Rico's conversation is spoken

## Why

The basement's and the block's conversations are spoken. In Rico's record shop (`record_shop`) the lines were still silent.

## What

- The seven lines of `SCENES["record_shop"]["dialogue"]` get their recordings (from the project author, "Audio Sources/Conversations/Ricos Record Shop"), as `static/audio/voices/record_shop/<number>_<speaker>.mp3`: `00_rico`, `01_needle`, `02_rico`, `03_portals`, `04_rico`, `05_meyhem`, `06_rico`.
- They play like the other conversations: Rico's first line when the crew comes in, the next one on the click to the next bubble; the background sound is quieter while someone speaks.
- Listed in `static/audio/CREDITS.md`.

## Done when

1. Every line of Rico's conversation has its recording, numbered and named after its speaker.
2. Rico speaks when the crew comes in.
3. A scene without recordings (the station) stays silent.
