# HyperTTS setup for Let's Polish

The deck is generated with two audio-related fields:

- `AudioText` — plain Polish text to synthesize (defaults to `Word`)
- `Audio` — destination field where HyperTTS writes Anki sound markup such as `[sound:...mp3]`

The two listening card templates are intentionally conditional on `Audio`, so they appear only after audio has been generated.

## Recommended workflow

1. Build and import `dist/letspolish.apkg` into Anki.
2. Install **HyperTTS** in Anki Desktop.
3. Open the Browser and select notes from `Let's Polish::A1 Vocabulary`.
4. Run HyperTTS bulk audio generation.
5. Configure:
   - source field: `AudioText`
   - target field: `Audio`
   - language: Polish (`pl-PL`)
   - service/voice: choose the Google/Google Translate option available in your HyperTTS installation, or another Polish voice you prefer
6. Generate audio for the selected notes.
7. Sync Anki so generated media is available on mobile devices.

## Why AudioText exists separately

For most entries `AudioText == Word`, but keeping a dedicated source field lets us later synthesize a normalized form, phrase, or sentence without changing the spelling prompt shown on the card.

Example:

```yaml
- word: proszę
  translation: proszę; пожалуйста; прошу
  audio_text: proszę
```

Or later, for a phrase-oriented card:

```yaml
- word: dzień dobry
  translation: здравствуйте; добрый день
  audio_text: dzień dobry
```

## Pre-generated or curated recordings

The repository still supports committed audio files. Put the file under `media/` and set:

```yaml
audio: ksiazka.mp3
```

The builder will package the file and pre-fill `Audio`. HyperTTS is therefore optional per note.

## Re-generating audio

Because `AudioText` and `Audio` are separate fields, audio can be replaced in bulk without touching `Word`, `Translation`, IPA, examples, or note identity.
