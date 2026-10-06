"""Registers new recordings in _archive/archive.json (identified by checksum).

- Files with identical content become one entry ("duplicates").
- Empty files (< 1 s) are moved to _empty_files.
- A date found in the file name is pre-filled (YYYY-MM-DD, YYYYMMDD, DD-MM-YYYY, YYYY-MM).
Title, summary, tags etc. stay empty and are filled in afterwards (by hand or via apply_metadata.py).
"""
import re
from common import ROOT, EMPTY_DIR, t, audio_files, sha256, duration, load, save


def date_from_name(name):
    if m := re.search(r"(20\d\d|19\d\d)-(\d\d)-(\d\d)", name):
        return f"{m[1]}-{m[2]}-{m[3]}"
    if m := re.search(r"(20\d\d|19\d\d)(\d\d)(\d\d)", name):
        return f"{m[1]}-{m[2]}-{m[3]}"
    if m := re.search(r"(\d\d)[-.](\d\d)[-.](20\d\d|19\d\d)", name):
        return f"{m[3]}-{m[2]}-{m[1]}"
    if m := re.search(r"(20\d\d|19\d\d)-(\d\d)", name):
        return f"{m[1]}-{m[2]}"
    return ""


def main():
    data = load()
    known = {h for r in data["recordings"] for h in [r["sha256"], *r.get("sha256_extra", [])]}
    groups = {}
    for p in audio_files():
        groups.setdefault(sha256(p), []).append(p)
    new = 0
    for h, group in groups.items():
        if h in known:
            continue
        main_file = max(group, key=lambda p: len(p.name))
        seconds = duration(main_file)
        if seconds < 1:
            (ROOT / EMPTY_DIR).mkdir(exist_ok=True)
            for p in group:
                p.rename(ROOT / EMPTY_DIR / p.name)
            print(t("cli.empty_moved", folder=EMPTY_DIR, names=", ".join(p.name for p in group)))
            continue
        data["recordings"].append({
            "sha256": h, "file": main_file.name, "original": main_file.name,
            "duplicates": [p.name for p in group if p != main_file],
            "duration_s": seconds, "date": date_from_name(main_file.name), "date_approx": False,
            "title": "", "summary": "", "tags": {}, "speakers": {}, "chapters": [], "note": "",
        })
        print(t("cli.new", name=main_file.name))
        new += 1
    save(data)
    pending = sum(1 for r in data["recordings"] if not r.get("title"))
    print(t("cli.register_summary", new=new, total=len(data["recordings"]), pending=pending))


if __name__ == "__main__":
    main()
