"""Sets up a folder of recordings as an audio archive.

Creates <folder>/_archive/archive.json from a profile (asks for profile, title and transcription language)
and writes the batch files (named in the configured language) that call these tools.
Existing archive data is never overwritten - running it again only refreshes the batch files.

Usage:  python setup_archive.py <folder> [--profile KEY] [--title "Title"] [--transcription-language de]
"""
import argparse, json
from pathlib import Path
from common import PACKAGE, SETTINGS, t

PROFILES = ["family", "oral_history", "linguistic_fieldwork", "sociolinguistics", "soundscape", "journalism", "generic"]

HEADER = """@echo off
chcp 65001 >nul
set "AUDIO_ARCHIVE_DIR=%~dp0.."
set "PYTHONIOENCODING=utf-8"
set "T={tools}"
"""

# batch file -> commands; names come from the locale ("batch.<key>")
BATCHES = {
    "transcribe": ['python "%T%\\transcribe.py" %*', 'python "%T%\\register.py"'],
    "edit": ['python "%T%\\register.py"', 'python "%T%\\build_archive.py" --open-editor'],
    "update": ['python "%T%\\apply_metadata.py" --inbox', 'python "%T%\\register.py"',
               'python "%T%\\organize.py"', 'python "%T%\\build_archive.py" --open'],
    "subtitles": ['python "%T%\\transcribe.py" --srt'],
    "redo": ['python "%T%\\transcribe.py" --redo'],
    "export": ['python "%T%\\export_csv.py"'],
    "undo": ['python "%T%\\undo.py"'],
}


def ask(prompt, default=""):
    answer = input(f"{prompt} [{default}]: " if default else f"{prompt}: ").strip()
    return answer or default


def choose_profile():
    print(t("cli.choose_profile"))
    for i, key in enumerate(PROFILES, 1):
        print(f"  {i}  {t('profiles.' + key)} - {t('profiles.' + key + '_desc')}")
    while True:
        answer = ask(t("cli.profile_number"), "1")
        if answer.isdigit() and 1 <= int(answer) <= len(PROFILES):
            return PROFILES[int(answer) - 1]
        if answer in PROFILES:
            return answer


def new_archive(profile_key, title, language):
    profile = json.loads((PACKAGE / "profiles" / f"{profile_key}.json").read_text(encoding="utf-8"))
    return {
        "title": title,
        "profile": profile_key,
        "transcribe": profile.get("transcribe", True),
        "transcription_language": language,
        "chapters_label": profile.get("chapters_label", ""),
        "project": {},
        "project_fields": profile["project_fields"],
        "recording_fields": profile["recording_fields"],
        "categories": [{"key": c["key"], "label": "", "order": []} for c in profile["categories"]],
        "recordings": [],
    }


def write_batches(archive_dir):
    for old in archive_dir.glob("*.bat"):  # only our own (e.g. after switching the language), never user files
        if "AUDIO_ARCHIVE_DIR" in old.read_text(encoding="utf-8", errors="ignore"):
            old.unlink()
    for key, commands in BATCHES.items():
        body = HEADER.format(tools=PACKAGE) + "\n".join(commands) + "\necho.\npause\n"
        (archive_dir / f"{t('batch.' + key)}.bat").write_bytes(body.replace("\n", "\r\n").encode("utf-8"))


def setup(folder, profile=None, title=None, language=None):
    archive_dir = Path(folder).resolve() / "_archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    data_file = archive_dir / "archive.json"
    if not data_file.exists():
        profile = profile or choose_profile()
        title = title if title is not None else ask(t("cli.ask_title"), Path(folder).resolve().name)
        language = language or ask(t("cli.ask_transcription_language"),
                                   SETTINGS.get("transcription_language", "auto"))
        data = new_archive(profile, title, language)
        data_file.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    write_batches(archive_dir)
    print(t("cli.setup_done", dir=archive_dir))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folders", nargs="+")
    ap.add_argument("--profile", choices=PROFILES)
    ap.add_argument("--title")
    ap.add_argument("--transcription-language")
    a = ap.parse_args()
    for f in a.folders:
        setup(f, a.profile, a.title, a.transcription_language)
