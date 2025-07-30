# pyw-music 🎵
[![PyPI](https://img.shields.io/pypi/v/pyw-music.svg)](https://pypi.org/project/pyw-music/)
[![CI](https://github.com/pythonWoods/pyw-music/actions/workflows/ci.yml/badge.svg)](https://github.com/pythonWoods/pyw-music/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
> Music processing bundle for the **pythonWoods** ecosystem.

## Components

| Package | Description | Status |
|---------|-------------|--------|
| **pyw-music21** | Music21 stubs & helpers | placeholder `0.0.0` |
| **pyw-musicparser** | Parse MIDI/Lilypond → music21 | placeholder `0.0.0` |
| **pyw-music** | Meta-package: music processing toolkit | `0.0.1` |

## Philosophy

* **Unified music processing** – da MIDI a Lilypond, tutto tramite music21.
* **Type-safe APIs** – Pydantic models per note, accordi, scale.
* **Format-agnostic** – importa da MIDI, MusicXML, Lilypond, esporta ovunque.
* **Composable** – usa solo i parser che ti servono.

### Installation (nothing to use yet)

```bash
pip install pyw-music
```

Questo installerà automaticamente:
- `pyw-core` (namespace comune)
- `pyw-music21` (stubs e utilities per music21)
- `pyw-musicparser` (parser MIDI/Lilypond)
- `music21` (libreria base)
- `pretty_midi` (parsing MIDI robusto)

## Roadmap

- 🎼 **pyw-music21**: Type stubs per music21, helpers per export/import
- 🎹 **pyw-musicparser**: Parser MIDI → music21, Lilypond → music21
- 🎵 Supporto per formati aggiuntivi (ABC notation, Finale, Sibelius)
- 🎤 Audio analysis integration (librosa, essentia)

## Contributing

1. Fork il repo del modulo che ti interessa (`pyw-music21`, `pyw-musicparser`).
2. Crea virtual-env via Poetry: `poetry install && poetry shell`.
3. Lancia linter e mypy: `ruff check . && mypy`.
4. Apri la PR: CI esegue lint, type-check, build.

Felice composizione nella foresta di **pythonWoods**! 🌲🎼

## Links utili
Documentazione dev (work-in-progress) → https://pythonwoods.dev/docs/pyw-music/latest/

Issue tracker → https://github.com/pythonWoods/pyw-music/issues

Changelog → https://github.com/pythonWoods/pyw-music/releases

© pythonWoods — MIT License