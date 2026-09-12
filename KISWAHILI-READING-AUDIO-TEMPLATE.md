# Template ya audio ya Kiswahili

Template hii inarekebisha matamshi bila kubadilisha maandishi yanayoonekana kwenye kitabu.

## Kanuni

- `(i)` hadi `(xiii)`, pamoja na `i.` hadi `xiii.`, zinasomwa `moja` hadi `kumi na tatu`.
- `a.` hadi `h.` zinasomwa `aa, bee, chee, dee, ee, efu, gee, hee`.
- `Kifungu A` na `Kifungu B` zinasomwa `Kifungu aa` na `Kifungu bee`.
- Alama ya nafasi ya jibu `[[blank:...]]` inasomwa `dashi`.
- Maandishi ya HTML na `texts.json` hayaongezewi maneno haya; MP3 pekee ndiyo inabadilishwa.

## Matumizi

Dry-run ya kitabu kizima:

```powershell
python tools/generate_kiswahili_reading_audio.py
```

Dry-run yenye ripoti:

```powershell
python tools/generate_kiswahili_reading_audio.py --report MATRIX-READING-AUDIO-DRY-RUN.json
```

Rekebisha reader page moja, mfano page 72:

```powershell
python tools/generate_kiswahili_reading_audio.py --apply --reader-page 72
```

Rekebisha page kwa ID yake, mfano `pg070`:

```powershell
python tools/generate_kiswahili_reading_audio.py --apply --page-id pg070
```

Baada ya sample pages kuthibitishwa, rekebisha kitabu kizima:

```powershell
python tools/generate_kiswahili_reading_audio.py --apply --all --jobs 4 --report MATRIX-READING-AUDIO-FINAL.json
```

Script inahitaji package ya `edge-tts` na hutumia sauti `sw-TZ-RehemaNeural` kwa kasi `-5%`.
Manifest ya IDs zilizorekebishwa inaandikwa kwenye `assets/reading-audio-manifest.js`.

## Matokeo ya dry-run

- Audio candidates: 1,977
- Maandishi ya kawaida: 1,000
- Easy Read: 977
- Pages zenye marekebisho: 75
- Audio mappings zilizokosekana: 0
