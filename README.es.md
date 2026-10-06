# audio-archive-tools

[English](README.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · **Español** · [日本語](README.ja.md) · [中文](README.zh-CN.md)

Convierte una carpeta de grabaciones de audio en un archivo consultable y bien descrito – **en local, sin servidor y sin subir nada**.

Las herramientas transcriben las grabaciones con [noScribe](https://github.com/kaixxx/noScribe) (Whisper + identificación de
hablantes), crean subtítulos, dan a cada archivo una fecha y un nombre descriptivo y generan una página de consulta sin
conexión: filtros, búsqueda en texto completo y salto directo a cualquier frase de una grabación. Un formulario permite
describir el proyecto y cada grabación sin editar archivos a mano.

Nació para un archivo familiar de antiguas grabaciones de dictáfono y móvil, y sirve igualmente para:

| | |
|---|---|
| **Familia / privado** | grabaciones en casa, voces de niños, conversaciones con los abuelos |
| **Historia oral** | entrevistas biográficas y testimonios, con consentimiento, acceso y embargo |
| **Trabajo de campo lingüístico** | sesiones con lenguas ISO 639-3, hablantes, género, estímulo, consentimiento y nivel de acceso (al estilo IMDI/ELAN) |
| **Sociolingüística** | entrevistas con variables sociales y módulos (conversación libre, lectura, lista de palabras, pares mínimos) |
| **Grabación de campo / paisaje sonoro** | sonidos de la naturaleza y del entorno con lugar, coordenadas, hábitat, equipo – sin transcripción |
| **Periodismo** | tomas y cortes de voz para reportajes, features, encuestas en la calle, manifestaciones, ruedas de prensa – con autorización de publicación |

## Funciones

- **Transcripción por lotes** con noScribe sin interfaz – se puede reiniciar en cualquier momento, los archivos idénticos
  se transcriben una sola vez, segundo intento automático sin identificación de hablantes, reintento con tratamiento de audio
- **Subtítulos (.srt)** junto a cada grabación – VLC los muestra automáticamente
- **Filtro contra alucinaciones de Whisper** en silencio o ruido (créditos de emisoras, bucles infinitos)
- **Nombres de archivo coherentes**: `AAAA-MM-DD_Título-corto_IDGrabadora.mp3` (fechas estimadas con `ca`), con registro para deshacer
- **Página de consulta**: filtros por año y por las categorías propias del archivo, búsqueda en texto completo, reproductor,
  clic en una frase para saltar a ella, capítulos o cortes de voz, datos del proyecto
- **Formulario** para el proyecto y cada grabación (fecha, título, resumen, etiquetas, campos del perfil, nombres de
  hablantes, capítulos) – los cambios se guardan en el navegador y luego en un archivo que importan las herramientas
- **Perfiles** para los usos anteriores – libremente adaptables en cada archivo
- **Exportación CSV** para hojas de cálculo, herramientas de corpus o depósitos en archivos
- **Seis idiomas** para páginas, mensajes y archivos batch: español, inglés, alemán, francés, japonés, chino
- Duplicados, originales AMR (convertidos a MP3 para navegadores) y archivos vacíos se **apartan, nunca se borran**
- Solo la biblioteca estándar de Python – nada que instalar

## Requisitos

- Windows 10/11 (los archivos batch son para Windows; los scripts de Python funcionan en cualquier sistema)
- [Python](https://www.python.org/) 3.9 o posterior
- [ffmpeg](https://ffmpeg.org/) en el `PATH` (p. ej. `winget install ffmpeg`)
- [noScribe](https://github.com/kaixxx/noScribe) 0.7 o posterior (con línea de comandos). Una tarjeta gráfica NVIDIA acelera
  mucho la transcripción, pero no es imprescindible.

## Instalación

1. Descargar o clonar este repositorio, p. ej. en `Documentos\audio-archive-tools`.
2. Copiar `settings.example.json` a `settings.json` y ajustarlo: `"language": "es"` para la interfaz,
   `"transcription_language": "es"` (o `auto`) para las grabaciones, ruta de noScribe.

## Inicio rápido

1. **Hacer una copia de seguridad** de la carpeta con las grabaciones.
2. **Arrastrar la carpeta sobre `setup-archive.bat`.** Elegir perfil, título e idioma de las grabaciones.
   Se crea una subcarpeta `_archive` con los archivos batch.
3. Ejecutar **`1 Transcribir`**. Cada grabación recibe una transcripción `.html` y subtítulos `.srt`.
4. Ejecutar **`2 Describir grabaciones (formulario)`**, completar los datos y guardar en la carpeta `_archive`.
5. Ejecutar **`3 Actualizar archivo`**. Los archivos se renombran y se abre `Archivo de audio.html`.

¿Grabaciones nuevas? Ponerlas en la carpeta y repetir 1 → 2 → 3. Solo se procesan los archivos nuevos.

| Archivo batch | Función |
|---|---|
| `1 Transcribir` | transcribe todo lo que no tiene transcripción y registra las grabaciones nuevas |
| `2 Describir grabaciones (formulario)` | genera y abre el formulario |
| `3 Actualizar archivo` | importa lo guardado, renombra, regenera subtítulos y páginas |
| `Regenerar subtítulos` | tras corregir una transcripción en el editor de noScribe |
| `Volver a transcribir un caso difícil` | nuevo intento con reducción de ruido y normalización de volumen |
| `Exportar como CSV` | escribe `<título>.csv` y `<título>_project.csv` |
| `Deshacer cambios de nombre` | revierte todos los cambios de nombre y traslados registrados |

## Perfiles, formato, Claude

Los campos de cada perfil y su justificación están en [docs/profiles.md](docs/profiles.md); el formato de archivo en
[docs/data-format.md](docs/data-format.md) (en inglés). Para que [Claude Code](https://claude.com/claude-code) describa
las grabaciones a partir de las transcripciones, copiar [`claude-skill/audio-archive`](claude-skill/audio-archive/SKILL.md)
a `~/.claude/skills/`.

## Privacidad

Todo se ejecuta en su ordenador; no se sube nada. El `.gitignore` excluye archivos de audio, carpetas `_archive` y
`settings.json`. Si usa un asistente de IA para describir grabaciones, las transcripciones se comparten con ese servicio:
decídalo para cada archivo, sobre todo con datos de investigación sujetos a consentimiento.

## Limitaciones

- Las transcripciones automáticas son borradores; voces infantiles, dialectos y grabaciones con ruido se reconocen mal.
- Whisper no cubre todas las lenguas: en ese caso usar `"transcribe": false`.
- Aún no hay exportación XML IMDI/CMDI; la exportación CSV sirve de puente.

## Contribuir · Licencia · Agradecimientos

Ver [CONTRIBUTING.md](CONTRIBUTING.md). Licencia [MIT](LICENSE). Transcripción con [noScribe](https://github.com/kaixxx/noScribe)
de Kai Dröge, basado en [faster-whisper](https://github.com/SYSTRAN/faster-whisper) y [pyannote](https://github.com/pyannote/pyannote-audio).
