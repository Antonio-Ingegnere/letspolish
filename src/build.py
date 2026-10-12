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
# Separate model for typed present-tense conjugation drills.
CONJUGATION_MODEL_ID = 1742031103
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

CONJUGATION_FIELDS = [
    {"name": "Infinitive"},
    {"name": "Translation"},
    {"name": "Person"},
    {"name": "Form"},
]

CONJUGATION_TEMPLATES = [
    {
        "name": "Present tense → type form",
        "qfmt": (
            '<div class="meta">Настоящее время · {{Person}}</div>'
            '<div class="word">{{Infinitive}}</div>'
            '<div class="translation">{{Translation}}</div>'
            '{{type:Form}}'
        ),
        "afmt": (
            '{{FrontSide}}<hr>'
            '<div class="word">{{Form}}</div>'
            '<div class="meta">{{Person}} · {{Infinitive}}</div>'
        ),
    },
]

CONJUGATION_MODEL = genanki.Model(
    CONJUGATION_MODEL_ID,
    "LetsPolish Present Conjugation v1",
    fields=CONJUGATION_FIELDS,
    templates=CONJUGATION_TEMPLATES,
    css=CSS,
)

PRESENT_PERSONS = [
    ("ja", "ja"),
    ("ty", "ty"),
    ("on_ona_ono", "on / ona / ono"),
    ("my", "my"),
    ("wy", "wy"),
    ("oni_one", "oni / one"),
]


def md_to_html(text: str | None) -> str:
    if not text:
        return ""
    return markdown.markdown(str(text), extensions=["extra", "sane_lists"])


def normalize_entry(raw: dict, source_body: str = "", source_file: str = "") -> dict:
    word = str(raw.get("word", "")).strip()
    translation = str(raw.get("translation", "")).strip()
    if not word or not translation:
        raise ValueError(f"Every entry needs word + translation ({source_file}): {raw!r}")

    audio_text = str(raw.get("audio_text", word) or word).strip()
    audio_name = str(raw.get("audio", "") or "").strip()
    audio_field = f"[sound:{audio_name}]" if audio_name else ""

    nuance = raw.get("nuance", "")
    example = raw.get("example", "")
    if source_body.strip() and not nuance and not example:
        nuance = source_body.strip()

    tags = raw.get("tags", []) or []
    if isinstance(tags, str):
        tags = [tags]

    present = raw.get("present", {}) or {}
    if present and not isinstance(present, dict):
        raise ValueError(f"present must be a mapping ({source_file}, {word!r})")

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
        "sources": raw.get("sources", []) or [],
        "present": {str(k): str(v).strip() for k, v in present.items()},
        "source_file": source_file,
    }


def load_entries() -> Iterable[dict]:
    seen: dict[str, str] = {}

    for path in sorted(WORDS_DIR.rglob("*.md")):
        post = frontmatter.load(path)
        raw_entries = post.metadata.get("entries")
        if raw_entries is None:
            raw_entries = [post.metadata]

        for raw in raw_entries or []:
            entry = normalize_entry(
                dict(raw),
                post.content if "entries" not in post.metadata else "",
                str(path.relative_to(ROOT)),
            )
            key = entry["word"].casefold()
            if key in seen:
                raise ValueError(
                    f"Duplicate canonical word {entry['word']!r}: "
                    f"{seen[key]} and {entry['source_file']}"
                )
            seen[key] = entry["source_file"]
            yield entry


def validate_present(entry: dict) -> None:
    present = entry["present"]
    if not present:
        return

    expected = {key for key, _ in PRESENT_PERSONS}
    actual = set(present)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise ValueError(
            f"Invalid present conjugation for {entry['word']!r}: "
            f"missing={missing}, extra={extra}"
        )

    empty = [key for key, _ in PRESENT_PERSONS if not present[key]]
    if empty:
        raise ValueError(f"Empty present forms for {entry['word']!r}: {empty}")


def main() -> None:
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    deck = genanki.Deck(DECK_ID, "Let's Polish::A1 Vocabulary")
    media_files: list[str] = []

    lexical_count = 0
    conjugation_count = 0
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
        lexical_count += 1

        validate_present(entry)
        if entry["present"]:
            for person_key, person_label in PRESENT_PERSONS:
                form = entry["present"][person_key]
                conjugation_note = genanki.Note(
                    model=CONJUGATION_MODEL,
                    fields=[
                        entry["word"],
                        entry["translation"],
                        person_label,
                        form,
                    ],
                    tags=entry["tags"] + ["grammar", "present_conjugation"],
                    guid=genanki.guid_for(
                        "pl-present-conjugation", entry["word"], person_key
                    ),
                )
                deck.add_note(conjugation_note)
                conjugation_count += 1

        if entry["audio_name"]:
            media_path = MEDIA_DIR / entry["audio_name"]
            if not media_path.exists():
                raise FileNotFoundError(f"Missing audio: {media_path}")
            media_files.append(str(media_path))

    output = DIST_DIR / "letspolish.apkg"
    package = genanki.Package(deck)
    package.media_files = media_files
    package.write_to_file(output)
    print(
        f"Built {lexical_count} lexical notes + "
        f"{conjugation_count} conjugation cards → {output}"
    )


if __name__ == "__main__":
    main()
