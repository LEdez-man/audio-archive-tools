# Archive profiles

A profile is only a starting point: when an archive is set up, its fields and tag categories are copied into
`_archive/archive.json`, where you can rename, remove or add them at any time.

| Profile | Transcription | Tag categories (filters) |
|---|---|---|
| `family` – family / private | yes | people, events |
| `oral_history` – oral history | yes | people, topics, places |
| `linguistic_fieldwork` – linguistic fieldwork | yes | languages, genres, speakers, places |
| `sociolinguistics` – sociolinguistics | yes | speakers, social groups, interview modules, places |
| `soundscape` – field recording / soundscape | no | places, sound sources / species, habitats |
| `journalism` – journalism | yes | people, topics, take types, places |
| `generic` – other | yes | keywords |

## Family / private

Minimal on purpose: a period and description for the archive, a place per recording. Dating and description
come from the recordings themselves (spoken date announcements are common in home recordings).

## Oral history

Project: project, institution, principal investigator, period, region, description, repository, licence.
Recording: interview ID, interviewee, interviewer, place, language, consent, access, embargo.

Consent, access level and embargo are the minimum needed to share interviews responsibly with an archive
later (cf. Oral History Association guidelines and typical deposit agreements).

## Linguistic fieldwork

Modelled on session-based metadata as used in language documentation archives (IMDI/CMDI at TLA and ELAR,
OLAC / Dublin Core for discovery):

- Project: project, principal investigator, institution, funder, period, region, languages as
  **ISO 639-3** codes, description, repository, licence, ethics approval.
- Recording ("session"): session ID, place and coordinates, language (ISO 639-3) and variety, speakers
  (code, role, age, gender, L1 – use codes/pseudonyms, not names, where required), recorded by, genre
  (elicitation, word list, narrative, conversation, interview, procedural text, song, ritual speech),
  stimulus/task (e.g. Pear Story, Frog Story, a questionnaire), equipment, audio format, consent, access
  level (open / restricted / closed) and transcription status (none / automatic / corrected / annotated).

The CSV export can be turned into an archive deposit spreadsheet or imported into a corpus tool. Whisper-based
transcription works for many major languages; for under-resourced languages set `"transcribe": false` in
`archive.json` and use the archive purely for metadata, listening and chapter marks.

## Sociolinguistics

Adds the social variables of a speaker sample (speaker code, age group, gender, education, occupation, origin)
and the **interview modules** of a classic sociolinguistic interview (e.g. free conversation, reading passage,
word list, minimal pairs – after Labov), plus a project field for the variables studied and the community.

## Field recording / soundscape

No transcription. Place and coordinates, time of day, habitat, weather, equipment, microphone setup (e.g. ORTF,
AB, MS, ambisonics, hydrophone), audio format, recordist. Tag categories for places, sound sources/species and
habitats make a sound map-like overview searchable.

## Journalism

For reports, features, podcasts, vox pops, demonstrations or press conferences:

- Project ("production"): production, outlet/broadcaster, author, editor, format, topic, period, deadline.
- Recording ("take"): take number, interviewee and role/function, situation (interview, vox pop, statement,
  press conference, ambience/atmo, scene, phone), place, **release** (yes / anonymised / pending / no),
  rating (usable / maybe / unusable), equipment.
- Chapters are shown as **soundbites**: mark the quotable passages with their time code while listening.

Release status and anonymisation matter: vox pop participants often agree only to anonymous use.
Store contact details outside this archive.
