"""Builds the two pages in the archive folder from _archive/archive.json and the noScribe transcripts:
- the overview (e.g. "Audio archive.html"): browse, filter, search, listen, jump into transcripts
- the editor   (e.g. "Audio archive - edit.html"): form to describe the project and each recording
Both are self-contained files: no server and no internet connection needed.

Usage:  python build_archive.py [--open | --open-editor]
"""
import json, os, sys
from datetime import datetime
from common import ROOT, PACKAGE, LANGUAGE, LOCALE, _FALLBACK, t, load, segments, category_label


def section(name):
    return {**_FALLBACK.get(name, {}), **LOCALE.get(name, {})}


def described_fields(fields):
    """Field definitions with translated labels and option labels for the pages."""
    options = section("options")
    return [{**f, "label": f.get("label") or t("fields." + f["key"]),
             "options": [[o, options.get(o, o)] for o in f.get("options", [])]} for f in fields]


def meta(data):
    return {
        "title": data.get("title") or t("ui.default_title"),
        "profile": data.get("profile", ""),
        "project": data.get("project", {}),
        "project_fields": described_fields(data.get("project_fields", [])),
        "recording_fields": described_fields(data.get("recording_fields", [])),
        "categories": [{"key": c["key"], "label": category_label(c), "order": c.get("order", [])}
                       for c in data["categories"]],
        "chapters_label": t("ui." + data["chapters_label"]) if data.get("chapters_label") else t("ui.chapters"),
        "lang": LANGUAGE,
        "built": datetime.now().isoformat(timespec="minutes"),
        "ui": section("ui"),
        "editor": section("editor"),
    }


def recordings(data, full_transcript):
    out = []
    for rec in data["recordings"]:
        audio = ROOT / rec["file"]
        h, srt = audio.with_suffix(".html"), audio.with_suffix(".srt")
        seg = segments(h.read_text(encoding="utf-8")) if h.exists() else []
        item = {k: rec.get(k) for k in ("file", "original", "date", "date_approx", "title", "summary", "tags",
                                        "fields", "speakers", "chapters", "duration_s", "note")}
        item.update(html=h.name if h.exists() else None, srt=srt.name if srt.exists() else None)
        if full_transcript:
            item["seg"] = [[round(s[0] / 1000, 1), s[2], s[3]] for s in seg]
        else:  # the editor only needs a preview and the speaker codes
            item["preview"] = [[round(s[0] / 1000), s[2], s[3]] for s in seg[:40]]
            item["speaker_codes"] = sorted({s[2] for s in seg})
        out.append(item)
    return out


def render(template, payload, target):
    data = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    page = (PACKAGE / "template" / template).read_text(encoding="utf-8").replace("/*__DATA__*/null", data)
    target.write_text(page, encoding="utf-8")
    return target


def main(open_page=None):
    data = load()
    m = meta(data)
    overview = render("archive.html", {"meta": m, "recordings": recordings(data, True)}, ROOT / t("files.overview"))
    editor = render("editor.html", {"meta": m, "recordings": recordings(data, False)}, ROOT / t("files.editor"))
    print(t("cli.built", n=len(data["recordings"]), file=overview.name))
    print(t("cli.built_editor", file=editor.name))
    if open_page and hasattr(os, "startfile"):
        os.startfile(overview if open_page == "overview" else editor)


if __name__ == "__main__":
    main("overview" if "--open" in sys.argv else "editor" if "--open-editor" in sys.argv else None)
