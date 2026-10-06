# Data format

Everything about an archive lives in `<archive>/_archive/archive.json` (UTF-8). The pages, file names and
subtitles are generated from it, so this file plus the recordings and `.html` transcripts are all you need to back up.

```json
{
 "title": "Kalasha documentation 2024",
 "profile": "linguistic_fieldwork",
 "transcribe": true,
 "transcription_language": "auto",
 "chapters_label": "",
 "project": { "project": "…", "languages_iso": ["kls"], "region": "Chitral" },
 "project_fields":   [ {"key": "project", "type": "text"}, … ],
 "recording_fields": [ {"key": "genre", "type": "select", "options": ["…"]}, … ],
 "categories": [ {"key": "languages", "label": "", "order": []}, … ],
 "recordings": [
  {
   "sha256": "…", "sha256_extra": ["…"],
   "file": "2024-03-03_Wordlist-body-parts_ZOOM0042.wav",
   "original": "ZOOM0042.wav",
   "duplicates": [],
   "duration_s": 312.4,
   "date": "2024-03-03", "date_approx": false,
   "title": "Wordlist body parts",
   "summary": "…",
   "tags": { "languages": ["Kalasha"], "genres": ["wordlist"] },
   "fields": { "session_id": "KLS-0003", "consent": "written", "access": "restricted" },
   "speakers": { "S00": "KLS-SP01" },
   "chapters": [[0, "Introduction"], [95, "Body parts"]],
   "note": ""
  }
 ]
}
```

| Key | Meaning |
|---|---|
| `transcribe` | `false` switches transcription off (e.g. soundscapes, languages Whisper does not know) |
| `transcription_language` | language code passed to noScribe, or `auto` |
| `categories[].label` | your own name for a tag category; empty = translated default |
| `categories[].order` | preferred order of values in the filter (e.g. family members) |
| `sha256` | identifies a recording independent of its name; `sha256_extra` holds e.g. the MP3 made from an AMR |
| `original` | first file name – kept forever, used as the key for imports |
| `date` | `YYYY`, `YYYY-MM` or `YYYY-MM-DD`; `date_approx` adds “ca” to the file name |
| `speakers` | noScribe speaker codes → names; written into the transcript and subtitles |
| `chapters` | `[seconds, title]`; shown as chapters or soundbites |

## Importing descriptions

`apply_metadata.py` merges a JSON file in the same shape (only what you want to change):

```json
{
 "title": "…",
 "project": { "region": "…" },
 "recordings": {
  "ZOOM0042.wav": { "title": "…", "tags": { "genres": ["wordlist"] }, "fields": { "consent": "written" } }
 }
}
```

The editor page saves exactly this format (`edits-*.json` in `_archive`); “3 Update archive” imports them.
Unknown fields, categories, malformed dates or chapters are rejected before anything is written.

## Files in the archive folder

| Path | Content |
|---|---|
| `<name>.mp3` / `.wav` … | recording |
| `<name>.html` | noScribe transcript (open and correct it in the noScribe editor) |
| `<name>.srt` | subtitles – VLC loads them automatically |
| `<overview>.html`, `<editor>.html` | generated pages (names depend on the language) |
| `_archive/archive.json` | the data above |
| `_archive/renames.csv` | log of all renames/moves (used by undo) |
| `_archive/transcription.log` | transcription log |
| `_archive/*.bat` | the batch files |
| `_duplicates/`, `_original_amr/`, `_empty_files/` | files put aside, never deleted |
