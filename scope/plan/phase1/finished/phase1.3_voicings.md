# Phase 1.3: MIDI Class Defaults & Scale Quantization

## Overview

Extend `ts.MIDI` to accept default attributes that propagate to child methods like `.n()`. This establishes the architectural foundation for inheritable parameters.

---

## Core Behavior: Two Modes

### Mode 1: No Scale (Chromatic / Piano Roll)

When no `scale` is set, numbers are **semitone offsets from the incoming voice** (current behavior):

```python
midi = ts.MIDI(v)  # v.note = 64 (E4)
midi.n("0 3 5 7")  # E4, G4, A4, B4 (semitone offsets: +0, +3, +5, +7)
```

This matches traditional piano roll / MIDI behavior.

### Mode 2: With Scale (Scale Degree Indices)

When `scale` is set, numbers are **0-indexed scale degree indices**. The number selects which note in the scale to play:

```python
midi = ts.MIDI(v, scale="c5:major")  # C major = [C, D, E, F, G, A, B]

midi.n("0 1 2")    # C5, D5, E5 (first 3 notes of C major)
midi.n("0 2 4")    # C5, E5, G5 (degrees 1, 3, 5 = major triad)
midi.n("0 2 4 6")  # C5, E5, G5, B5 (degrees 1, 3, 5, 7 = maj7 chord)
```

| Degree Index | C Major Note | Scale Degree Name |
|--------------|--------------|-------------------|
| 0 | C | Root (1st) |
| 1 | D | 2nd |
| 2 | E | 3rd |
| 3 | F | 4th |
| 4 | G | 5th |
| 5 | A | 6th |
| 6 | B | 7th |
| 7 | C (next octave) | Root (8th) |

The **incoming voice is ignored for pitch** when scale is active. It's still used for:
- Velocity inheritance
- Parent voice lifecycle (`stop_patterns_for_voice`)
- Other parameters (pan, output, etc.)

### Note Names vs Numbers

| Input Type | Behavior with Scale |
|------------|---------------------|
| **Numbers** (`0`, `2`, `4`) | Scale degree indices — selects which note in the scale |
| **Note names** (`"c4"`, `"e4"`) | Quantized to nearest scale note |

```python
midi = ts.MIDI(v, scale="c5:minor")

# Numbers = scale degree indices
midi.n("0 2 4")      # C5, Eb5, G5 (degrees 1, 3, 5 of C minor)

# Note names = quantized to scale
midi.n("c4 e4 g4")   # C4, Eb4, G4 (e4 snaps to eb4 in C minor)
```

---

## Proposed API

```python
# MIDI instance with defaults
midi = ts.MIDI(incomingVoice, c=0.75, scale="c5:minor")

# .n() inherits defaults from parent MIDI
midi.n("0 2 4 6")              # c=0.75, plays C5 Eb5 G5 Bb5 (minor 7th chord)
midi.n("0 2 4 6", c=1)         # c overridden to 1, still C minor
midi.n("0 2 4 6", scale="d5:dorian")  # scale overridden to D dorian
```

### Scale String Format

```
"<root>[octave]:<scale_name>"

Examples:
  "c:major"     → root=C3 (MIDI 48), default octave 3
  "c5:major"    → root=C5 (MIDI 72)
  "a4:minor"    → root=A4 (MIDI 69)
  "f#5:blues"   → root=F#5 (MIDI 78)
  "bb3:dorian"  → root=Bb3 (MIDI 58)
```

### Color-Based Routing Example

```python
def onTriggerVoice(incomingVoice):
    if incomingVoice.color == 0:
        midi = ts.MIDI(incomingVoice, c=0.75, scale="c4:major")
        midi.n("0 2 4 6")  # C4 E4 G4 B4 (Cmaj7)

    if incomingVoice.color == 1:
        midi = ts.MIDI(incomingVoice, c=0.75, scale="a3:minor")
        midi.n("0 2 4 6", c=1)  # A3 C4 E4 G4 (Am7)
```

---

## Registry Pattern: `ts.scales`, `ts.notes`, `ts.chords`

Dictionaries are exposed via a unified registry pattern that supports inspection and extension.

### Registry Class

```python
class _Registry:
    """A dict-like container that prints nicely and supports .add()"""
    
    def __init__(self, name, data):
        self._name = name
        self._data = data
    
    def __repr__(self):
        """When you type `ts.scales` in REPL, show the contents."""
        items = ', '.join(sorted(self._data.keys()))
        return f"<{self._name}: {items}>"
    
    def __getitem__(self, key):
        """Allow ts.scales['major'] access."""
        return self._data.get(key.lower())
    
    def __contains__(self, key):
        """Allow 'major' in ts.scales."""
        return key.lower() in self._data
    
    def __iter__(self):
        """Allow for scale in ts.scales."""
        return iter(self._data.keys())
    
    def add(self, name, value):
        """Add a custom entry."""
        self._data[name.lower()] = value
    
    def list(self):
        """Return list of all names."""
        return list(self._data.keys())
    
    def get(self, key, default=None):
        """Dict-like get with default."""
        return self._data.get(key.lower(), default)
```

### Usage

```python
# Print available (in REPL or via print())
ts.scales        # <scales: major, minor, dorian, phrygian, ...>
ts.notes         # <notes: c, c#, d, d#, e, f, ...>
ts.chords        # <chords: , m, 7, m7, maj7, ...>

# Access values
ts.scales['major']       # [0, 2, 4, 5, 7, 9, 11]
ts.notes['c#']           # 1
ts.chords['m7']          # [0, 3, 7, 10]

# Check existence
'dorian' in ts.scales    # True
'bebop' in ts.scales     # False

# Iterate
for scale_name in ts.scales:
    print(scale_name)

# List all
ts.scales.list()         # ['major', 'minor', 'dorian', ...]

# Add custom
ts.scales.add('bebop', [0, 2, 4, 5, 7, 9, 10, 11])
ts.chords.add('add9', [0, 4, 7, 14])

# Then use it
midi = ts.MIDI(v, scale="c4:bebop")
```

---

## MIDI Class Changes

```python
class MIDI(vfx.Voice):
    def __init__(self, incomingVoice, c=4, scale=None):
        super().__init__(incomingVoice)
        self.parentVoice = incomingVoice
        self._c = c                    # Default cycle beats
        self._scale = None             # Scale intervals (e.g., [0,2,3,5,7,8,10])
        self._scale_root = None        # Scale root as MIDI note (e.g., 72 for C5)
        
        if scale:
            self._scale, self._scale_root = _parse_scale(scale)
```

### `_midi_n()` Inheritance

```python
def _midi_n(self, pattern_str, c=None, scale=None, mute=False, bus=None):
    # Inherit from MIDI instance if not overridden
    cycle_beats = c if c is not None else self._c
    
    # Parse scale if provided at .n() level, else inherit from MIDI
    if scale is not None:
        active_scale, active_scale_root = _parse_scale(scale)
    else:
        active_scale = self._scale
        active_scale_root = self._scale_root
    
    # Determine pattern root
    if active_scale is not None:
        # Scale mode: root is the scale root
        pattern_root = active_scale_root
    else:
        # Chromatic mode: root is incoming voice note
        pattern_root = self.note
    
    # ... rest of pattern creation with pattern_root
```

---

## Scale System

### Scales Registry

```python
scales = _Registry('scales', {
    # Modal (7-note)
    'major':      [0, 2, 4, 5, 7, 9, 11],   # Ionian
    'minor':      [0, 2, 3, 5, 7, 8, 10],   # Natural minor / Aeolian
    'dorian':     [0, 2, 3, 5, 7, 9, 10],
    'phrygian':   [0, 1, 3, 5, 7, 8, 10],
    'lydian':     [0, 2, 4, 6, 7, 9, 11],
    'mixolydian': [0, 2, 4, 5, 7, 9, 10],
    'locrian':    [0, 1, 3, 5, 6, 8, 10],
    
    # Pentatonic
    'pentatonic':       [0, 2, 4, 7, 9],
    'minor_pentatonic': [0, 3, 5, 7, 10],
    
    # Blues
    'blues': [0, 3, 5, 6, 7, 10],
    
    # Harmonic/Melodic
    'harmonic_minor': [0, 2, 3, 5, 7, 8, 11],
    'melodic_minor':  [0, 2, 3, 5, 7, 9, 11],
    
    # Chromatic (all 12 notes)
    'chromatic': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
})
```

### Notes Registry

```python
notes = _Registry('notes', {
    'c': 0, 'c#': 1, 'db': 1,
    'd': 2, 'd#': 3, 'eb': 3,
    'e': 4, 'fb': 4, 'e#': 5,
    'f': 5, 'f#': 6, 'gb': 6,
    'g': 7, 'g#': 8, 'ab': 8,
    'a': 9, 'a#': 10, 'bb': 10,
    'b': 11, 'cb': 11, 'b#': 0,
})
```

### Chords Registry (for Phase 1.4)

```python
chords = _Registry('chords', {
    '':     [0, 4, 7],           # Major triad
    'm':    [0, 3, 7],           # Minor triad
    'dim':  [0, 3, 6],           # Diminished
    'aug':  [0, 4, 8],           # Augmented
    '7':    [0, 4, 7, 10],       # Dominant 7
    'maj7': [0, 4, 7, 11],       # Major 7
    'm7':   [0, 3, 7, 10],       # Minor 7
    'dim7': [0, 3, 6, 9],        # Diminished 7
    # ... more in Phase 1.4
})
```

---

## Parsing Functions

```python
def _parse_note_with_octave(note_str, default_octave=3):
    """
    Parse note string to MIDI number.
    
    Examples:
        "c"   → 48 (C3, default octave)
        "c5"  → 72 (C5)
        "f#4" → 66 (F#4)
        "bb3" → 58 (Bb3)
    """
    note_str = note_str.lower().strip()
    
    # Extract note name and octave
    import re
    match = re.match(r'^([a-g][#b]?)(-?\d)?$', note_str)
    if not match:
        raise ValueError(f"Invalid note: {note_str}")
    
    note_name = match.group(1)
    octave = int(match.group(2)) if match.group(2) else default_octave
    
    chroma = notes.get(note_name)  # Uses notes registry
    if chroma is None:
        raise ValueError(f"Unknown note name: {note_name}")
    
    return (octave + 1) * 12 + chroma  # MIDI: C4 = 60


def _parse_scale(scale_str):
    """
    Parse scale string into (intervals, root_midi).
    
    Examples:
        "c:major"    → ([0,2,4,5,7,9,11], 48)   # C3 default
        "c5:major"   → ([0,2,4,5,7,9,11], 72)   # C5
        "a4:minor"   → ([0,2,3,5,7,8,10], 69)   # A4
        "f#5:blues"  → ([0,3,5,6,7,10], 78)     # F#5
    """
    parts = scale_str.lower().split(':')
    if len(parts) != 2:
        raise ValueError(f"Invalid scale format: {scale_str}. Use 'root:scale' (e.g., 'c5:major')")
    
    root_str, scale_name = parts
    
    intervals = scales.get(scale_name)  # Uses scales registry
    if intervals is None:
        raise ValueError(f"Unknown scale: {scale_name}. Available: {scales.list()}")
    
    root_midi = _parse_note_with_octave(root_str, default_octave=3)
    
    return intervals, root_midi
```

---

## Scale Degree Calculation

When scale is active, convert pattern numbers to MIDI notes:

```python
def _scale_degree_to_midi(degree, scale_intervals, scale_root):
    """
    Convert a scale degree index (0-indexed) to MIDI note.
    
    Args:
        degree: Scale degree index (0 = root, 1 = 2nd note, 2 = 3rd note, etc.)
                Negative values go below root. Values >= len(scale) wrap octaves.
        scale_intervals: List of semitone offsets [0, 2, 4, 5, 7, 9, 11]
        scale_root: MIDI note of scale root (e.g., 72 for C5)
    
    Returns:
        MIDI note number
    
    Examples (C major scale, root=60):
        degree=0  → 60 (C4) - 1st note
        degree=1  → 62 (D4) - 2nd note
        degree=2  → 64 (E4) - 3rd note
        degree=6  → 71 (B4) - 7th note
        degree=7  → 72 (C5) - wraps to next octave
        degree=-1 → 59 (B3) - below root
    """
    num_degrees = len(scale_intervals)
    
    # Handle octave wrapping
    octave_offset = degree // num_degrees
    degree_in_scale = degree % num_degrees
    
    # Handle negative degrees (Python's % handles this correctly)
    if degree < 0 and degree_in_scale != 0:
        octave_offset -= 1
        degree_in_scale = num_degrees + degree_in_scale
    
    semitone_offset = scale_intervals[degree_in_scale]
    return scale_root + semitone_offset + (octave_offset * 12)
```

---

## Note Name Quantization

When using note names (e.g., `"c4 e4 g4"`) with a scale, they are **quantized to the nearest scale note**:

```python
midi = ts.MIDI(v, scale="c5:minor")
midi.n("c4 e4 g4")  # e4 → eb4 (quantized to C minor)
```

This uses the `_quantize_to_scale()` function (Strudel's approach):

```python
def _quantize_to_scale(midi_note, scale_intervals, scale_root, prefer_higher=False):
    """
    Quantize a MIDI note to the nearest note in the scale.
    """
    # Build scale notes across octaves
    all_scale_notes = []
    for octave in range(-1, 10):  # Cover MIDI range
        for interval in scale_intervals:
            note = scale_root + interval + (octave * 12)
            if 0 <= note <= 127:
                all_scale_notes.append(note)
    
    # Find nearest
    best_note = scale_root
    best_diff = float('inf')
    for scale_note in all_scale_notes:
        diff = abs(scale_note - midi_note)
        if diff < best_diff or (prefer_higher and diff == best_diff):
            best_note = scale_note
            best_diff = diff
    
    return best_note
```

---

## Common Chord Patterns Reference

With scale degree indices, building chords is intuitive:

| Pattern | Chord Type | Example (C major) |
|---------|------------|-------------------|
| `"0 2 4"` | Triad | C E G |
| `"0 2 4 6"` | 7th chord | C E G B |
| `"0 2 4 6 8"` | 9th chord | C E G B D |
| `"0 1 2 3 4 5 6"` | Full scale | C D E F G A B |

For minor scale (`scale="a4:minor"`):

| Pattern | Chord Type | Example (A minor) |
|---------|------------|-------------------|
| `"0 2 4"` | Minor triad | A C E |
| `"0 2 4 6"` | Minor 7th | A C E G |

---

## Implementation Steps

### Phase 1.3a: Registry Infrastructure

1. [ ] Implement `_Registry` class
2. [ ] Create `scales` registry with built-in scales
3. [ ] Create `notes` registry with note-to-chroma mapping
4. [ ] Create `chords` registry (basic, for Phase 1.4)

### Phase 1.3b: MIDI Class Defaults

5. [ ] Extend `MIDI.__init__` with `c` parameter
6. [ ] Update `_midi_n()` to inherit `c` from MIDI instance
7. [ ] Test: `midi = ts.MIDI(v, c=2); midi.n("0 1 2 3")` uses c=2

### Phase 1.3c: Scale Infrastructure

8. [ ] Add `_parse_note_with_octave(note_str)` function (uses `notes` registry)
9. [ ] Add `_parse_scale(scale_str)` function (uses `scales` registry)
10. [ ] Add `_scale_degree_to_midi(degree, intervals, root)` function

### Phase 1.3d: Scale Integration

11. [ ] Extend `MIDI.__init__` with `scale` parameter
12. [ ] Update `_midi_n()` to:
    - Inherit `scale` from MIDI instance
    - Use scale root as pattern root when scale is set
    - Use incoming voice as pattern root when no scale
13. [ ] Update pattern note resolution to use `_scale_degree_to_midi()` when scale is active
14. [ ] Add `_quantize_to_scale()` for absolute note names

### Phase 1.3e: Testing

15. [ ] Test chromatic mode (no scale) — existing behavior unchanged
16. [ ] Test scale mode — numbers as scale degree indices
17. [ ] Test octave in scale string (`c5:major` vs `c:major`)
18. [ ] Test scale override at `.n()` level
19. [ ] Test absolute notes with scale (quantization)
20. [ ] Test custom scales via `ts.scales.add()`

---

## Test Cases

```python
# === Registry Access ===
ts.scales                # <scales: major, minor, dorian, ...>
ts.scales['major']       # [0, 2, 4, 5, 7, 9, 11]
ts.scales.list()         # ['major', 'minor', ...]
'dorian' in ts.scales    # True

ts.notes                 # <notes: c, c#, d, ...>
ts.notes['c#']           # 1

# === Custom Scale ===
ts.scales.add('bebop', [0, 2, 4, 5, 7, 9, 10, 11])
midi = ts.MIDI(v, scale="c4:bebop")
midi.n("0 1 2 3 4 5 6 7")  # C4 D4 E4 F4 G4 A4 Bb4 B4

# === Chromatic Mode (no scale) ===
midi = ts.MIDI(v)  # v.note = 64 (E4)
midi.n("0 3 5 7")  # E4, G4, A4, B4 (semitone offsets)

# === Scale Mode: Basic ===
midi = ts.MIDI(v, scale="c5:major")
midi.n("0 1 2")    # C5, D5, E5 (first 3 notes of scale)
midi.n("0 2 4")    # C5, E5, G5 (major triad)
midi.n("0 2 4 6")  # C5, E5, G5, B5 (maj7)

# === Scale Mode: Minor ===
midi = ts.MIDI(v, scale="a4:minor")
midi.n("0 1 2")    # A4, B4, C5 (first 3 notes of A minor)
midi.n("0 2 4")    # A4, C5, E5 (minor triad)
midi.n("0 2 4 6")  # A4, C5, E5, G5 (Am7)

# === Scale with different octave ===
midi = ts.MIDI(v, scale="c3:major")
midi.n("0 2 4")    # C3, E3, G3

# === Default octave (3) ===
midi = ts.MIDI(v, scale="c:major")
midi.n("0 2 4")    # C3, E3, G3

# === Inheritance ===
midi = ts.MIDI(v, c=2, scale="c5:major")
midi.n("0 2 4")        # c=2, C5 E5 G5
midi.n("0 2 4", c=4)   # c=4 (overridden), C5 E5 G5

# === Scale Override ===
midi = ts.MIDI(v, scale="c5:major")
midi.n("0 2 4", scale="a4:minor")  # A4, C5, E5 (overrides to A minor)

# === Negative degrees ===
midi = ts.MIDI(v, scale="c5:major")
midi.n("-1 0 1")  # B4, C5, D5 (below root, root, 2nd)

# === Octave wrapping ===
midi = ts.MIDI(v, scale="c4:major")  # 7-note scale
midi.n("7 8 9")  # C5, D5, E5 (wraps to next octave)

# === Note names with scale (quantization) ===
midi = ts.MIDI(v, scale="c5:minor")
midi.n("c4 e4 g4")  # C4, Eb4, G4 (e4 quantized to eb4)

# === Pentatonic (5-note scale) ===
midi = ts.MIDI(v, scale="c4:pentatonic")  # [C, D, E, G, A]
midi.n("0 1 2 3 4")  # C4, D4, E4, G4, A4
midi.n("5 6")        # C5, D5 (wraps to next octave)
```

---

## Shared Components (for Phase 1.4 Chord Symbols)

These components will be reused by chord symbol parsing:

| Component | Phase 1.3 Use | Phase 1.4 Use |
|-----------|---------------|---------------|
| `_Registry` class | `scales`, `notes` | `chords`, voicings |
| `notes` registry | Scale root parsing | Chord root parsing |
| `_parse_note_with_octave()` | Scale root | Chord root |
| `scales` registry | Scale intervals | — |
| `chords` registry | — | Chord intervals |
| `_quantize_to_scale()` | Note quantization | Optional voicing quantization |

---

## References

- Strudel `tonal.mjs` — Scale handling, `scaleStep()` function (line 36-45)
- Strudel `tonleiter.mjs` — `stepInNamedScale()`, `nearestNumberIndex()`
- `@tonaljs/tonal` — External library Strudel uses (we embed equivalent)

---

## Future Ideas

- Allow `bpm` parameter on `ts.MIDI` that converts to `c` internally
- `bpm` and `c` would be mutually exclusive
- Would require `ts.Context.bpm` or similar for project tempo access
