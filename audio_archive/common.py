"""Shared foundation of the audio archive tools: paths, settings, translations, transcript cleaning, subtitles.

The archive folder (the folder holding the recordings) is taken from the environment variable
AUDIO_ARCHIVE_DIR, which the batch files in <archive>/_archive set. Without it, the current directory is used.
"""
import hashlib, html, json, os, re, subprocess
from collections import Counter
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
PACKAGE = Path(__file__).resolve().parent


def _load_settings():
    """settings.json (personal, git-ignored) or, as a fallback, settings.example.json."""
    for name in ("settings.json", "settings.example.json"):
        if (PROJECT / name).exists():
            return json.loads((PROJECT / name).read_text(encoding="utf-8"))
    return {}


SETTINGS = _load_settings()
LANGUAGE = os.environ.get("AUDIO_ARCHIVE_LANG") or SETTINGS.get("language", "en")


def _load_locale(lang):
    path = PACKAGE / "locales" / f"{lang}.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


_FALLBACK = _load_locale("en")
LOCALE = _load_locale(LANGUAGE)


def t(key, **kwargs):
    """Translated text for 'section.key' in the configured language (falls back to English)."""
    section, name = key.split(".", 1)
    text = LOCALE.get(section, {}).get(name) or _FALLBACK.get(section, {}).get(name) or key
    return text.format(**kwargs) if kwargs else text


ROOT = Path(os.environ.get("AUDIO_ARCHIVE_DIR") or Path.cwd()).resolve()
ARCHIVE = ROOT / "_archive"
DATA = ARCHIVE / "archive.json"
AUDIO_EXT = {".mp3", ".amr", ".m4a", ".wav", ".ogg", ".flac"}
SIDECARS = (".html", ".srt")  # companion files that are renamed together with the recording
DUPLICATES_DIR = "_duplicates"
EMPTY_DIR = "_empty_files"
ORIGINAL_AMR_DIR = "_original_amr"

# Typical Whisper hallucinations in silence/noise (broadcaster credits, subtitle credits, "thanks for watching")
PHANTOM = re.compile(r"Untertitel|Amara\.org|ZDF|WDR|SWR|fürs Zuschauen|Copyright|Abonnier|"
                     r"subtitles by|thanks for watching|sous-titr|subtítulos", re.I)


def audio_files():
    return sorted(p for p in ROOT.iterdir() if p.is_file() and p.suffix.lower() in AUDIO_EXT)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    try:
        return round(float(r.stdout.strip()), 1)
    except ValueError:
        return 0.0


def load():
    """archive.json: the archive's own description (title, description, transcribe, transcription_language,
    categories) plus the list of recordings."""
    data = json.loads(DATA.read_text(encoding="utf-8")) if DATA.exists() else {}
    data.setdefault("recordings", [])
    data.setdefault("categories", [])
    return data


def category_label(category):
    """Display name of a tag category: its own label, else the translated default for well-known keys."""
    return category.get("label") or t(f"categories.{category['key']}")


def save(data):
    data["recordings"].sort(key=lambda r: (r.get("date") or "9999", r["file"]))
    DATA.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")


# ---------- reading and cleaning transcripts ----------

def is_phantom(text, frequency):
    """Whisper invents text in noise/silence: broadcaster credits, endless loops, the same sentence over and over."""
    if PHANTOM.search(text):
        return True
    words = re.findall(r"\w+", text.lower())
    if len(words) >= 12 and len(set(words)) / len(words) < 0.3:
        return True  # "that is, uh, that is, uh, that is ..."
    return len(text) > 15 and frequency.get(text, 0) >= 4


def segments(html_text):
    """noScribe anchors <a name="ts_START_END_SPEAKER">text</a> -> cleaned list of
    (start_ms, end_ms, speaker, text). Speaker is the visible name (e.g. "Maria") if one was assigned,
    otherwise the code (S00). Pure pause markers and phantom texts are dropped."""
    raw, names = [], {}
    for start, end, spk, content in re.findall(
            r'<a name="ts_(\d+)_(\d+)_(\w+)"\s*>(.*?)</a>', html_text, re.S):
        text = html.unescape(re.sub(r"<[^>]+>", "", content))
        m = re.match(r"^\s*([^:\[\]]{1,40}):\s*(?=\[\d\d:\d\d:\d\d\])", text)  # "Name: [hh:mm:ss]"
        if m:
            names.setdefault(spk, m.group(1).strip())
            text = text[m.end():]
        text = re.sub(r"\[\d\d:\d\d:\d\d\]\s*", "", text).strip()
        text = re.sub(r"^//\s*", "", text)  # noScribe marker for overlapping speech
        raw.append((int(start), int(end), names.get(spk, spk), text))
    frequency = Counter(s[3] for s in raw)
    kept = [s for s in raw
            if s[3] and not re.fullmatch(r"\([^)]*\)", s[3]) and not is_phantom(s[3], frequency)]
    # shorten loops of short segments ("In... In... In...") to their first occurrences
    result = []
    for s in kept:
        run = 0
        for prev in reversed(result):
            if prev[3] != s[3]:
                break
            run += 1
        if run < 3:
            result.append(s)
    return result


# ---------- subtitles ----------

def srt_time(ms):
    s, ms = divmod(int(ms), 1000)
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def split_cue(start, end, text, max_ms=8000, max_chars=110):
    """Split long segments into sentences; times proportional to text length (approximation)."""
    if end - start <= max_ms and len(text) <= max_chars:
        return [(start, end, text)]
    pieces, current = [], ""
    for sentence in re.split(r"(?<=[.!?…。！？])\s*", text):
        if current and len(current) + len(sentence) > max_chars:
            pieces.append(current)
            current = sentence
        else:
            current = f"{current} {sentence}".strip()
    if current:
        pieces.append(current)
    total, pos, out = sum(len(p) for p in pieces), start, []
    for p in pieces:
        share = (end - start) * len(p) / total
        reading_time = 1500 + 70 * len(p)  # don't keep a cue on screen for minutes of silence
        out.append((int(pos), int(pos + min(share, reading_time)), p))
        pos += share
    return out


def html_to_srt(html_text):
    cues = []
    for start, end, spk, text in segments(html_text):
        for a, b, piece in split_cue(start, end, text):
            cues.append(f"{len(cues) + 1}\n{srt_time(a)} --> {srt_time(b)}\n{spk}: {piece}\n")
    return "\n".join(cues)
