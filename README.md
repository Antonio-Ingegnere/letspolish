# Let's Polish

Markdown-first Polish vocabulary trainer for Anki.

One lexical note generates five training cards:

1. Polish → Russian (recognition)
2. Polish → type Russian
3. Russian → type Polish
4. Polish audio → type Polish (dictation)
5. Polish audio → type Russian (listening comprehension)

Each word lives in `words/*.md`. The build script generates an `.apkg` deck.

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

## Word format

```md
---
word: książka
translation: книга
ipa: /ˈkɕɔ̃ʂka/
pos: noun
gender: f
tags: [a1, vocabulary]
audio: ""
---

## Nuance
Обычное слово «книга».

## Example
To jest dobra książka. — Это хорошая книга.
```

If `audio` contains a filename such as `ksiazka.mp3`, the corresponding file must exist under `media/`. Audio cards are skipped when no audio is available.
