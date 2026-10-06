"""Exports the archive as CSV (one row per recording) for spreadsheets, ELAN/corpus projects or archive deposits.
Writes _archive/<title>.csv (UTF-8 with BOM, semicolon-separated so Excel opens it directly) and
_archive/<title>_project.csv with the project-level metadata."""
import csv, re
from common import ARCHIVE, t, load, category_label


def main():
    data = load()
    name = re.sub(r'[\\/:*?"<>|]', "", data.get("title") or "archive").strip() or "archive"
    fields = data.get("recording_fields", [])
    cats = data["categories"]
    header = (["file", "original", "date", "date_approx", "duration_s", "title", "summary"]
              + [t("fields." + f["key"]) for f in fields] + [category_label(c) for c in cats]
              + ["speaker_names", "chapters", "note"])
    rows = []
    for r in data["recordings"]:
        values = r.get("fields", {})
        rows.append([r["file"], r["original"], r.get("date", ""), r.get("date_approx", False), r.get("duration_s", ""),
                     r.get("title", ""), r.get("summary", "")]
                    + [", ".join(v) if isinstance(v := values.get(f["key"], ""), list) else v for f in fields]
                    + [", ".join(r.get("tags", {}).get(c["key"], [])) for c in cats]
                    + [", ".join(f"{k}={v}" for k, v in r.get("speakers", {}).items()),
                       " | ".join(f"{int(s) // 60}:{int(s) % 60:02} {title}" for s, title in r.get("chapters", [])),
                       r.get("note", "")])
    target = ARCHIVE / f"{name}.csv"
    with open(target, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(header)
        w.writerows(rows)
    project = ARCHIVE / f"{name}_project.csv"
    with open(project, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["field", "value"])
        w.writerow([t("editor.archive_title"), data.get("title", "")])
        for pf in data.get("project_fields", []):
            v = data.get("project", {}).get(pf["key"], "")
            w.writerow([t("fields." + pf["key"]), ", ".join(v) if isinstance(v, list) else v])
    print(t("cli.exported", file=target, n=len(rows)))


if __name__ == "__main__":
    main()
