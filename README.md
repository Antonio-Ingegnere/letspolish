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
audio: ""
nuance: Обычное слово «книга».
example: To jest dobra książka. — Это хорошая книга.
---
```

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

## Audio

Put pronunciation files into `media/` and reference them by filename:

```yaml
audio: ksiazka.mp3
```

When `audio` is empty, the two listening cards are not generated for that lexical note.

## Anki fields

Each lexical entry produces these fields:

- Word
- Translation
- IPA
- POS
- Gender
- Nuance
- Example
- Audio

The note model then derives all five training directions automatically.
