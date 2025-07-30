# pyw-music21 🎵
[![PyPI](https://img.shields.io/pypi/v/pyw-music21.svg)](https://pypi.org/project/pyw-music21/)
[![CI](https://github.com/pythonWoods/pyw-music21/actions/workflows/ci.yml/badge.svg)](https://github.com/pythonWoods/pyw-music21/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Type-safe **Music21** integration with stubs, helpers and Pydantic models for the **pythonWoods** ecosystem.

## Overview

**pyw-music21** trasforma Music21 in un'esperienza type-safe e developer-friendly, fornendo stub files per un'autocomplete perfetta, helpers per analisi musicale comuni e modelli Pydantic per una validazione robusta dei dati musicali.

## Quick Start

```bash
pip install pyw-music21

# Genera stubs per il tuo IDE (una volta sola)
python -m pyw.music21.stub

# Oppure con extras per analisi avanzata
pip install pyw-music21[analysis]
```

## Core Features

### 🎯 Type-Safe Music21

```python
from pyw.music21 import Stream, Note, Chord, Key
from pyw.music21.types import Pitch, Duration, TimeSignature

# Autocomplete perfetto e type checking
stream = Stream()
note = Note("C4", quarterLength=1.0)
chord = Chord(["C4", "E4", "G4"])

# Type hints ovunque
def analyze_melody(stream: Stream) -> list[Pitch]:
    """Estrae tutte le altezze dalla melodia."""
    return [note.pitch for note in stream.notes]
```

### 🔧 Smart Helpers

```python
from pyw.music21.helpers import (
    quick_analysis, interval_analysis,
    chord_progression, scale_degrees
)

# Analisi rapida completa
analysis = quick_analysis("path/to/score.xml")
print(f"Key: {analysis.key}")
print(f"Time signature: {analysis.time_signature}")
print(f"Tempo: {analysis.tempo}")

# Analisi intervalli con context
intervals = interval_analysis(melody_stream)
for interval in intervals:
    print(f"{interval.name}: {interval.semitones} semitoni")

# Progressioni armoniche
progression = chord_progression(piano_part)
print("Chord progression:", " → ".join(progression.roman_numerals))

# Gradi della scala
degrees = scale_degrees(melody, key="C major")
print("Scale degrees:", degrees)  # [1, 3, 5, 1, ...]
```

### 📊 Pydantic Models

```python
from pyw.music21.models import (
    MusicalAnalysis, ChordProgression, 
    Interval, ScaleInfo
)

# Modelli validati e serializzabili
@dataclass
class SongAnalysis(MusicalAnalysis):
    title: str
    composer: Optional[str] = None
    key_signature: str
    time_signature: str
    chord_progression: ChordProgression
    melodic_intervals: list[Interval]
    
    def to_json(self) -> str:
        """Serializza l'analisi in JSON."""
        return self.model_dump_json(indent=2)

# Uso type-safe
analysis = SongAnalysis(
    title="Amazing Grace",
    key_signature="G major",
    time_signature="3/4",
    chord_progression=ChordProgression.from_stream(stream),
    melodic_intervals=interval_analysis(melody)
)
```

### 🎼 Advanced Analysis

```python
from pyw.music21.analysis import (
    harmonic_rhythm, voice_leading,
    motivic_analysis, form_analysis
)

# Ritmo armonico
rhythm = harmonic_rhythm(piano_score)
print(f"Chord changes per measure: {rhythm.changes_per_measure}")

# Condotta delle parti
leading = voice_leading(four_part_harmony)
for voice in leading.voices:
    print(f"{voice.name}: {voice.motion_types}")

# Analisi motivica
motifs = motivic_analysis(melody, min_length=4)
for motif in motifs:
    print(f"Motif at measure {motif.measure}: {motif.intervals}")

# Analisi formale
form = form_analysis(sonata_score)
print(f"Form: {form.structure}")  # ["A", "B", "A", "Coda"]
```

### 🔄 Stream Processing

```python
from pyw.music21.processing import (
    transpose_safe, extract_voices,
    normalize_durations, add_chord_symbols
)

# Trasposizione type-safe
transposed = transpose_safe(
    original_stream, 
    interval="P5",  # Quinta perfetta
    validate_range=True
)

# Estrazione voci con nomi
voices = extract_voices(satb_score)
soprano = voices["Soprano"]
bass = voices["Bass"]

# Normalizzazione durate
normalized = normalize_durations(
    stream, 
    target_note_value="quarter",
    quantize=True
)

# Aggiunta simboli accordi
with_chords = add_chord_symbols(
    melody_stream,
    chord_progression=["C", "Am", "F", "G"]
)
```

## Integration Examples

### 🎹 Piano Score Analysis

```python
from pyw.music21 import converter
from pyw.music21.piano import PianoAnalyzer

# Carica e analizza spartito piano
score = converter.parse("chopin_prelude.xml")
analyzer = PianoAnalyzer(score)

# Analisi tecnica
difficulty = analyzer.difficulty_rating()
print(f"Difficulty: {difficulty.level}/10")
print(f"Technical challenges: {difficulty.challenges}")

# Analisi delle mani
hands = analyzer.hand_analysis()
print(f"Right hand range: {hands.right.range}")
print(f"Left hand patterns: {hands.left.patterns}")

# Pedalizzazione suggerita
pedaling = analyzer.suggest_pedaling()
for measure, pedal in pedaling.items():
    print(f"Measure {measure}: {pedal}")
```

### 🎤 Vocal Analysis

```python
from pyw.music21.vocal import VocalAnalyzer, VoiceType

# Analisi parte vocale
vocal_line = extract_voices(score)["Soprano"]
analyzer = VocalAnalyzer(vocal_line)

# Range e tessiture
range_analysis = analyzer.vocal_range()
print(f"Range: {range_analysis.lowest} - {range_analysis.highest}")
print(f"Tessitura: {range_analysis.comfortable_range}")

# Difficoltà vocali
challenges = analyzer.vocal_challenges()
for challenge in challenges:
    print(f"Measure {challenge.measure}: {challenge.difficulty}")

# Classificazione voce
voice_type = analyzer.classify_voice_type()
print(f"Suitable for: {voice_type}")  # VoiceType.SOPRANO
```

### 🎺 Orchestral Tools

```python
from pyw.music21.orchestral import (
    OrchestralScore, InstrumentRange,
    orchestrate, check_ranges
)

# Gestione partitura orchestrale
full_score = OrchestralScore.from_file("symphony.xml")

# Verifica estensioni strumenti
range_issues = check_ranges(full_score)
for issue in range_issues:
    print(f"⚠️ {issue.instrument}: note {issue.problematic_notes} out of range")

# Orchestrazione automatica
piano_reduction = converter.parse("piano_sketch.xml")
orchestrated = orchestrate(
    piano_reduction,
    ensemble="chamber",  # "chamber", "orchestra", "wind_band"
    style="classical"
)
```

## Configuration & Customization

### ⚙️ Settings

```python
from pyw.music21.config import Music21Config

# Configurazione globale
config = Music21Config(
    # Stub generation
    stub_output_dir="./stubs",
    include_private_methods=False,
    
    # Analysis defaults
    default_key_detection="krumhansl",
    chord_detection_method="chordify",
    
    # Performance
    cache_analysis_results=True,
    parallel_processing=True,
    
    # Output formats
    preferred_note_names="english",  # "english", "german", "italian"
    decimal_precision=3
)

# Applica configurazione
config.apply()
```

### 🧩 Custom Analyzers

```python
from pyw.music21.base import BaseAnalyzer
from pyw.music21.types import AnalysisResult

class MyCustomAnalyzer(BaseAnalyzer):
    """Analizzatore personalizzato."""
    
    name = "custom_harmony"
    version = "1.0.0"
    
    def analyze(self, stream: Stream) -> AnalysisResult:
        """Implementa la tua logica di analisi."""
        # Custom analysis logic here
        return AnalysisResult(
            analyzer=self.name,
            data={"custom_metric": self._calculate_metric(stream)}
        )
    
    def _calculate_metric(self, stream: Stream) -> float:
        # Your custom calculation
        return 42.0

# Registra analyzer
from pyw.music21.registry import register_analyzer
register_analyzer(MyCustomAnalyzer)
```

## CLI Tools

```bash
# Genera stubs (migliorato)
pyw-music21 stub --output-dir ./stubs --include-docs

# Analisi rapida da CLI
pyw-music21 analyze score.xml --output analysis.json
pyw-music21 analyze *.mid --format csv --parallel

# Conversioni
pyw-music21 convert song.mid --to musicxml --transpose P5
pyw-music21 convert *.xml --to midi --tempo 120

# Validazione
pyw-music21 validate score.xml --check-ranges --voice-types SATB
pyw-music21 lint orchestral_score.xml --report detailed
```

## Performance & Caching

```python
from pyw.music21.performance import (
    cache_analysis, parallel_analyze,
    lazy_load_score
)

# Cache automatico per analisi costose
@cache_analysis(ttl=3600)  # Cache for 1 hour
def expensive_harmonic_analysis(stream: Stream):
    return detailed_harmonic_analysis(stream)

# Processamento parallelo
scores = ["song1.xml", "song2.xml", "song3.xml"]
results = parallel_analyze(
    scores, 
    analyzer=quick_analysis,
    max_workers=4
)

# Lazy loading per file grandi
large_score = lazy_load_score("massive_symphony.xml")
# Carica solo quando necessario
first_part = large_score.parts[0]  # Ora carica effettivamente
```

## Testing & Quality

```python
from pyw.music21.testing import (
    create_test_score, assert_valid_music,
    MockScore, generate_random_melody
)

def test_my_analyzer():
    # Score di test predefiniti
    test_score = create_test_score("major_scale_c")
    
    # Genera melodie casuali per stress testing
    random_melody = generate_random_melody(
        length=16,
        key="G major",
        note_values=["quarter", "eighth"]
    )
    
    # Validazione musicale
    result = my_analyzer.analyze(test_score)
    assert_valid_music(result.processed_score)
    
    # Mock per test unitari
    with MockScore(notes=["C4", "E4", "G4"]) as mock:
        analysis = quick_analysis(mock.stream)
        assert analysis.key.name == "C major"
```

## Bundle Integration

Parte del bundle **pyw-music**:

```bash
# Installa tutto l'ecosistema musicale
pip install pyw-music  # pyw-music21 + pyw-musicparser

# Oppure componenti individuali
pip install pyw-music21[analysis,orchestral]
pip install pyw-musicparser[lilypond,advanced]
```

Cross-module integration:

```python
# Con pyw-musicparser
from pyw.musicparser import LilypondParser
from pyw.music21.converters import from_lilypond

lilypond_code = '''
\\relative c' { c d e f g }
'''

# Parse Lilypond → Music21 Stream
parser = LilypondParser()
parsed = parser.parse(lilypond_code)
stream = from_lilypond(parsed)

# Analizza con pyw-music21
analysis = quick_analysis(stream)
```

## Migration Guide

### From Raw Music21

```python
# Before (raw music21)
from music21 import stream, note, pitch
s = stream.Stream()
n = note.Note("C4")
s.append(n)

# After (pyw-music21)
from pyw.music21 import Stream, Note
s = Stream()  # Type-safe!
n = Note("C4")  # Autocomplete perfetto
s.append(n)

# Plus: helpers inclusi
analysis = quick_analysis(s)  # Non disponibile in music21
```

### Existing Codebases

1. **Install**: `pip install pyw-music21`
2. **Generate stubs**: `python -m pyw.music21.stub`
3. **Replace imports**: `music21.` → `pyw.music21.`
4. **Add type hints**: Usa i nuovi tipi typed
5. **Leverage helpers**: Sostituisci codice boilerplate con helpers

## Advanced Topics

### 🎛️ Custom Music21 Builds

```python
from pyw.music21.build import Music21Builder

# Build Music21 personalizzato
builder = Music21Builder()
builder.include_modules(["stream", "note", "chord", "key"])
builder.exclude_modules(["graph", "braille"])  # Riduce footprint
builder.optimize_for("analysis")  # vs "composition", "performance"

custom_music21 = builder.build()
```

### 🔌 Plugin System

```python
from pyw.music21.plugins import register_plugin

@register_plugin("jazz_analysis")
class JazzAnalysisPlugin:
    """Plugin per analisi jazz-specific."""
    
    def analyze_chord_extensions(self, chord):
        # Jazz-specific chord analysis
        pass
    
    def detect_ii_v_i(self, progression):
        # Rileva progressioni ii-V-I
        pass

# Auto-discovery e integrazione
```

### 📈 Performance Monitoring

```python
from pyw.music21.monitoring import (
    profile_analysis, memory_usage,
    optimization_hints
)

# Profiling automatico
@profile_analysis
def complex_analysis(score):
    # Your analysis code
    pass

# Hint per ottimizzazione
hints = optimization_hints(my_analysis_function)
print("Suggested optimizations:", hints)
```

## Ecosystem Integration

```python
# Con altri moduli pyw
from pyw.logger import get_logger  # Logging strutturato
from pyw.fs import Path  # Filesystem unificato
from pyw.config import load_config  # Configurazione

logger = get_logger("music21")

def analyze_music_library(library_path: Path):
    """Analizza intera libreria musicale."""
    config = load_config("music_analysis.yaml")
    
    for score_file in library_path.glob("**/*.xml"):
        logger.info("Analyzing", file=score_file.name)
        
        try:
            analysis = quick_analysis(score_file)
            # Salva risultati...
        except Exception as e:
            logger.error("Analysis failed", file=score_file.name, error=str(e))
```

## Roadmap

- 🎼 **Enhanced stubs**: Copertura completa Music21 3.x+
- 🤖 **AI integration**: Analisi basate su ML, generazione intelligente
- 🎹 **Interactive tools**: Jupyter widgets, live analysis
- 📱 **Mobile support**: Ottimizzazioni per deployment mobile
- 🎵 **Real-time**: Stream processing, live performance analysis
- 🌐 **Web integration**: WebAudio API, browser compatibility
- 📊 **Advanced visualization**: Interactive score displays, analysis plots

## Contributing

1. **Fork & Clone**: `git clone https://github.com/pythonWoods/pyw-music21.git`
2. **Setup**: `poetry install && poetry shell`
3. **Stubs**: `python -m pyw.music21.stub --dev` (per development)
4. **Test**: `pytest --cov=pyw.music21`
5. **Lint**: `ruff check . && mypy`
6. **Music validation**: `python scripts/validate_music_examples.py`

Contributi particolarmente benvenuti su:
- Stub completeness per Music21 edge cases
- Performance optimization per large scores
- Domain-specific analyzers (jazz, classical, contemporary)
- Cross-platform compatibility

---

**Happy music coding nella foresta di pythonWoods!** 🎵🌲

## Links utili

Documentazione dev (work-in-progress) → https://pythonwoods.dev/docs/pyw-music21/latest/

Issue tracker → https://github.com/pythonWoods/pyw-music21/issues

Changelog → https://github.com/pythonWoods/pyw-music21/releases

Music21 official docs → https://web.mit.edu/music21/doc/

© pythonWoods — MIT License