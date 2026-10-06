"""Unit tests for the audio archive tools (standard library only: python -m unittest discover tests)."""
import json, sys, unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1] / "audio_archive"
sys.path.insert(0, str(PACKAGE))

import common  # noqa: E402
from register import date_from_name  # noqa: E402
from organize import recorder_id, target_stem, write_speakers  # noqa: E402

SAMPLE = (
    '<p><a name="ts_0_4000_S00" >S00: <span style="color: #78909C" >[00:00:00]</span> Heute ist der 16.07.2013.</a></p>'
    '<p><a name="ts_4000_9000_S01" >S01: <span style="color: #78909C" >[00:00:04]</span> Hallo.</a>'
    '<a name="ts_9000_12000_S01" > (.....)</a></p>'
    '<p><a name="ts_12000_15000_S00" >S00: <span>[00:00:12]</span> Untertitel im Auftrag des ZDF</a></p>'
)


class TranscriptCleaning(unittest.TestCase):
    def test_segments_drop_pauses_and_phantoms(self):
        seg = common.segments(SAMPLE)
        self.assertEqual([s[3] for s in seg], ["Heute ist der 16.07.2013.", "Hallo."])
        self.assertEqual(seg[0][:3], (0, 4000, "S00"))

    def test_assigned_speaker_name_is_used(self):
        named = write_speakers(SAMPLE, {"S00": "Maria"})
        self.assertEqual(common.segments(named)[0][2], "Maria")
        self.assertEqual(common.segments(named)[1][2], "S01")

    def test_loops_are_detected(self):
        self.assertTrue(common.is_phantom("das ist, äh, " * 8, {}))
        self.assertFalse(common.is_phantom("Das Kind lacht und erzählt etwas vom Kindergarten.", {}))
        self.assertTrue(common.is_phantom("Das ist nicht so einfach.", {"Das ist nicht so einfach.": 6}))

    def test_short_loops_are_shortened(self):
        html = "".join(f'<a name="ts_{i}000_{i + 1}000_S00" >In...</a>' for i in range(20))
        self.assertEqual(len(common.segments(html)), 3)


class Subtitles(unittest.TestCase):
    def test_srt_time(self):
        self.assertEqual(common.srt_time(3723456), "01:02:03,456")

    def test_long_segment_is_split_and_not_left_on_screen(self):
        text = "Erster Satz ist hier. " * 10
        cues = common.split_cue(0, 120000, text.strip())
        self.assertGreater(len(cues), 1)
        for start, end, piece in cues:
            self.assertLessEqual(len(piece), 130)
            self.assertLessEqual(end - start, 1500 + 70 * len(piece))

    def test_html_to_srt(self):
        srt = common.html_to_srt(SAMPLE)
        self.assertIn("00:00:00,000 --> 00:00:04,000\nS00: Heute ist der 16.07.2013.", srt)
        self.assertNotIn("ZDF", srt)


class Naming(unittest.TestCase):
    def test_date_from_name(self):
        self.assertEqual(date_from_name("2013-07-16 Ausflug an den See.MP3"), "2013-07-16")
        self.assertEqual(date_from_name("20150807_002 Interview.amr"), "2015-08-07")
        self.assertEqual(date_from_name("M_EXT_40 Besuch 22-11-2013.MP3"), "2013-11-22")
        self.assertEqual(date_from_name("2013-06 Atem.MP3"), "2013-06")
        self.assertEqual(date_from_name("M_EXT_02.MP3"), "")

    def test_recorder_id(self):
        self.assertEqual(recorder_id("M_EXT_22.MP3"), "M_EXT_22")
        self.assertEqual(recorder_id("20150807_001 Markt.amr"), "20150807_001")
        self.assertEqual(recorder_id("ZOOM0042.wav"), "ZOOM0042")

    def test_target_stem(self):
        rec = {"title": 'Emil: lacht / "laut"', "date": "2013-08", "date_approx": True, "original": "M_EXT_30.MP3"}
        self.assertEqual(target_stem(rec), "2013-08ca_Emil-lacht-laut_M_EXT_30")


class LocalesAndProfiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.locales = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in (PACKAGE / "locales").glob("*.json")}
        cls.profiles = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in (PACKAGE / "profiles").glob("*.json")}

    def test_all_languages_present(self):
        self.assertEqual(set(self.locales), {"en", "de", "fr", "es", "ja", "zh"})

    def test_locales_have_the_same_keys(self):
        ref = {(s, k) for s, d in self.locales["en"].items() for k in d}
        for lang, loc in self.locales.items():
            keys = {(s, k) for s, d in loc.items() for k in d}
            self.assertEqual(keys, ref, f"{lang}: missing {sorted(ref - keys)}, extra {sorted(keys - ref)}")

    def test_placeholders_match(self):
        import re
        for (section, key) in {(s, k) for s, d in self.locales["en"].items() for k in d}:
            expected = set(re.findall(r"\{(\w+)", self.locales["en"][section][key]))
            for lang, loc in self.locales.items():
                found = set(re.findall(r"\{(\w+)", loc[section][key]))
                self.assertEqual(found, expected, f"{lang}: {section}.{key}")

    def test_profiles_are_fully_translated(self):
        en = self.locales["en"]
        from setup_archive import PROFILES
        self.assertEqual(set(PROFILES), set(self.profiles))
        for name, prof in self.profiles.items():
            self.assertIn(name, en["profiles"])
            for f in prof["project_fields"] + prof["recording_fields"]:
                self.assertIn(f["key"], en["fields"], f"{name}: field {f['key']}")
                for o in f.get("options", []):
                    self.assertIn(o, en["options"], f"{name}: option {o}")
            for c in prof["categories"]:
                self.assertIn(c["key"], en["categories"], f"{name}: category {c['key']}")
            if prof.get("chapters_label"):
                self.assertIn(prof["chapters_label"], en["ui"])

    def test_templates_have_data_placeholder(self):
        for t in ("archive.html", "editor.html"):
            self.assertIn("/*__DATA__*/null", (PACKAGE / "template" / t).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
