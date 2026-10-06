# audio-archive-tools

[English](README.md) · [Deutsch](README.de.md) · **Français** · [Español](README.es.md) · [日本語](README.ja.md) · [中文](README.zh-CN.md)

Transformer un dossier d'enregistrements audio en une archive consultable et bien documentée – **en local, sans serveur, sans rien téléverser**.

Les outils transcrivent les enregistrements avec [noScribe](https://github.com/kaixxx/noScribe) (Whisper + identification des
locuteurs), créent des sous-titres, donnent à chaque fichier une date et un nom parlant, et génèrent une page de
consultation hors ligne : filtres, recherche plein texte et accès direct à chaque phrase d'un enregistrement.
Un formulaire permet de décrire le projet et chaque enregistrement sans modifier de fichiers à la main.

Né pour une archive familiale d'anciens enregistrements de dictaphone et de téléphone, le projet convient tout autant à :

| | |
|---|---|
| **Famille / privé** | enregistrements à la maison, voix d'enfants, conversations avec les grands-parents |
| **Histoire orale** | entretiens biographiques et témoignages, avec consentement, accès et embargo |
| **Terrain linguistique** | sessions avec langues ISO 639-3, locuteurs, genre, stimulus, consentement et niveau d'accès (à la manière d'IMDI/ELAN) |
| **Sociolinguistique** | entretiens avec variables sociales et modules (conversation libre, texte lu, liste de mots, paires minimales) |
| **Field recording / paysage sonore** | sons de la nature et de l'environnement avec lieu, coordonnées, habitat, matériel – sans transcription |
| **Journalisme** | prises et extraits sonores pour reportages, magazines, micro-trottoirs, manifestations, conférences de presse – avec autorisation de diffusion |

## Fonctionnalités

- **Transcription par lots** avec noScribe sans interface – relançable à tout moment, fichiers identiques transcrits une
  seule fois, second essai automatique sans identification des locuteurs, nouvel essai avec traitement audio pour les cas difficiles
- **Sous-titres (.srt)** à côté de chaque enregistrement – VLC les affiche automatiquement
- **Filtre contre les hallucinations de Whisper** dans le silence ou le bruit (génériques de chaînes, boucles infinies)
- **Noms de fichiers cohérents** : `AAAA-MM-JJ_Titre-court_IDAppareil.mp3` (dates estimées avec `ca`), avec journal d'annulation
- **Page de consultation** : filtres par année et par catégories propres à l'archive, recherche plein texte, lecteur intégré,
  clic sur une phrase pour y accéder, chapitres ou extraits sonores, informations sur le projet
- **Formulaire** pour le projet et chaque enregistrement (date, titre, résumé, mots-clés, champs du profil, noms des
  locuteurs, chapitres) – les modifications restent dans le navigateur et sont enregistrées dans un fichier importé par les outils
- **Profils** adaptés aux usages ci-dessus – modifiables librement pour chaque archive
- **Export CSV** pour tableurs, outils de corpus ou dépôts d'archives
- **Six langues** pour les pages, messages et fichiers batch : français, anglais, allemand, espagnol, japonais, chinois
- Doublons, originaux AMR (convertis en MP3 pour les navigateurs) et fichiers vides sont **mis de côté, jamais supprimés**
- Uniquement la bibliothèque standard de Python – aucun paquet à installer

## Prérequis

- Windows 10/11 (les fichiers batch sont pour Windows ; les scripts Python fonctionnent partout)
- [Python](https://www.python.org/) 3.9 ou plus récent
- [ffmpeg](https://ffmpeg.org/) dans le `PATH` (p. ex. `winget install ffmpeg`)
- [noScribe](https://github.com/kaixxx/noScribe) 0.7 ou plus récent (avec ligne de commande). Une carte graphique NVIDIA
  accélère fortement la transcription, mais n'est pas indispensable.

## Installation

1. Télécharger ou cloner ce dépôt, p. ex. dans `Documents\audio-archive-tools`.
2. Copier `settings.example.json` en `settings.json` et l'adapter : `"language": "fr"` pour l'interface,
   `"transcription_language": "fr"` (ou `auto`) pour les enregistrements, chemin de noScribe.

## Démarrage rapide

1. **Sauvegarder** le dossier contenant les enregistrements.
2. **Glisser le dossier sur `setup-archive.bat`.** Choisir un profil, un titre et la langue des enregistrements.
   Un sous-dossier `_archive` contenant les fichiers batch est créé.
3. Lancer **`1 Transcrire`**. Chaque enregistrement reçoit une transcription `.html` et des sous-titres `.srt`.
4. Lancer **`2 Décrire les enregistrements (formulaire)`**, remplir les informations, enregistrer – choisir le dossier `_archive`.
5. Lancer **`3 Mettre à jour l'archive`**. Les fichiers sont renommés et la page `Archive audio.html` s'ouvre.

Nouveaux enregistrements ? Les placer dans le dossier et refaire 1 → 2 → 3. Seuls les nouveaux fichiers sont traités.

| Fichier batch | Fonction |
|---|---|
| `1 Transcrire` | transcrit tout ce qui n'a pas de transcription et enregistre les nouveaux fichiers |
| `2 Décrire les enregistrements (formulaire)` | génère et ouvre le formulaire |
| `3 Mettre à jour l'archive` | importe les saisies, renomme, régénère sous-titres et pages |
| `Régénérer les sous-titres` | après correction d'une transcription dans l'éditeur de noScribe |
| `Retranscrire un cas difficile` | nouvel essai avec réduction du bruit et normalisation du volume |
| `Exporter en CSV` | écrit `<titre>.csv` et `<titre>_project.csv` |
| `Annuler les renommages` | annule tous les renommages et déplacements enregistrés |

## Profils, format, Claude

Les champs de chaque profil et leur justification sont décrits dans [docs/profiles.md](docs/profiles.md), le format de
fichier dans [docs/data-format.md](docs/data-format.md) (en anglais). Pour faire décrire les enregistrements par
[Claude Code](https://claude.com/claude-code) à partir des transcriptions, copier
[`claude-skill/audio-archive`](claude-skill/audio-archive/SKILL.md) dans `~/.claude/skills/`.

## Confidentialité

Tout fonctionne sur votre ordinateur ; rien n'est téléversé. Le `.gitignore` exclut fichiers audio, dossiers `_archive`
et `settings.json`. Si vous utilisez un assistant IA pour décrire les enregistrements, les transcriptions sont
transmises à ce service – à décider pour chaque archive, en particulier pour des données de recherche soumises à consentement.

## Limites

- Les transcriptions automatiques sont des brouillons ; voix d'enfants, dialectes et enregistrements bruités sont mal reconnus.
- Whisper ne couvre pas toutes les langues : utiliser alors `"transcribe": false`.
- Pas encore d'export XML IMDI/CMDI – l'export CSV sert de passerelle.

## Contribuer · Licence · Remerciements

Voir [CONTRIBUTING.md](CONTRIBUTING.md). Licence [MIT](LICENSE). Transcription par [noScribe](https://github.com/kaixxx/noScribe)
de Kai Dröge, basé sur [faster-whisper](https://github.com/SYSTRAN/faster-whisper) et [pyannote](https://github.com/pyannote/pyannote-audio).
