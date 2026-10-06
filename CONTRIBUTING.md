# Contributing

Thank you for helping! Issues and pull requests are welcome – in English or German.

## Ground rules

- **No recordings, transcripts or personal data** in issues, pull requests or test files. Use synthetic examples.
- Standard library only. The tools must keep running with a plain Python installation plus ffmpeg and noScribe.
- Code, comments and identifiers in English; everything users see goes through the locale files.

## Development

```bash
python -m unittest discover -s tests -v
```

The tests also check that all locale files have the same keys and placeholders and that every profile field
is translated.

## Adding a language

1. Copy `audio_archive/locales/en.json` to `audio_archive/locales/<code>.json` (e.g. `it.json`) and translate the values.
   Keep the `{placeholders}` unchanged.
2. Add the code to `test_all_languages_present` in `tests/test_tools.py`.
3. Optionally add `README.<code>.md` and link it in the language bar of every README.

## Adding or changing a profile

Profiles live in `audio_archive/profiles/<key>.json`:

```json
{
 "transcribe": true,
 "chapters_label": "soundbites",
 "project_fields":   [{"key": "project", "type": "text"}],
 "recording_fields": [{"key": "genre", "type": "select", "options": ["narrative", "conversation"]}],
 "categories":       [{"key": "speakers"}]
}
```

Field types: `text`, `textarea`, `date`, `list` (comma-separated), `select` (with `options`).
Every new field key, option and category needs a label in **all** locale files (`fields`, `options`, `categories`),
and a new profile needs `profiles.<key>` and `profiles.<key>_desc`. Register the profile in `PROFILES` in
`setup_archive.py`.
