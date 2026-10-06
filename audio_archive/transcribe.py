"""Transcribes all recordings in the archive folder with noScribe (headless).

- Only recordings without <name>.html are processed -> safe to restart at any time.
- Files with identical content (same checksum) are transcribed once.
- Writes <name>.html (noScribe transcript, editable in the noScribe editor) and <name>.srt (subtitles, VLC
  loads them automatically).

Usage:  python transcribe.py [part-of-file-name ...]   (no arguments: all)
        python transcribe.py --srt                     (only rebuild subtitles from the HTML transcripts)
        python transcribe.py --redo [part-of-name ...] (retry problem cases with audio clean-up;
                                                        previous version is kept in _archive/tmp)
"""
import html, re, subprocess, sys, time
from datetime import datetime
from pathlib import Path
from common import (ROOT, ARCHIVE, AUDIO_EXT, SETTINGS as S, t, load, audio_files, sha256, duration,
                    html_to_srt)

TMP = ARCHIVE / "tmp"
LOG = ARCHIVE / "transcription.log"
NOSCRIBE = Path(S.get("noscribe_path", r"C:\Program Files (x86)\noScribe\noScribe.exe"))
ARCHIVE_INFO = load()
NOSCRIBE_ARGS = ["--no-gui",
                 "--language", ARCHIVE_INFO.get("transcription_language") or S.get("transcription_language", "auto"),
                 "--model", S.get("model", "precise"), "--speaker-detection", S.get("speaker_detection", "auto"),
                 "--timestamps", "--pause", S.get("mark_pauses", "3sec+")]


def log(msg):
    line = f"{datetime.now():%Y-%m-%d %H:%M:%S}  {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def run_noscribe(wav, out, args):
    return subprocess.run([str(NOSCRIBE), str(wav), str(out), *args],
                          capture_output=True, text=True, encoding="utf-8", errors="replace")


def transcribe(audio, clean_up=False):
    TMP.mkdir(parents=True, exist_ok=True)
    wav, out = TMP / "job.wav", TMP / "job.html"
    for p in (wav, out):
        p.unlink(missing_ok=True)
    # Convert first: avoids problems with non-ASCII paths, AMR input and damaged MP3 frames.
    # clean_up: remove rumble/hum and normalise loudness - helps when Whisper loops on quiet recordings.
    filters = ["-af", "highpass=f=100,afftdn,loudnorm"] if clean_up else []
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(audio), *filters, "-ac", "1", "-ar", "16000", str(wav)],
                   capture_output=True)
    if not wav.exists():
        raise RuntimeError(t("cli.ffmpeg_failed"))
    r = run_noscribe(wav, out, NOSCRIBE_ARGS)
    if not out.exists():
        # speaker detection fails on recordings with almost no speech -> second attempt without it
        i = NOSCRIBE_ARGS.index("--speaker-detection") + 1
        r = run_noscribe(wav, out, NOSCRIBE_ARGS[:i] + ["none"] + NOSCRIBE_ARGS[i + 1:])
    if not out.exists() and "completed successfully" in r.stdout:
        # noScribe reports success but writes nothing when it finds no speech at all -> placeholder transcript,
        # so the recording is not retried on every run
        out.write_text(f'<!DOCTYPE html><html><head><meta charset="UTF-8" /></head><body>'
                       f'<p style="font-weight: 600" >job</p><p>{html.escape(t("ui.no_text"))}</p></body></html>',
                       encoding="utf-8")
    if not out.exists():
        raise RuntimeError("noScribe: " + (r.stdout + r.stderr)[-600:])
    text = out.read_text(encoding="utf-8")
    # point the transcript to the real recording instead of the temporary WAV (the noScribe editor plays it)
    text = text.replace(str(wav), str(audio))
    text = re.sub(r'(<p style="font-weight: 600" >)job(</p>)', lambda m: m[1] + html.escape(audio.stem) + m[2],
                  text, count=1)
    audio.with_suffix(".html").write_text(text, encoding="utf-8")
    audio.with_suffix(".srt").write_text(html_to_srt(text), encoding="utf-8-sig")
    wav.unlink(missing_ok=True)
    out.unlink(missing_ok=True)


def main(name_filter, redo=False):
    if ARCHIVE_INFO.get("transcribe") is False:
        print(t("cli.transcription_off"))
        return
    TMP.mkdir(parents=True, exist_ok=True)
    files = audio_files()
    if name_filter:
        files = [p for p in files if any(f.lower() in p.name.lower() for f in name_filter)]
    groups = {}
    for p in files:
        groups.setdefault(sha256(p), []).append(p)

    jobs = []
    for group in groups.values():
        if not redo and any(p.with_suffix(".html").exists() for p in group):
            continue  # already transcribed (possibly under a duplicate's name)
        main_file = max(group, key=lambda p: len(p.name))  # most descriptive name
        seconds = duration(main_file)
        if seconds < 1:
            log(t("cli.skipped_empty", name=main_file.name))
            continue
        jobs.append((main_file, seconds))

    total = sum(s for _, s in jobs)
    log(t("cli.start", root=ROOT, n=len(jobs), hours=total / 3600))
    for i, (audio, seconds) in enumerate(jobs, 1):
        log(t("cli.item", i=i, n=len(jobs), name=audio.name, minutes=seconds / 60))
        t0 = time.time()
        try:
            if redo:  # keep the previous version in case the new one is worse
                for ext in (".html", ".srt"):
                    old = audio.with_suffix(ext)
                    if old.exists():
                        old.replace(TMP / (audio.stem + ".previous" + ext))
            transcribe(audio, clean_up=redo)
            log(t("cli.done", minutes=(time.time() - t0) / 60))
        except Exception as e:
            log(t("cli.error", msg=e))
    log(t("cli.end"))


def rebuild_subtitles():
    """Rebuild all SRT files from the (possibly corrected) HTML transcripts."""
    for h in sorted(ROOT.glob("*.html")):
        if not any(h.with_suffix(e).exists() for e in AUDIO_EXT):
            continue  # no matching recording (e.g. the archive overview page)
        h.with_suffix(".srt").write_text(html_to_srt(h.read_text(encoding="utf-8")), encoding="utf-8-sig")
        print(t("cli.subtitles", name=h.with_suffix(".srt").name))


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["--srt"]:
        rebuild_subtitles()
    elif args[:1] == ["--redo"]:
        names = args[1:] or [input(t("cli.ask_name")).strip()]
        if not any(names):
            sys.exit(t("cli.redo_needs_name"))
        main(names, redo=True)
    else:
        main(args)
