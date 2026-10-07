from __future__ import annotations

from pathlib import Path
from typing import Iterable

import frontmatter
import genanki
import markdown

ROOT = Path(__file__).resolve().parents[1]
WORDS_DIR = ROOT / "words"
MEDIA_DIR = ROOT / "media"
DIST_DIR = ROOT / "dist"

# v2 adds AudioText as a dedicated HyperTTS source field.
MODEL_ID = 1742031102
DECK_ID = 2059400110

FIELDS = [
    {"name": "Word"},
    {"name": "Translation"},
    {"name": "IPA"},
    {"name": "POS"},
    {"name": "Gender"},
    {"name": "Nuance"},
    {"name": "Example"},
    {"name": "AudioText"},
    {"name": "Audio"},
]

CSS = r"""
.card {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-size: 26px;
  text-align: center;
  color: #222;
  background: #fff;
  padding: 24px;
}
.word { font-size: 40px; font-weight: 700; margin-bottom: 8px; }
.ipa { font-size: 20px; opacity: .65; margin-bottom: 18px; }
.translation { font-size: 30px; font-weight: 600; }
.meta { margin-top: 18px; font-size: 18px; opacity: .82; }
.example { margin-top: 14px; font-size: 20px; }
hr { border: 0; border-top: 1px solid #ddd; margin: 20px 0; }
input { font-size: 24px !important; text-align: center; }
"""

TEMPLATES = [
    {
        "name": "01 Polish → Russian",
        "qfmt": '<div class="word">{{Word}}</div><div class="ipa">{{IPA}}</div>',
        "afmt": '{{FrontSide}}<hr><div class="translation">{{Translation}}</div><div class="meta">{{Nuance}}</div><div class="example">{{Example}}</div>',
    },
    {
        "name": "02 Polish → type Russian",
        "qfmt": '<div class="word">{{Word}}</div><div class="ipa">{{IPA}}</div>{{type:Translation}}',
        "afmt": '{{FrontSide}}<hr><div class="translation">{{Translation}}</div><div class="meta">{{Nuance}}</div><div class="example">{{Example}}</div>',
    },
    {
        "name": "03 Russian → type Polish",
        "qfmt": '<div class="translation">{{Translation}}</div>{{type:Word}}',
        "afmt": '{{FrontSide}}<hr><div class="word">{{Word}}</div><div class="ipa">{{IPA}}</div><div class="meta">{{Nuance}}</div><div class="example">{{Example}}</div>',
    },
    {
        "name": "04 Audio → type Polish",
        "qfmt": '{{#Audio}}<div>{{Audio}}</div>{{type:Word}}{{/Audio}}',
        "afmt": '{{FrontSide}}<hr><div class="word">{{Word}}</div><div class="ipa">{{IPA}}</div><div class="translation">{{Translation}}</div>',
    },
    {
        "name": "05 Audio → type Russian",
        "qfmt": '{{#Audio}}<div>{{Audio}}</div>{{type:Translation}}{{/Audio}}',
        "afmt": '{{FrontSide}}<hr><div class="word">{{Word}}</div><div class="ipa">{{IPA}}</div><div class="translation">{{Translation}}</div>',
    },
]

MODEL = genanki.Model(
    MODEL_ID,
    "LetsPolish Vocabulary v2",
    fields=FIELDS,
    templates=TEMPLATES,
    css=CSS,
)


def md_to_html(text: str | None) -> str:
    if not text:
        return ""
    return markdown.markdown(str(text), extensions=["extra", "sane_lists"])


def normalize_entry(raw: dict, source_body: str = "") -> dict:
    word = str(raw.get("word", "")).strip()
    translation = str(raw.get("translation", "")).strip()
    if not word or not translation:
        raise ValueError(f"Every entry needs word + translation: {raw!r}")

    # AudioText is intentionally plain Polish text. HyperTTS uses it as the
    # source and writes generated [sound:...] markup into Audio inside Anki.
    audio_text = str(raw.get("audio_text", word) or word).strip()

    # Optional pre-generated audio remains supported. This lets us mix
    # HyperTTS-generated audio with hand-curated recordings later.
    audio_name = str(raw.get("audio", "") or "").strip()
    audio_field = f"[sound:{audio_name}]" if audio_name else ""

    nuance = raw.get("nuance", "")
    example = raw.get("example", "")

    # Single-entry files may keep richer prose in the Markdown body.
    if source_body.strip() and not nuance and not example:
        nuance = source_body.strip()

    tags = raw.get("tags", []) or []
    if isinstance(tags, str):
        tags = [tags]

    return {
        "word": word,
        "translation": translation,
        "ipa": str(raw.get("ipa", "") or ""),
        "pos": str(raw.get("pos", "") or ""),
        "gender": str(raw.get("gender", "") or ""),
        "nuance": md_to_html(nuance),
        "example": md_to_html(example),
        "audio_text": audio_text,
        "audio": audio_field,
        "audio_name": audio_name,
        "tags": [str(tag) for tag in tags],
    }


def load_entries() -> Iterable[dict]:
    for path in sorted(WORDS_DIR.glob("*.md")):
        post = frontmatter.load(path)
        if "entries" in post.metadata:
            for raw in post.metadata["entries"] or []:
                yield normalize_entry(dict(raw))
        else:
            yield normalize_entry(dict(post.metadata), post.content)


def main() -> None:
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    deck = genanki.Deck(DECK_ID, "Let's Polish::A1 Vocabulary")
    media_files: list[str] = []

    count = 0
    for entry in load_entries():
        note = genanki.Note(
            model=MODEL,
            fields=[
                entry["word"],
                entry["translation"],
                entry["ipa"],
                entry["pos"],
                entry["gender"],
                entry["nuance"],
                entry["example"],
                entry["audio_text"],
                entry["audio"],
            ],
            tags=entry["tags"],
            guid=genanki.guid_for("pl-ru", entry["word"], entry["translation"]),
        )
        deck.add_note(note)
        count += 1

        if entry["audio_name"]:
            media_path = MEDIA_DIR / entry["audio_name"]
            if not media_path.exists():
                raise FileNotFoundError(f"Missing audio: {media_path}")
            media_files.append(str(media_path))

    output = DIST_DIR / "letspolish.apkg"
    package = genanki.Package(deck)
    package.media_files = media_files
    package.write_to_file(output)
    print(f"Built {count} lexical notes → {output}")


if __name__ == "__main__":
    main()
