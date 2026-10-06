"""Organises the archive folder according to _archive/archive.json:

- AMR recordings get an MP3 version (browsers cannot play AMR); the AMR original moves to _original_amr
- files with identical content move to _duplicates
- recording + .html + .srt are renamed:  YYYY-MM-DD_Short-title_ID.mp3
  (approximate dates get the suffix "ca", e.g. 2013-07-20ca_...; ID = recorder number such as M_EXT_22)
- speaker names from archive.json are written into the noScribe transcript and the subtitles

Every rename is logged in _archive/renames.csv (undo.py reverts them). Running it again is harmless.
"""
import csv, html, re, subprocess
from datetime import datetime
from common import (ROOT, ARCHIVE, SIDECARS, DUPLICATES_DIR, ORIGINAL_AMR_DIR, t, load, save, sha256,
                    html_to_srt)

RENAME_LOG = ARCHIVE / "renames.csv"
FORBIDDEN = re.compile(r'[\\/:*?"<>|]')


def log_rename(old, new):
    first = not RENAME_LOG.exists()
    with open(RENAME_LOG, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        if first:
            w.writerow(["time", "old", "new"])
        w.writerow([f"{datetime.now():%Y-%m-%d %H:%M:%S}", str(old.relative_to(ROOT)), str(new.relative_to(ROOT))])


def move(old, new):
    if old == new or not old.exists():
        return
    if new.exists() and new.resolve() != old.resolve():
        raise FileExistsError(t("cli.target_exists", name=new.name))
    new.parent.mkdir(exist_ok=True)
    old.rename(new)
    log_rename(old, new)


def recorder_id(name):
    """Keeps the recorder's own numbering in the new name so files stay traceable (M_EXT_22, 20150807_001, ...)."""
    m = re.search(r"([A-Z]+_(?:EXT|INT)_\d+|\d{8}_\d{3}|DS\d{3,}|ZOOM\d{3,}|R\d{2}_\d{4})", name)
    return m.group(1) if m else ""


def target_stem(rec):
    title = re.sub(r"\s+", "-", FORBIDDEN.sub("", rec["title"]).strip())
    date = rec["date"] + ("ca" if rec.get("date_approx") else "")
    return "_".join(p for p in [date, title, recorder_id(rec["original"])] if p)


def write_speakers(html_text, speakers):
    for code, name in (speakers or {}).items():
        html_text = re.sub(rf'(<a name="ts_\d+_\d+_{code}"\s*>)[^:<]{{1,40}}(: <span)',
                           lambda m: m[1] + html.escape(name) + m[2], html_text)
    return html_text


def main():
    data = load()
    for rec in data["recordings"]:
        audio = ROOT / rec["file"]
        if not audio.exists():
            print(t("cli.missing", name=rec["file"]))
            continue

        # 1. AMR -> MP3
        if audio.suffix.lower() == ".amr":
            mp3 = audio.with_suffix(".mp3")
            if not mp3.exists():
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(audio), "-ac", "1",
                                "-ar", "22050", "-b:a", "48k", str(mp3)], check=True)
            move(audio, ROOT / ORIGINAL_AMR_DIR / audio.name)
            rec.setdefault("sha256_extra", []).append(sha256(mp3))  # so register.py doesn't add the MP3 again
            audio = mp3
            rec["file"] = mp3.name

        # 2. put duplicates aside
        for d in rec.get("duplicates", []):
            move(ROOT / d, ROOT / DUPLICATES_DIR / d)

        # 3. rename (only once title and date are set)
        if rec.get("title") and rec.get("date"):
            target = audio.with_name(target_stem(rec) + audio.suffix.lower())
            if target != audio:
                for ext in SIDECARS:
                    move(audio.with_suffix(ext), target.with_suffix(ext))
                move(audio, target)
                audio = target
                rec["file"] = target.name

        # 4. update transcript (file reference, title, speaker names) and rebuild subtitles
        h = audio.with_suffix(".html")
        if h.exists():
            text = h.read_text(encoding="utf-8")
            # replacement functions instead of strings: Windows paths contain backslashes
            text = re.sub(r'(<meta name="audio_source" content=")[^"]*(")',
                          lambda m: m[1] + html.escape(str(audio)) + m[2], text)
            text = re.sub(r"((?:Audiodatei|Audio file|Fichier audio|Archivo de audio): )[^<]*(<br />)",
                          lambda m: m[1] + html.escape(audio.name) + m[2], text, count=1)
            text = re.sub(r'(<p style="font-weight: 600" >)[^<]*(</p>)',
                          lambda m: m[1] + html.escape(rec.get("title") or audio.stem) + m[2], text, count=1)
            text = write_speakers(text, rec.get("speakers"))
            h.write_text(text, encoding="utf-8")
            audio.with_suffix(".srt").write_text(html_to_srt(text), encoding="utf-8-sig")
    save(data)
    print(t("cli.organize_done"))


if __name__ == "__main__":
    main()
