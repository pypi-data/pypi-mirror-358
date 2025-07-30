# pyw-musicparser 🎼
[![PyPI](https://img.shields.io/pypi/v/pyw-musicparser.svg)](https://pypi.org/project/pyw-musicparser/)
[![CI](https://github.com/pythonWoods/pyw-musicparser/actions/workflows/ci.yml/badge.svg)](https://github.com/pythonWoods/pyw-musicparser/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Parse **MIDI**, **MusicXML**, **Lilypond** e altri formati musicali con estrazione automatica di features per l'ecosistema **pythonWoods**.

## Overview

**pyw-musicparser** è il parser musicale universale dell'ecosistema pythonWoods. Converte qualsiasi formato musicale in oggetti Music21 strutturati, estrae features automaticamente e si integra perfettamente con pyw-music21 per analisi avanzate.

## Features

### 🎵 Format Support
- **MIDI**: Parsing completo con metadata preservation  
- **MusicXML**: Import/export con layout information
- **Lilypond**: Notation parsing con lilypond-book support
- **ABC Notation**: Folk e traditional music
- **Kern**: Musicological analysis format
- **Audio**: MP3/WAV → MIDI via onset detection

### 🔍 Feature Extraction
- **Harmonic Analysis**: Key detection, chord progression, cadences
- **Rhythmic Features**: Tempo, meter, syncopation analysis
- **Melodic Analysis**: Intervals, contour, phrase structure
- **Statistical Features**: Note distributions, duration patterns
- **Style Recognition**: Genre classification, composer identification

### ⚡ Performance
- **Streaming Parser**: Gestione file musicali enormi senza memory overflow
- **Batch Processing**: Parse migliaia di file in parallelo
- **Caching Intelligente**: Feature extraction con cache persistente
- **Format Detection**: Auto-detect formato da contenuto/estensione

## Installation

```bash
# Base installation
pip install pyw-musicparser

# Con support audio analysis (librosa, aubio)
pip install pyw-musicparser[audio]

# Con Lilypond rendering support
pip install pyw-musicparser[lilypond]

# Music processing completo
pip install pyw-music  # Bundle: pyw-music21 + pyw-musicparser
```

## Quick Start

### Basic Parsing

```python
from pyw.musicparser import parse, MusicScore

# Parse qualsiasi formato - auto-detection
score = parse("symphony.mid")
print(f"Key: {score.key_signature}")
print(f"Tempo: {score.tempo} BPM") 
print(f"Duration: {score.duration} seconds")
print(f"Parts: {len(score.parts)}")

# Parse con options specifiche
score = parse("song.xml", 
    extract_features=True,
    normalize_tempo=True,
    quantize_timing=True
)

# Access parsed elements
for part in score.parts:
    print(f"Instrument: {part.instrument}")
    for measure in part.measures:
        print(f"  Measure {measure.number}: {len(measure.notes)} notes")
```

### Feature Extraction

```python
from pyw.musicparser import FeatureExtractor

# Extract comprehensive features
extractor = FeatureExtractor(
    harmonic=True,      # Key, chords, progressions
    rhythmic=True,      # Tempo, meter, syncopation  
    melodic=True,       # Intervals, contour, phrases
    statistical=True    # Distributions, patterns
)

features = extractor.extract("piece.mid")

# Harmonic features
print(f"Key: {features.harmonic.key}")
print(f"Mode: {features.harmonic.mode}")
print(f"Chord progression: {features.harmonic.chord_sequence}")
print(f"Modulations: {features.harmonic.key_changes}")

# Rhythmic features  
print(f"Tempo: {features.rhythmic.tempo_mean} ± {features.rhythmic.tempo_std}")
print(f"Time signature: {features.rhythmic.time_signature}")
print(f"Syncopation level: {features.rhythmic.syncopation_score}")

# Melodic features
print(f"Melodic range: {features.melodic.pitch_range} semitones")
print(f"Average interval: {features.melodic.avg_interval}")
print(f"Phrase count: {len(features.melodic.phrases)}")

# Statistical features
print(f"Note density: {features.statistical.notes_per_beat}")
print(f"Most common pitch: {features.statistical.pitch_mode}")
```

### Batch Processing

```python
from pyw.musicparser import BatchParser
from pathlib import Path

# Setup batch parser
parser = BatchParser(
    formats=['mid', 'xml', 'ly'],
    extract_features=True,
    parallel_workers=8,
    cache_results=True
)

# Parse entire directory
results = parser.parse_directory("music_collection/")

# Results with progress tracking
for result in parser.parse_with_progress("large_dataset/"):
    if result.success:
        print(f"✓ {result.filename}: {result.score.duration:.1f}s")
        # Save features to database
        save_features(result.filename, result.features)
    else:
        print(f"✗ {result.filename}: {result.error}")

# Export results
parser.export_features("features.json", format="json")
parser.export_features("features.csv", format="csv")
```

## Advanced Usage

### Custom Format Support

```python
from pyw.musicparser import register_parser, BaseParser

@register_parser("custom", extensions=[".cus", ".custom"])
class CustomFormatParser(BaseParser):
    """Parser per formato musicale personalizzato."""
    
    def parse_file(self, filepath: Path) -> MusicScore:
        # Implementa parsing logic
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Convert to Music21 objects
        score = self.create_score()
        # ... parsing logic ...
        return score
    
    def detect_format(self, content: bytes) -> bool:
        # Logic per auto-detection
        return content.startswith(b"CUSTOM_MUSIC")

# Ora disponibile automaticamente
score = parse("music.custom")  # Usa CustomFormatParser
```

### Smart MIDI Analysis

```python
from pyw.musicparser import MidiAnalyzer

# Analyzer con AI-powered features
analyzer = MidiAnalyzer(
    chord_detection="advanced",     # Uses harmonic analysis
    tempo_detection="dynamic",      # Handles tempo changes
    instrument_separation=True,     # Separate melody/accompaniment
    style_analysis=True            # Genre/style classification
)

analysis = analyzer.analyze("complex_piece.mid")

# Advanced harmonic analysis
print("Chord progression analysis:")
for progression in analysis.chord_progressions:
    print(f"  {progression.measures}: {' - '.join(progression.chords)}")
    print(f"    Function: {progression.harmonic_function}")
    print(f"    Cadence: {progression.cadence_type}")

# Tempo and rhythm analysis
print(f"Tempo changes: {len(analysis.tempo_changes)}")
for change in analysis.tempo_changes:
    print(f"  Measure {change.measure}: {change.tempo} BPM")

# Style classification
print(f"Predicted genre: {analysis.style.genre} ({analysis.style.confidence:.2f})")
print(f"Composer style: {analysis.style.composer_similarity}")
```

### Lilypond Integration

```python
from pyw.musicparser import LilypondParser, LilypondRenderer

# Parse Lilypond notation
parser = LilypondParser(
    include_layout=True,        # Preserve formatting
    extract_lyrics=True,        # Handle vocal music
    process_markup=True         # Parse text annotations
)

score = parser.parse("sheet_music.ly")

# Access Lilypond-specific features
if score.has_lyrics:
    for verse in score.lyrics:
        print(f"Verse {verse.number}: {verse.text}")

if score.markup_annotations:
    for annotation in score.markup_annotations:
        print(f"Markup at {annotation.position}: {annotation.text}")

# Render back to Lilypond
renderer = LilypondRenderer(
    paper_size="a4",
    staff_size=20,
    include_midi=True
)

lilypond_code = renderer.render(score)
with open("output.ly", "w") as f:
    f.write(lilypond_code)
```

### Audio-to-MIDI Conversion

```python
from pyw.musicparser import AudioParser

# Advanced audio-to-MIDI conversion
parser = AudioParser(
    onset_detection="complex",      # Multi-algorithm onset detection
    pitch_tracking="polyphonic",    # Handle multiple simultaneous notes
    tempo_tracking="dynamic",       # Adaptive tempo following
    noise_reduction=True           # Clean up audio artifacts
)

# Convert audio file
midi_score = parser.parse("recording.wav")

# Fine-tune conversion parameters
parser.configure(
    min_note_duration=0.1,         # Filter very short notes
    pitch_bend_sensitivity=0.5,    # Handle microtonal variations
    velocity_normalization=True,   # Normalize note velocities
    quantization_strength=0.8      # Balance between accuracy and readability
)

# Batch audio conversion
audio_files = ["song1.mp3", "song2.wav", "song3.flac"]
midi_results = parser.convert_batch(audio_files, output_dir="midi_output/")
```

## Integration with pyw-music21

```python
from pyw.musicparser import parse
from pyw.music21 import analyze, transform, generate

# Parse and analyze in one pipeline
score = parse("composition.mid", extract_features=True)

# Use pyw-music21 for advanced analysis
harmonic_analysis = analyze.harmonic_rhythm(score)
melodic_patterns = analyze.find_motifs(score)
voice_leading = analyze.voice_leading_quality(score)

# Transform parsed music
transposed = transform.transpose(score, interval="P5")
augmented = transform.augment_rhythm(score, factor=2.0)
reharmonized = transform.reharmonize(score, style="jazz")

# Generate variations
variations = generate.create_variations(score, 
    techniques=["inversion", "retrograde", "diminution"]
)

# Export enhanced version
enhanced_score = transform.apply_multiple(score, [
    transform.add_ornaments,
    transform.improve_voice_leading,
    transform.add_dynamics
])
enhanced_score.export("enhanced.xml")
```

## Data Analysis & Export

### Feature Analysis Pipeline

```python
from pyw.musicparser import FeatureAnalyzer, Dataset
import pandas as pd

# Create musical dataset
dataset = Dataset.from_directory("classical_music/")

# Comprehensive feature extraction
analyzer = FeatureAnalyzer(
    features=[
        "harmonic_complexity", "melodic_variation", 
        "rhythmic_diversity", "structural_coherence",
        "instrumental_texture", "dynamic_range"
    ]
)

# Extract features for all pieces
feature_matrix = analyzer.extract_batch(dataset)

# Convert to pandas DataFrame
df = feature_matrix.to_dataframe()
print(df.describe())

# Statistical analysis
correlation_matrix = df.corr()
clusters = analyzer.cluster_pieces(df, n_clusters=5)

# Export results
df.to_csv("music_features.csv")
analyzer.export_clusters("clusters.json")
```

### Database Integration

```python
from pyw.musicparser import MusicDatabase
from pyw.core import BaseConfig

class DatabaseConfig(BaseConfig):
    database_url: str = "sqlite:///music_analysis.db"
    index_features: bool = True
    auto_backup: bool = True

# Setup music database
db = MusicDatabase(DatabaseConfig())

# Store parsed scores with features
score = parse("symphony.mid", extract_features=True)
db.store_score(
    filepath="symphony.mid",
    score=score,
    features=score.features,
    metadata={
        "composer": "Mozart",
        "opus": "K.550",
        "genre": "Classical"
    }
)

# Query database
results = db.query(
    composer="Mozart",
    key_signature="D minor",
    tempo_range=(120, 140),
    duration_min=300  # 5+ minutes
)

# Feature-based similarity search
similar_pieces = db.find_similar(
    reference_score=score,
    similarity_threshold=0.8,
    features=["harmonic", "melodic"]
)
```

## Quality Assurance

### Parsing Validation

```python
from pyw.musicparser import ParseValidator, QualityChecker

# Validate parsing results
validator = ParseValidator(
    check_completeness=True,    # All notes parsed correctly
    check_timing=True,          # Rhythm preservation
    check_harmony=True,         # Chord structure intact
    check_structure=True        # Form and sections
)

# Check single file
validation_result = validator.validate("complex_score.xml")
if not validation_result.is_valid:
    for issue in validation_result.issues:
        print(f"⚠️  {issue.severity}: {issue.message}")
        print(f"   Location: measure {issue.measure}")

# Quality assessment
checker = QualityChecker()
quality_report = checker.assess("parsed_music/")

print(f"Files parsed successfully: {quality_report.success_rate:.1%}")
print(f"Average parsing accuracy: {quality_report.accuracy_mean:.2f}")
print(f"Files requiring manual review: {len(quality_report.flagged_files)}")
```

### Format Conversion Accuracy

```python
from pyw.musicparser import ConversionTester

# Test round-trip conversion accuracy
tester = ConversionTester()

# MIDI → MusicXML → MIDI
accuracy = tester.test_roundtrip(
    input_file="original.mid",
    intermediate_format="xml",
    metrics=["pitch", "rhythm", "dynamics", "articulation"]
)

print(f"Pitch accuracy: {accuracy.pitch:.2%}")
print(f"Rhythm accuracy: {accuracy.rhythm:.2%}")
print(f"Overall fidelity: {accuracy.overall:.2%}")
```

## CLI Tools

```bash
# Parse single file with features
pyw-musicparser parse song.mid --extract-features --output=analysis.json

# Batch processing
pyw-musicparser batch music_dir/ --formats=mid,xml --workers=8 --progress

# Format conversion
pyw-musicparser convert input.mid --to=xml --output=output.xml

# Feature extraction only
pyw-musicparser features *.mid --harmonic --melodic --export=csv

# Quality check
pyw-musicparser validate score.xml --comprehensive --report=html

# Audio to MIDI conversion
pyw-musicparser audio2midi recording.wav --polyphonic --clean

# Database operations
pyw-musicparser db import music_collection/ --extract-features
pyw-musicparser db query --composer="Bach" --key="C major" --export=csv

# Analysis tools
pyw-musicparser analyze piece.mid --chord-progressions --style-classification
pyw-musicparser similarity song1.mid song2.mid --features=harmonic,melodic
```

## Testing Support

```python
from pyw.musicparser.testing import (
    create_test_score, assert_parsing_accuracy,
    mock_parser, benchmark_parser
)

def test_midi_parsing():
    # Generate test MIDI
    test_midi = create_test_score(
        duration=30,  # seconds
        complexity="medium",
        instruments=["piano", "violin"],
        style="classical"
    )
    
    # Test parsing
    parsed = parse(test_midi)
    
    # Assertions
    assert_parsing_accuracy(test_midi, parsed, threshold=0.95)
    assert len(parsed.parts) == 2
    assert parsed.duration == pytest.approx(30, rel=0.1)

# Performance benchmarking
@benchmark_parser
def test_large_file_performance():
    large_midi = create_test_score(duration=600, complexity="high")
    result = parse(large_midi, extract_features=True)
    return result

# Mock parser for testing
with mock_parser(fake_features={
    "key": "C major", "tempo": 120, "duration": 180
}) as parser:
    result = parser.parse("test.mid")
    assert result.features.key == "C major"
```

## Examples

### Automatic Chord Chart Generation

```python
from pyw.musicparser import ChordChartGenerator

# Generate chord charts from any format
generator = ChordChartGenerator(
    chord_detection="advanced",
    simplify_chords=True,      # Convert complex chords to simpler forms
    add_bass_notes=True,       # Include bass line information
    format_style="lead_sheet"  # Or "roman_numeral", "nashville"
)

# Parse and generate chord chart
score = parse("jazz_standard.mid")
chord_chart = generator.generate(score)

print("Chord Chart:")
for section in chord_chart.sections:
    print(f"\n[{section.name}]")
    for measure in section.measures:
        chords_str = " | ".join([f"{c.symbol}({c.duration})" for c in measure.chords])
        print(f"  {measure.number:2d}: {chords_str}")

# Export in multiple formats
chord_chart.export("chart.txt", format="text")
chord_chart.export("chart.json", format="json") 
chord_chart.export("chart.ly", format="lilypond")
```

### Music Theory Analysis

```python
from pyw.musicparser import TheoryAnalyzer

# Deep music theory analysis
analyzer = TheoryAnalyzer(
    analyze_form=True,          # Sonata, rondo, etc.
    analyze_harmony=True,       # Functional harmony
    analyze_counterpoint=True,  # Voice leading rules
    analyze_style=True         # Style period classification
)

analysis = analyzer.analyze("fugue.mid")

# Form analysis
print(f"Musical form: {analysis.form.type}")
print("Sections:")
for section in analysis.form.sections:
    print(f"  {section.name}: measures {section.start}-{section.end}")

# Harmonic analysis
print("\nKey areas:")
for key_area in analysis.harmony.key_areas:
    print(f"  {key_area.key}: measures {key_area.measures}")

print(f"\nCadences found: {len(analysis.harmony.cadences)}")
for cadence in analysis.harmony.cadences:
    print(f"  {cadence.type} in {cadence.key} at measure {cadence.measure}")

# Counterpoint analysis
print(f"\nVoice leading quality: {analysis.counterpoint.quality_score:.2f}")
if analysis.counterpoint.violations:
    print("Voice leading issues:")
    for violation in analysis.counterpoint.violations:
        print(f"  {violation.type} at measure {violation.measure}")
```

### Educational Tools

```python
from pyw.musicparser import EducationalAnalyzer

# Educational music analysis
educator = EducationalAnalyzer(
    difficulty_assessment=True,
    learning_objectives=True,
    practice_suggestions=True
)

# Analyze piece for educational purposes
assessment = educator.assess("student_piece.mid")

print(f"Difficulty level: {assessment.difficulty.level}")
print(f"Technical challenges:")
for challenge in assessment.difficulty.challenges:
    print(f"  - {challenge.skill}: {challenge.description}")

print(f"\nLearning objectives:")
for objective in assessment.learning_objectives:
    print(f"  - {objective.category}: {objective.description}")

print(f"\nPractice suggestions:")
for suggestion in assessment.practice_suggestions:
    print(f"  - {suggestion.type}: {suggestion.instruction}")

# Generate practice exercises
exercises = educator.generate_exercises(assessment, 
    focus_areas=["rhythm", "harmony"],
    difficulty="progressive"
)
```

## Roadmap

- 🤖 **AI-Powered Analysis**: Machine learning per style recognition e auto-harmonization
- 🎤 **Vocal Analysis**: Lyrics alignment, vocal technique analysis  
- 🎸 **Tablature Support**: Guitar/bass tab parsing e generation
- 📱 **Real-time Processing**: Streaming MIDI analysis per live performance
- 🔄 **Advanced Conversion**: Lossless format conversion con preservation di ogni dettaglio
- 🎯 **Educational Features**: Interactive music theory lessons, ear training
- 🌐 **Web Integration**: REST API per music analysis as a service
- 📊 **Big Data**: Distributed processing per large music corpora

## Architecture

```
pyw-musicparser/
├── pyw/
│   └── musicparser/
│       ├── __init__.py          # Public API
│       ├── core/
│       │   ├── parser.py        # Base parser classes
│       │   ├── score.py         # MusicScore data model
│       │   ├── features.py      # Feature extraction engine
│       │   └── formats.py       # Format detection/routing
│       ├── parsers/
│       │   ├── midi.py         # MIDI parser
│       │   ├── musicxml.py     # MusicXML parser  
│       │   ├── lilypond.py     # Lilypond parser
│       │   ├── abc.py          # ABC notation parser
│       │   ├── kern.py         # Kern parser
│       │   └── audio.py        # Audio-to-MIDI parser
│       ├── features/
│       │   ├── harmonic.py     # Harmonic analysis
│       │   ├── rhythmic.py     # Rhythmic analysis
│       │   ├── melodic.py      # Melodic analysis
│       │   └── statistical.py # Statistical features
│       ├── analysis/
│       │   ├── theory.py       # Music theory analysis
│       │   ├── style.py        # Style classification
│       │   └── quality.py      # Quality assessment
│       ├── export/
│       │   ├── formats.py      # Export format handlers
│       │   ├── database.py     # Database integration
│       │   └── visualization.py # Analysis visualization
│       └── cli/                # Command line interface
└── tests/                      # Comprehensive test suite
```

## Contributing

1. **Fork & Clone**: `git clone https://github.com/pythonWoods/pyw-musicparser.git`
2. **Development setup**: `poetry install --with dev && poetry shell`
3. **Install extras**: `poetry install --extras "audio lilypond"`
4. **Quality checks**: `ruff check . && mypy && pytest --cov`
5. **Test with real files**: Usa il dataset in `tests/fixtures/music/`
6. **Music theory accuracy**: Validate contro ground truth in `tests/theory_tests/`
7. **Performance testing**: `pytest --benchmark-only` per regression testing
8. **Documentation**: Include esempi musicali e use cases
9. **Pull Request**: Include test files musicali e coverage report

Libera la potenza dell'analisi musicale con **pythonWoods**! 🌲🎵

## Links utili

Documentazione dev (work-in-progress) → https://pythonwoods.dev/docs/pyw-musicparser/latest/

Issue tracker → https://github.com/pythonWoods/pyw-musicparser/issues

Changelog → https://github.com/pythonWoods/pyw-musicparser/releases

© pythonWoods — MIT License