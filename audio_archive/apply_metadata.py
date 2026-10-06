"""Merges descriptions into _archive/archive.json.

Usage:  python apply_metadata.py file.json [file2.json ...]
        python apply_metadata.py --inbox      imports all _archive/edits*.json saved by the editor page,
                                              then renames them to *.applied.json

Format:
{
  "title":      "Archive title",                                          (optional)
  "project":    { "<project field key>": value, ... },                    (optional)
  "recordings": {
    "<original or current file name>": {
      "date":        "YYYY-MM-DD" | "YYYY-MM" | "YYYY",
      "date_approx": true if the date is only estimated,
      "title":       short title (becomes part of the file name),
      "summary":     2-4 sentences,
      "tags":        { "<category key>": ["value", ...] },
      "fields":      { "<recording field key>": value },
      "speakers":    { "S00": "Name" }        - only when the assignment is certain,
      "chapters":    [[seconds, "title"], ...] - chapters / soundbites,
      "note":        remarks, e.g. on dating or transcript quality
    }
  }
}
Keys not mentioned stay unchanged; "tags" and "fields" are merged per key.
"""
import json, re, sys
from common import ARCHIVE, t, load, save

FIELDS = {"date": str, "date_approx": bool, "title": str, "summary": str, "tags": dict, "fields": dict,
          "speakers": dict, "chapters": list, "note": str}


def check(name, values, data):
    categories = {c["key"] for c in data["categories"]}
    rec_fields = {f["key"] for f in data.get("recording_fields", [])}
    for key, value in values.items():
        if key not in FIELDS:
            raise ValueError(t("cli.unknown_field", name=name, field=key))
        if not isinstance(value, FIELDS[key]):
            raise ValueError(t("cli.wrong_type", name=name, field=key, type=FIELDS[key].__name__))
    if values.get("date") and not re.fullmatch(r"\d{4}(-\d\d(-\d\d)?)?", values["date"]):
        raise ValueError(t("cli.bad_date", name=name, date=values["date"]))
    for chapter in values.get("chapters", []):
        if not (isinstance(chapter, list) and len(chapter) == 2
                and isinstance(chapter[0], (int, float)) and isinstance(chapter[1], str)):
            raise ValueError(t("cli.bad_chapter", name=name, chapter=chapter))
    for cat, tags in values.get("tags", {}).items():
        if cat not in categories:
            raise ValueError(t("cli.unknown_category", name=name, category=cat, known=", ".join(sorted(categories))))
        if not (isinstance(tags, list) and all(isinstance(x, str) for x in tags)):
            raise ValueError(t("cli.wrong_type", name=name, field=f"tags.{cat}", type="list"))
    for key in values.get("fields", {}):
        if key not in rec_fields:
            raise ValueError(t("cli.unknown_recording_field", name=name, field=key, known=", ".join(sorted(rec_fields))))


def apply(update, data):
    if not {"recordings", "project", "title"} & update.keys():
        update = {"recordings": update}  # short form: { "<name>": {...} }
    index = {}
    for rec in data["recordings"]:
        index[rec["original"]] = rec
        index[rec["file"]] = rec
    recs = update.get("recordings", {})
    missing = [n for n in recs if n not in index]
    if missing:
        sys.exit(t("cli.not_found") + "\n  " + "\n  ".join(missing))
    for name, values in recs.items():
        try:
            check(name, values, data)
        except ValueError as e:
            sys.exit(str(e))  # nothing has been written yet
    if isinstance(update.get("title"), str):
        data["title"] = update["title"]
    data.setdefault("project", {}).update(update.get("project", {}))
    for name, values in recs.items():
        rec = index[name]
        values = dict(values)
        for merged in ("tags", "fields"):
            if merged in values:
                rec.setdefault(merged, {}).update(values.pop(merged))
        rec.update(values)
    return len(recs)


def main(paths):
    data = load()
    n = 0
    for p in paths:
        n += apply(json.loads(open(p, encoding="utf-8").read()), data)
    save(data)
    pending = [r["original"] for r in data["recordings"] if not r.get("title")]
    print(t("cli.applied", n=n, pending=len(pending)))
    for p in pending:
        print("  ", p)


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["--inbox"]:
        files = sorted(p for p in ARCHIVE.glob("edits*.json") if not p.name.endswith(".applied.json"))
        if files:
            main(files)
            for f in files:
                f.replace(f.with_name(f.stem + ".applied.json"))
    elif args:
        main(args)
    else:
        sys.exit(__doc__)
