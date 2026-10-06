# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versions follow [Semantic Versioning](https://semver.org/).

## [0.1.0] – 2026-10-06

First public version, developed while building a family audio archive of 71 recordings (2013–2016).

### Added
- Batch transcription with [noScribe](https://github.com/kaixxx/noScribe) (headless), restartable, duplicates transcribed once,
  automatic retry without speaker detection, placeholder transcript for recordings without speech
- Optional re-transcription with audio clean-up (high-pass, noise reduction, loudness normalisation) for problem cases
- Subtitles (.srt) from noScribe transcripts; long segments split by sentence; filters for Whisper hallucinations
  (broadcaster credits, endless loops, repeated sentences)
- `archive.json` data model with archive profiles: family, oral history, linguistic fieldwork, sociolinguistics,
  field recording / soundscape, journalism, generic
- Renaming to `YYYY-MM-DD_Title_RecorderID.ext`, duplicates and AMR originals moved aside, undo log
- Self-contained overview page (filters, full-text search, player, jump to sentence, chapters/soundbites)
- Self-contained editor page (project details, per-recording fields, tags, speakers, chapters) – no server
- CSV export of recordings and project metadata
- User interface, console messages and batch file names in English, German, French, Spanish, Japanese and Chinese
- Template for a Claude Code skill that describes recordings from their transcripts
