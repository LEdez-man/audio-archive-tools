"""Reverts all renames/moves logged in _archive/renames.csv (newest first).
Note: archive.json is not reset - run register.py/organize.py again afterwards only if you want to redo them."""
import csv, sys
from common import ROOT, ARCHIVE, t

RENAME_LOG = ARCHIVE / "renames.csv"

if not RENAME_LOG.exists():
    sys.exit(t("cli.nothing_to_undo"))
if input(t("cli.undo_confirm")).strip().lower() not in ("y", "j", "o", "s", "yes", "ja", "oui", "si", "sí", "はい", "是"):
    sys.exit()
with open(RENAME_LOG, encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f, delimiter=";"))
for row in reversed(rows):
    new, old = ROOT / row["new"], ROOT / row["old"]
    if new.exists() and not old.exists():
        new.rename(old)
        print(f"{row['new']}  ->  {row['old']}")
RENAME_LOG.rename(RENAME_LOG.with_suffix(".undone.csv"))
