---
name: audio-archive
description: Build and maintain an audio archive with the audio-archive-tools - transcribe recordings with noScribe, describe them (date, title, summary, tags, fields, speakers, chapters) from their transcripts, rename them and build the offline overview page. Use when the user wants a folder of recordings transcribed, described, organised or added to an audio archive.
---

# Audio archive

<!-- Copy this folder to ~/.claude/skills/audio-archive/ and adjust the two sections marked ADAPT. -->

Tools: `<path to audio-archive-tools>` (ADAPT). Data format: `docs/data-format.md`; profiles: `docs/profiles.md`.

All scripts read the archive folder from `AUDIO_ARCHIVE_DIR`. From Bash:

```bash
T="<path to audio-archive-tools>/audio_archive"
AUDIO_ARCHIVE_DIR="<archive folder>" PYTHONIOENCODING=utf-8 python "$T/<script>.py" ...
```

## Workflow

1. **Set up** (if `_archive/archive.json` is missing): ask which profile fits, then
   `python "$T/setup_archive.py" "<folder>" --profile <key> --title "<title>" --transcription-language <code>`.
   Make sure the user has a backup – renaming and moving follow later.
2. **Transcribe**: run `transcribe.py` in the background (restartable), then `register.py`. Check
   `_archive/transcription.log` for errors.
3. **Read**: `reading_view.py` writes compact versions of all untitled recordings to `_archive/reading/`
   (short recordings line by line, long ones in 3-minute blocks).
4. **Describe**: write a JSON file in the shape documented in `apply_metadata.py` into the scratchpad and run
   `apply_metadata.py <file>`. It validates everything and lists what is still missing. Key = original file name.
5. **Organise and build**: `organize.py`, then `build_archive.py`. Open the overview page and check filters,
   search and playback.

## People and conventions (ADAPT)

- List the people, places or projects that recur in this archive, with the spelling to use in tags.

## Rules for describing recordings

- **Date** – sources in this order: spoken announcement in the recording > date in the file name > the
  recorder's numbering (IDs usually run chronologically) > content (age of a child, events, seasons).
  Estimated dates get `date_approx: true` and a reason in `note`. Name contradictions openly; file names can be wrong.
- **Title** – 2–6 words, about the content; it becomes part of the file name.
- **Summary** – 2–4 sentences, only what the transcript supports. Mark guesses as such. Name unintelligible
  passages instead of interpreting them.
- **Speakers** – assign `S00` → name only when certain (announcement, form of address, clear role such as
  interviewer). Otherwise leave the code. In research archives use speaker codes/pseudonyms as required.
- **Chapters / soundbites** – for recordings from ~10 minutes on: 5–15 entries with seconds from the reading view.
  In journalism archives mark quotable passages.
- **Tags** – reuse values already present in `archive.json`; check the categories defined there.
- **Fields** – fill the profile's recording fields only from evidence (transcript, file name, user information).
- **Sensitive content** – keep summaries factual; do not spread sensitive details about third parties.
- **Transcript quality** – Whisper hallucinates in noise (broadcaster credits, loops). The tools filter this for
  subtitles and pages. If a transcript is still broken (one sentence repeating for minutes), try
  `transcribe.py --redo "<name>"` (with audio clean-up) and keep the better version.

## Finish

Report: how many recordings are new, which dates are estimated, which transcripts stayed poor, and where the
overview page is.
