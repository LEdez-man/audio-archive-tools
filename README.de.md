# audio-archive-tools

[English](README.md) · **Deutsch** · [Français](README.fr.md) · [Español](README.es.md) · [日本語](README.ja.md) · [中文](README.zh-CN.md)

Aus einem Ordner mit Audioaufnahmen wird ein durchsuchbares, gut beschriebenes Archiv – **lokal, ohne Server, ohne Upload**.

Die Werkzeuge transkribieren Aufnahmen mit [noScribe](https://github.com/kaixxx/noScribe) (Whisper + Sprechererkennung),
erzeugen Untertitel, geben jeder Datei ein Datum und einen sprechenden Namen und bauen eine Offline-Übersicht, in der man
filtern, im Volltext suchen und direkt zu jedem Satz einer Aufnahme springen kann. Eine Eingabemaske nimmt Projektangaben
und die Beschreibung jeder Aufnahme auf, ohne dass man Dateien von Hand bearbeiten muss.

Entstanden ist das Projekt für ein Familienarchiv alter Diktiergeräte- und Handyaufnahmen. Es ist aber ebenso gedacht für:

| | |
|---|---|
| **Familie / privat** | Aufnahmen zu Hause, Kinderstimmen, Gespräche mit Großeltern |
| **Oral History** | biografische und Zeitzeugeninterviews mit Einverständnis, Zugang und Sperrfrist |
| **Linguistische Feldforschung** | Sessions mit Sprachen nach ISO 639-3, Sprecher:innen, Genre, Stimulus, Einverständnis und Zugangsstufe (wie bei IMDI/ELAN) |
| **Soziolinguistik** | Interviews mit sozialen Variablen und Interview-Modulen (freies Gespräch, Lesetext, Wortliste, Minimalpaare) |
| **Field Recording / Soundscape** | Natur- und Umweltklang mit Ort, Koordinaten, Habitat, Gerät – ohne Transkription |
| **Journalismus** | Takes und O-Töne für Reportage, Feature, Straßenumfrage, Demonstration, Pressekonferenz – mit Freigabestatus |

## Funktionen

- **Stapel-Transkription** mit noScribe ohne Oberfläche – jederzeit neu startbar, inhaltsgleiche Dateien werden nur
  einmal transkribiert, automatischer zweiter Versuch ohne Sprechererkennung, auf Wunsch Wiederholung mit
  Audio-Aufbereitung für schwierige Aufnahmen
- **Untertitel (.srt)** neben jeder Aufnahme – VLC zeigt sie automatisch; lange Passagen werden in Sätze aufgeteilt
- **Filter gegen Whisper-Halluzinationen** in Stille und Rauschen (Senderkennungen, Endlosschleifen)
- **Einheitliche Dateinamen**: `JJJJ-MM-TT_Kurzer-Titel_Gerätenummer.mp3` (geschätzte Daten mit `ca`), mit Protokoll zum Rückgängigmachen
- **Übersichtsseite**: Filter nach Jahr und nach den eigenen Schlagwort-Kategorien des Archivs, Volltextsuche über alle
  Transkripte, eingebauter Player, Klick auf einen Satz springt zur Stelle, Kapitel bzw. O-Töne, Projektangaben
- **Eingabemaske**: Formular für Projektangaben und jede Aufnahme (Datum, Titel, Zusammenfassung, Schlagworte,
  Profilfelder, Sprechernamen, Kapitel/O-Töne) – Änderungen bleiben im Browser erhalten und werden als Datei gespeichert,
  die die Werkzeuge übernehmen
- **Profile** mit passenden Feldern für die genannten Einsatzzwecke – pro Archiv frei anpassbar
- **CSV-Export** für Tabellenkalkulation, Korpuswerkzeuge oder Archiv-Depositen
- **Sechs Sprachen** für Seiten, Meldungen und Batch-Dateien: Deutsch, Englisch, Französisch, Spanisch, Japanisch, Chinesisch
- Duplikate, AMR-Originale (für Browser in MP3 umgewandelt) und leere Dateien werden **beiseitegelegt, nie gelöscht**
- Nur Python-Standardbibliothek – keine Pakete zu installieren

## Ablauf

```
 Aufnahmen ──▶ 1 Transkribieren ──▶ 2 Beschreiben (Eingabemaske oder Claude) ──▶ 3 Archiv aktualisieren ──▶ Übersicht
                noScribe .html        archive.json                                 umbenennen, Untertitel,     filtern · suchen ·
                + .srt                                                             Seiten bauen                hören · springen
```

## Voraussetzungen

- Windows 10/11 (die Batch-Dateien sind für Windows; die Python-Skripte selbst laufen überall)
- [Python](https://www.python.org/) ab 3.9
- [ffmpeg](https://ffmpeg.org/) im `PATH` (z. B. `winget install ffmpeg` oder `scoop install ffmpeg`)
- [noScribe](https://github.com/kaixxx/noScribe) ab 0.7 (mit Kommandozeilen-Unterstützung).
  Eine NVIDIA-Grafikkarte beschleunigt die Transkription stark (etwa 10-fache Echtzeit auf einer GTX 1080 Ti), ist aber nicht nötig.

## Installation

1. Repository herunterladen oder klonen, z. B. nach `Dokumente\audio-archive-tools`.
2. `settings.example.json` nach `settings.json` kopieren und anpassen:

   ```json
   {
    "language": "de",
    "transcription_language": "de",
    "noscribe_path": "C:/Program Files (x86)/noScribe/noScribe.exe",
    "model": "precise",
    "speaker_detection": "auto",
    "mark_pauses": "3sec+"
   }
   ```

   `language` ist die Sprache von Seiten, Meldungen und Batch-Dateien (`de`, `en`, `fr`, `es`, `ja`, `zh`).

## Schnellstart

1. **Sicherung** des Ordners mit den Aufnahmen anlegen.
2. **Den Ordner auf `setup-archive.bat` ziehen.** Profil, Titel und Sprache der Aufnahmen wählen.
   Es entsteht ein Unterordner `_archive` mit den Batch-Dateien.
3. **`1 Transkribieren`** starten. Jede Aufnahme bekommt ein `.html`-Transkript und eine `.srt`-Untertiteldatei.
4. **`2 Aufnahmen beschreiben (Eingabemaske)`** starten, Projektangaben ausfüllen, Aufnahmen beschreiben, speichern –
   der Browser fragt nach dem Speicherort: den Ordner `_archive` wählen.
5. **`3 Archiv aktualisieren`** starten. Die Dateien werden umbenannt, die Übersicht `Audioarchiv.html` öffnet sich.

Später neue Aufnahmen? In den Ordner legen und 1 → 2 → 3 wiederholen. Bearbeitet werden nur die neuen Dateien.

### Batch-Dateien in `_archive`

| Batch-Datei | Was sie tut |
|---|---|
| `1 Transkribieren` | transkribiert alles ohne Transkript und nimmt neue Aufnahmen auf |
| `2 Aufnahmen beschreiben (Eingabemaske)` | baut die Eingabemaske und öffnet sie |
| `3 Archiv aktualisieren` | übernimmt gespeicherte Eingaben, benennt um, erzeugt Untertitel und Seiten neu |
| `Untertitel neu erzeugen` | nach Korrekturen im noScribe-Editor |
| `Problemfall neu transkribieren` | eine Aufnahme mit Rauschfilter und Lautstärke-Angleichung erneut transkribieren |
| `Als CSV exportieren` | schreibt `<Titel>.csv` und `<Titel>_project.csv` |
| `Umbenennungen rückgängig machen` | dreht alle protokollierten Umbenennungen und Verschiebungen zurück |

## Profile

Beim Einrichten wählt man ein Profil; dessen Felder und Schlagwort-Kategorien werden nach `_archive/archive.json`
kopiert und lassen sich dort umbenennen, ergänzen oder entfernen. Die Felder jedes Profils und ihre fachliche Begründung
stehen in [docs/profiles.md](docs/profiles.md), das Dateiformat in [docs/data-format.md](docs/data-format.md) (beides Englisch).

## Aufnahmen mit Claude beschreiben (optional)

Dutzende Aufnahmen zu beschreiben ist der zeitaufwendige Teil. Mit [Claude Code](https://claude.com/claude-code) kann
Claude die Transkripte lesen und Datum, Titel, Zusammenfassung, Schlagworte, Sprechernamen und Kapitel eintragen.
Dazu [`claude-skill/audio-archive`](claude-skill/audio-archive/SKILL.md) nach `~/.claude/skills/` kopieren, die zwei
markierten Abschnitte anpassen und z. B. sagen: *„Beschreibe die neuen Aufnahmen in meinem Audioarchiv in D:\Feldforschung\2024.“*
`reading_view.py` und `apply_metadata.py` sind die Werkzeuge des Skills – sie funktionieren genauso in jedem anderen Ablauf.

## Datenschutz

Alles läuft auf dem eigenen Rechner. noScribe transkribiert lokal, die Seiten sind einfache Dateien, nichts wird
hochgeladen. Die `.gitignore` dieses Repositorys schließt Audiodateien, `_archive`-Ordner und die eigene
`settings.json` aus, damit keine Archivdaten versehentlich auf GitHub landen. Wer einen KI-Assistenten zum Beschreiben
nutzt, gibt die Transkripte an diesen Dienst weiter – das sollte man pro Archiv entscheiden, besonders bei
Forschungsdaten mit Einschränkungen aus Einverständniserklärungen.

## Grenzen

- Automatische Transkripte sind Entwürfe. Kindersprache, Dialekte, verrauschte oder sehr leise Aufnahmen werden schlecht
  erkannt. Die Sprechererkennung kennt keine Namen; die Zuordnung gehört zum Beschreiben.
- Whisper kennt nicht jede Sprache. Für wenig dokumentierte Sprachen `"transcribe": false` setzen und das Archiv für
  Metadaten, Anhören und Kapitelmarken nutzen.
- Noch kein IMDI/CMDI-XML-Export – der CSV-Export ist die Brücke zu Archiv-Depositen.

## Aufbau des Projekts

```
audio_archive/         Python-Werkzeuge (nur Standardbibliothek)
  locales/             en, de, fr, es, ja, zh
  profiles/            Archiv-Profile
  template/            Übersicht und Eingabemaske
claude-skill/          optionaler Claude-Code-Skill
docs/                  Profile und Datenformat
tests/                 Unit-Tests (python -m unittest discover -s tests)
setup-archive.bat      Ordner darauf ziehen, um ein Archiv einzurichten
settings.example.json  nach settings.json kopieren
```

## Mitmachen

Siehe [CONTRIBUTING.md](CONTRIBUTING.md) – neue Sprachen und Profile sind besonders willkommen.

## Lizenz

[MIT](LICENSE)

## Dank

Die Transkription übernimmt [noScribe](https://github.com/kaixxx/noScribe) von Kai Dröge, das auf
[faster-whisper](https://github.com/SYSTRAN/faster-whisper) und [pyannote](https://github.com/pyannote/pyannote-audio) aufbaut.
