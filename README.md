# Let's Polish

Markdown-first Polish vocabulary trainer for Anki.

One lexical note generates five training cards:

1. Polish → Russian (recognition)
2. Polish → type Russian
3. Russian → type Polish
4. Polish audio → type Polish (dictation)
5. Polish audio → type Russian (listening comprehension)

The build script generates an `.apkg` deck from Markdown files in `words/`.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/build.py
```

Output:

```text
dist/letspolish.apkg
```

## Source formats

### Single-word Markdown file

```md
---
word: książka
translation: книга
ipa: /ˈkɕɔ̃ʂka/
pos: noun
gender: f
tags: [a1, vocabulary]
audio_text: książka
audio: ""
nuance: Обычное слово «книга».
example: To jest dobra książka. — Это хорошая книга.
---
```

`audio_text` is optional; when omitted it defaults to `word`.

### Batch Markdown file

For lesson-sized batches, one Markdown file may contain many lexical entries in YAML front matter:

```md
---
entries:
  - word: książka
    translation: книга
    ipa: /ˈkɕɔ̃ʂka/
    pos: noun
    gender: f
    tags: [a1, vocabulary]
  - word: dziecko
    translation: ребёнок
    ipa: /ˈd͡ʑɛt͡skɔ/
    pos: noun
    gender: n
    tags: [a1, vocabulary]
---
```

This is the format currently used by `words/a1-current.md`.

## Audio via HyperTTS

The generated note model contains two dedicated fields:

- `AudioText` — Polish text that should be synthesized; defaults to `Word`
- `Audio` — generated Anki sound markup

Recommended workflow:

1. Build and import `dist/letspolish.apkg` into Anki.
2. Install HyperTTS.
3. Select the deck notes in Anki Browser.
4. Run HyperTTS bulk generation with:
   - source field: `AudioText`
   - target field: `Audio`
   - language: Polish (`pl-PL`)
   - voice/service: your preferred Polish provider (Google/Google Translate if available in your setup)
5. Sync Anki to copy generated media to mobile clients.

The two listening cards are conditional on `Audio`, so they become active once HyperTTS fills that field.

Detailed instructions: [`docs/hypertts.md`](docs/hypertts.md).

## Curated audio is also supported

If you later want to use a hand-picked recording instead of TTS, put the file into `media/` and reference it by filename:

```yaml
audio: ksiazka.mp3
```

The builder will package that file and pre-fill `Audio` for the note.

## Anki fields

Each lexical entry produces these fields:

- Word
- Translation
- IPA
- POS
- Gender
- Nuance
- Example
- AudioText
- Audio

The note model then derives all five training directions automatically.
