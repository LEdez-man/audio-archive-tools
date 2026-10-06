"""Compact reading versions of the transcripts for describing recordings -> _archive/reading/*.txt

Usage:  python reading_view.py          only recordings without a title
        python reading_view.py --all    all recordings
Short recordings (< 15 min) are listed segment by segment; long ones in 3-minute blocks (700 characters each),
so the course of a conversation and its chapters become visible without reading everything.
"""
import re, sys
from common import ROOT, ARCHIVE, t, load, segments

TARGET = ARCHIVE / "reading"


def clock(ms):
    s = int(ms // 1000)
    return f"{s // 3600}:{s % 3600 // 60:02}:{s % 60:02}" if s >= 3600 else f"{s // 60}:{s % 60:02}"


def main(everything):
    TARGET.mkdir(parents=True, exist_ok=True)
    for old in TARGET.glob("*.txt"):
        old.unlink()
    for nr, rec in enumerate(load()["recordings"]):
        if rec.get("title") and not everything:
            continue
        h = (ROOT / rec["file"]).with_suffix(".html")
        seg = segments(h.read_text(encoding="utf-8")) if h.exists() else []
        lines = [f"### {rec['file']} | original={rec['original']} | {rec['duration_s']:.0f}s | "
                 f"date_from_name={rec.get('date') or '-'} | {len(seg)} segments"]
        if not h.exists():
            lines.append(t("cli.no_transcript"))
        elif rec["duration_s"] < 900:
            lines += [f"{clock(s[0])} {s[2]}: {s[3]}" for s in seg]
        else:
            blocks = {}
            for s in seg:
                blocks.setdefault(s[0] // 180000, []).append(f"{s[2]}: {s[3]}")
            lines += [f"--- {clock(k * 180000)}: " + " | ".join(v)[:700] for k, v in sorted(blocks.items())]
        name = re.sub(r"[^\w\-]+", "_", rec["original"])[:60]
        (TARGET / f"{nr:03}_{name}.txt").write_text("\n".join(lines), encoding="utf-8")
        print(f"{nr:03}  {rec['duration_s'] / 60:6.1f} min  {len(seg):4} seg.  {rec['original']}")
    print(t("cli.reading_written", dir=TARGET))


if __name__ == "__main__":
    main("--all" in sys.argv)
