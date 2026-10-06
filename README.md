# audio-archive-tools

**English** · [Deutsch](README.de.md) · [Français](README.fr.md) · [Español](README.es.md) · [日本語](README.ja.md) · [中文](README.zh-CN.md)

Turn a folder of audio recordings into a searchable, self-describing archive – **locally, without a server and without uploading anything**.

The tools transcribe recordings with [noScribe](https://github.com/kaixxx/noScribe) (Whisper + speaker detection),
create subtitles, give every file a date and a meaningful name, and build an offline overview page in which you can
filter, search the full text and jump straight to any sentence in a recording. A form page lets you describe the
project and each recording without touching a file by hand.

It started as a family archive of old voice-recorder and phone recordings and is designed to work just as well for:

| | |
|---|---|
| **Family / private** | home recordings, children's voices, conversations with grandparents |
| **Oral history** | biographical and witness interviews with consent, access and embargo |
| **Linguistic fieldwork** | sessions with ISO 639-3 languages, speakers, genre, stimulus, consent and access level (IMDI/ELAN style) |
| **Sociolinguistics** | interviews with social variables and interview modules (conversation, reading passage, word list, minimal pairs) |
| **Field recording / soundscape** | nature and environmental sound with place, coordinates, habitat, equipment – no transcription |
| **Journalism** | takes and soundbites for reports, features, vox pops, demonstrations, press conferences – with release status |

## Features

- **Batch transcription** with noScribe in headless mode – restartable at any time, identical files are transcribed
  once, automatic second attempt without speaker detection, optional retry with audio clean-up for difficult recordings
- **Subtitles (.srt)** next to every recording – VLC shows them automatically; long passages are split into sentences
- **Hallucination filter** for typical Whisper artefacts in silence or noise (broadcaster credits, endless loops)
- **Consistent file names**: `YYYY-MM-DD_Short-title_RecorderID.mp3` (estimated dates get `ca`), with an undo log
- **Overview page**: filters by year and by the archive's own tag categories, full-text search across all transcripts,
  built-in player, click a sentence to jump there, chapters or soundbites, project information
- **Editor page**: form for project details and every recording (date, title, summary, tags, profile fields,
  speaker names, chapters/soundbites) – changes are kept in the browser and saved as a file the tools import
- **Profiles** with field sets for the use cases above – freely adjustable per archive
- **CSV export** for spreadsheets, corpus tools or archive deposits
- **Six languages** for pages, messages and batch file names: English, German, French, Spanish, Japanese, Chinese
- Duplicates, AMR originals (converted to MP3 for browsers) and empty files are **moved aside, never deleted**
- Python standard library only – no packages to install

## How it works

```
 recordings ──▶ 1 Transcribe ──▶ 2 Describe (editor page or Claude) ──▶ 3 Update archive ──▶ overview page
                 noScribe .html      archive.json                        rename, subtitles,     filter · search ·
                 + .srt                                                  build pages            listen · jump
```

## Requirements

- Windows 10/11 (the batch files are for Windows; the Python scripts themselves are cross-platform)
- [Python](https://www.python.org/) 3.9 or newer
- [ffmpeg](https://ffmpeg.org/) on the `PATH` (e.g. `winget install ffmpeg` or `scoop install ffmpeg`)
- [noScribe](https://github.com/kaixxx/noScribe) 0.7 or newer (with command-line support).
  An NVIDIA GPU makes transcription much faster (about 10× real time on a GTX 1080 Ti), but is not required.

## Installation

1. Download or clone this repository, e.g. to `Documents\audio-archive-tools`.
2. Copy `settings.example.json` to `settings.json` and adjust it:

   ```json
   {
    "language": "en",
    "transcription_language": "auto",
    "noscribe_path": "C:/Program Files (x86)/noScribe/noScribe.exe",
    "model": "precise",
    "speaker_detection": "auto",
    "mark_pauses": "3sec+"
   }
   ```

   `language` is the language of pages, messages and batch files (`en`, `de`, `fr`, `es`, `ja`, `zh`).

## Quick start

1. **Back up** the folder with your recordings.
2. **Drag the folder onto `setup-archive.bat`.** Choose a profile, a title and the language of the recordings.
   A subfolder `_archive` with the batch files appears.
3. Run **`1 Transcribe`**. Every recording gets a `.html` transcript and a `.srt` subtitle file.
4. Run **`2 Describe recordings (editor)`**. Fill in the project details and describe the recordings, then save –
   the browser asks where to put the file: choose the `_archive` folder.
5. Run **`3 Update archive`**. Files are renamed and the overview page `Audio archive.html` opens.

New recordings later? Put them into the folder and run 1 → 2 → 3 again. Only new files are processed.

### Batch files in `_archive`

| Batch file | What it does |
|---|---|
| `1 Transcribe` | transcribes everything that has no transcript yet and registers new recordings |
| `2 Describe recordings (editor)` | builds and opens the editor page |
| `3 Update archive` | imports saved edits, renames files, rebuilds subtitles and pages |
| `Rebuild subtitles` | after correcting a transcript in the noScribe editor |
| `Re-transcribe a problem case` | retry one recording with noise reduction and loudness normalisation |
| `Export as CSV` | writes `<title>.csv` and `<title>_project.csv` |
| `Undo renaming` | reverts all logged renames and moves |

## Profiles

When you set up an archive you choose a profile; its fields and tag categories are copied into
`_archive/archive.json`, where you can rename, add or remove them. See [docs/profiles.md](docs/profiles.md) for the
fields of each profile and why they are there, and [docs/data-format.md](docs/data-format.md) for the file format.

## Describing recordings with Claude (optional)

Describing dozens of recordings is the part that takes time. With [Claude Code](https://claude.com/claude-code) you can
let Claude read the transcripts and fill in dates, titles, summaries, tags, speaker names and chapters. Copy
[`claude-skill/audio-archive`](claude-skill/audio-archive/SKILL.md) to `~/.claude/skills/`, adapt the two marked
sections, and say for example *"Describe the new recordings in my audio archive in D:\Fieldwork\2024"*.
`reading_view.py` and `apply_metadata.py` are the tools the skill uses – they work just as well for any other workflow.

## Privacy

Everything runs on your computer. noScribe transcribes locally, the pages are plain files that open from disk,
nothing is uploaded. The `.gitignore` of this repository excludes audio files, `_archive` folders and your
`settings.json`, so archive data cannot end up on GitHub by accident. If you use an AI assistant to describe
recordings, the transcripts are shared with that service – decide per archive whether that is acceptable,
particularly for research data with consent restrictions.

## Limitations

- Automatic transcripts are drafts. Children's speech, dialects, noisy or very quiet recordings come out poorly.
  Speaker detection does not know names; assigning them is part of describing.
- Whisper does not cover every language. For under-resourced languages set `"transcribe": false` and use the archive
  for metadata, listening and chapter marks.
- No IMDI/CMDI XML export yet – the CSV export is the bridge to archive deposits.

## Project structure

```
audio_archive/         Python tools (standard library only)
  locales/             en, de, fr, es, ja, zh
  profiles/            archive profiles
  template/            overview and editor pages
claude-skill/          optional Claude Code skill
docs/                  profiles and data format
tests/                 unit tests (python -m unittest discover -s tests)
setup-archive.bat      drag a folder onto it to set up an archive
settings.example.json  copy to settings.json
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) – new languages and profiles are especially welcome.

## License

[MIT](LICENSE)

## Acknowledgements

Transcription is done by [noScribe](https://github.com/kaixxx/noScribe) by Kai Dröge, which builds on
[faster-whisper](https://github.com/SYSTRAN/faster-whisper) and [pyannote](https://github.com/pyannote/pyannote-audio).
