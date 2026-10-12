# Let's Polish

Markdown-first Polish vocabulary trainer for Anki.

One lexical note generates five vocabulary training cards:

1. Polish → Russian (recognition)
2. Polish → type Russian
3. Russian → type Polish
4. Polish audio → type Polish (dictation)
5. Polish audio → type Russian (listening comprehension)

Verb entries can also contain a `present` conjugation map. For such a verb the builder automatically adds six typed present-tense drills: `ja`, `ty`, `on/ona/ono`, `my`, `wy`, `oni/one`.

The build script generates an `.apkg` deck from Markdown files in `words/`.

## Vocabulary organization

Vocabulary is canonical and grouped semantically, not by textbook page or worksheet.

Current layout includes files such as:

```text
words/
├── verbs.md
├── nouns.md
├── adjectives.md
├── adverbs-function.md
├── numerals.md
├── pronouns.md
├── expressions.md
├── forms-of-address.md
└── geography.md
```

Rules:

- one Polish word/form has one canonical lexical entry;
- do not duplicate a word just because it appears in another lesson;
- `tags` describe level, part of speech, pronunciation drills and learning themes;
- `sources` records every worksheet/lesson where the word occurred;
- the builder rejects duplicate canonical words across files;
- nested folders are supported if we need more structure later.

Example:

```yaml
- word: cześć
  translation: привет; пока; честь
  ipa: /t͡ʂɛɕt͡ɕ/
  pos: expression
  tags: [a1, expression, greeting, farewell, pronunciation]
  sources: [alphabet_p8, t1_1b]
```

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

## Entry format

A semantic file contains an `entries` list in YAML front matter:

```md
---
entries:
  - word: książka
    translation: книга
    ipa: /ˈkɕɔ̃ʂka/
    pos: noun
    gender: f
    tags: [a1, noun]
    sources: [alphabet_p8]
    audio_text: książka
    audio: ""
    nuance: Обычное слово «книга».
    example: To jest dobra książka. — Это хорошая книга.
---
```

`audio_text` is optional; when omitted it defaults to `word`.

## Present-tense conjugation training

For verbs that should produce conjugation drills, add a complete `present` map:

```yaml
- word: mieszkać
  translation: жить; проживать
  ipa: /ˈmjɛʂkat͡ɕ/
  pos: verb
  tags: [a1, verb, conjugation_m_sz, present]
  present:
    ja: mieszkam
    ty: mieszkasz
    on_ona_ono: mieszka
    my: mieszkamy
    wy: mieszkacie
    oni_one: mieszkają
```

The builder validates that all six persons are present, then generates six additional typed cards such as:

```text
mieszkać · ja → [type: mieszkam]
mieszkać · oni / one → [type: mieszkają]
```

These cards use the separate `LetsPolish Present Conjugation v1` note model and receive the `grammar` and `present_conjugation` tags, so they can be filtered independently in Anki.

## Audio via HyperTTS

The generated vocabulary note model contains two dedicated fields:

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
   - voice/service: your preferred Polish provider
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

Each lexical entry produces these vocabulary fields:

- Word
- Translation
- IPA
- POS
- Gender
- Nuance
- Example
- AudioText
- Audio

The vocabulary note model derives all five vocabulary training directions automatically. Verb entries with `present` additionally generate the six conjugation cards described above.
