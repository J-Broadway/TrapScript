# Phase 1.3.2: Scale-Relative Voice Quantization

## Problem Statement

Currently, when a scale is specified (e.g., `scale="c5:major"`), degree `0` in a pattern maps to the **scale root** (C5=72), ignoring the incoming voice's note entirely. This is incorrect behavior.

**Expected behavior:**
- The scale defines a **pitch grid** (which notes are valid)
- Degree `0` = the incoming voice note, **quantized/snapped** to the nearest scale degree
- Degree `1`, `2`, etc. = subsequent scale steps up from that snapped position
- Negative degrees = scale steps below

This means `"c5:major"` and `"c:major"` should behave identically for `midi.n()` — the octave in the scale spec is meaningless because the octave is determined by the incoming voice.

---

## How Strudel Handles This

Strudel has **two separate concepts** (see `tonleiter.mjs:stepInNamedScale`):

### 1. Scale Root (in scale name)
- `"C:major"` vs `"C5:major"` — the octave sets the **default octave** for step 0 when no anchor is provided
- Only the pitch class (C, D, F#, etc.) matters for defining which notes are in the scale

### 2. Anchor (optional parameter)
- When provided, step 0 becomes the scale degree **nearest to the anchor**
- The anchor repositions where "0" is in the scale
- Used in `.voicing(anchor='c5')` for chord voice leading

```javascript
// Strudel's stepInNamedScale (simplified)
if (anchor) {
  const anchorChroma = midi2chroma(anchor);
  const anchorDiff = _mod(anchorChroma - rootChroma, 12);
  const zeroIndex = nearestNumberIndex(anchorDiff, steps);
  step = step + zeroIndex;  // offset step by anchor's position in scale
  transpose = anchor - anchorDiff;
}
```

### Key Difference: TrapScript Has Incoming Voices

Strudel patterns are self-contained — there's no "incoming MIDI note" concept. In TrapScript's `midi.n()`, the **incoming voice IS effectively the anchor**.

This means:

| Context | Step 0 = | Octave in scale spec |
|---------|----------|---------------------|
| Strudel `n("0").scale("C5:major")` | C5 (scale root) | **Matters** — sets default octave |
| Strudel with anchor | Nearest to anchor | Ignored (anchor determines register) |
| TrapScript `ts.n("0")` | Scale root | **Matters** — no incoming voice |
| TrapScript `midi.n("0")` | Incoming voice (snapped) | **Ignored** — incoming voice is implicit anchor |

### Implication for TrapScript

- For `midi.n()`: `scale="c:major"` and `scale="c5:major"` are equivalent
- For `ts.n()`: The octave in scale spec matters (no incoming voice to anchor to)
- For `.voicing()`: The `anchor` parameter matters (separate from scale)

## Current Implementation

### Key Functions/Locations

1. **`_parse_scale(scale_str)`** (line ~1264)
   - Parses `"c5:major"` → `([0,2,4,5,7,9,11], 72)`
   - Returns `(intervals, root_midi)`
   - The `root_midi` is used as the fixed starting point (the bug)

2. **`_scale_degree_to_midi(degree, scale_intervals, scale_root)`** (line ~1289)
   - Converts degree index to MIDI note
   - Uses `scale_root` as base, adds interval offsets
   - `degree=0` → `scale_root` (currently C5=72 for `"c5:major"`)

3. **`_quantize_to_scale(midi_note, scale_intervals, scale_root)`** (line ~1318)
   - Snaps a MIDI note to nearest scale tone
   - Already exists and works correctly
   - **This is the key function we need to use**

4. **`MIDI.__init__`** (line ~248)
   - Stores `self._scale` (intervals) and `self._scale_root` (MIDI note)
   - Has access to `self.note` (the incoming voice's MIDI note)

5. **`_midi_n()` / `MIDI.n()`** (line ~2602)
   - Sets `chain._root`:
   ```python
   if active_scale is not None:
       chain._root = active_scale_root  # BUG: ignores incoming voice
   else:
       chain._root = self.note  # Correct for chromatic
   ```

6. **Pattern tick/trigger** (line ~2735)
   - Resolves note values:
   ```python
   if _mw_scale is not None:
       note_val = _scale_degree_to_midi(int(e.value), _mw_scale, _mw_scale_root)
   ```

## Required Changes

### 1. New Helper: `_midi_to_scale_degree()`

Add function to find which scale degree a MIDI note is closest to (inverse of `_scale_degree_to_midi`):

```python
def _midi_to_scale_degree(midi_note, scale_intervals, scale_root):
    """
    Find the scale degree index for a MIDI note (or nearest if not in scale).
    
    Args:
        midi_note: The MIDI note to find (e.g., 64 for E4)
        scale_intervals: List of semitone offsets [0, 2, 4, 5, 7, 9, 11]
        scale_root: MIDI note of scale root (e.g., 60 for C4)
    
    Returns:
        Scale degree index (0-indexed, can be negative or >= len(scale))
    
    Example (C major, root=60):
        midi=60 (C4) -> 0
        midi=64 (E4) -> 2  
        midi=72 (C5) -> 7
        midi=59 (B3) -> -1
    """
    # First quantize to ensure we're on a scale tone
    quantized = _quantize_to_scale(midi_note, scale_intervals, scale_root)
    
    # Calculate offset from root
    semitone_offset = quantized - scale_root
    octave_offset = semitone_offset // 12
    semitone_in_octave = semitone_offset % 12
    
    # Find which degree this semitone corresponds to
    num_degrees = len(scale_intervals)
    for i, interval in enumerate(scale_intervals):
        if interval == semitone_in_octave:
            return octave_offset * num_degrees + i
    
    # Fallback (shouldn't happen if quantize worked)
    return 0
```

### 2. Modify `_midi_n()` (line ~2648)

Change root calculation from scale-root to incoming-voice-snapped:

```python
# BEFORE (buggy):
if active_scale is not None:
    chain._root = active_scale_root  # Scale mode: root is scale root

# AFTER (fixed):
if active_scale is not None:
    # Snap incoming voice to scale, use as degree-0 reference
    snapped_note = _quantize_to_scale(self.note, active_scale, active_scale_root)
    chain._root = snapped_note
    # Store the snapped position's degree for offset calculations
    chain._base_degree = _midi_to_scale_degree(self.note, active_scale, active_scale_root)
```

### 3. Modify Pattern Note Resolution (line ~2743)

Change how scale degrees are resolved:

```python
# BEFORE:
note_val = _scale_degree_to_midi(int(e.value), _mw_scale, _mw_scale_root)

# AFTER:
# e.value is relative to the base degree (0 = snapped incoming note)
absolute_degree = chain._base_degree + int(e.value)
note_val = _scale_degree_to_midi(absolute_degree, _mw_scale, _mw_scale_root)
```

### 4. Simplify Scale Parsing (Context-Dependent)

The octave in scale spec should be handled differently based on context:

| Context | Octave behavior |
|---------|-----------------|
| `midi.n()` | Ignored — incoming voice determines register |
| `ts.n()` | Matters — no incoming voice, octave sets step 0 register |

**Option A: Ignore octave in `_parse_scale()`, only extract chroma**

```python
def _parse_scale(scale_str):
    """
    Parse scale string. Extracts intervals and root chroma (0-11).
    
    Examples:
        "major"      -> ([0,2,4,5,7,9,11], 0)   # C chroma
        "c:major"    -> ([0,2,4,5,7,9,11], 0)   # Same
        "d:dorian"   -> ([0,2,3,5,7,9,10], 2)   # D chroma
        "c5:major"   -> ([0,2,4,5,7,9,11], 0)   # Octave stripped, just C chroma
    """
```

Then `midi.n()` uses incoming voice + chroma, while `ts.n()` would need a separate default octave.

**Option B: Keep current parsing, handle octave differently per context**

Keep `_parse_scale()` returning full MIDI root. Then:
- `midi.n()`: Ignore the octave, use only chroma from scale root
- `ts.n()`: Use the full MIDI root as step 0

This is cleaner and maintains backward compat for `ts.n()`.

**Recommendation: Option B** — minimal changes, clear separation of concerns.

The key insight: the scale root letter (C, D, F#, etc.) only matters for **which chroma values are in the scale**. For `midi.n()`, the octave is determined by the incoming voice. For `ts.n()`, the octave in the scale spec sets the default register.

## Example Behavior After Fix

```python
# User plays E4 (MIDI 64)
midi = ts.MIDI(incomingVoice, scale="c:major")  # or "c5:major" - same result
midi.n("0 2 4")  

# Pattern plays:
# 0 -> E4 (64) - snapped incoming note (E is 3rd degree of C major)
# 2 -> G4 (67) - 2 scale steps up from E = G
# 4 -> B4 (71) - 4 scale steps up from E = B
```

```python
# User plays C#4 (MIDI 61) - not in C major scale
midi = ts.MIDI(incomingVoice, scale="c:major")
midi.n("0 1 2")

# Pattern plays:
# C#4 snaps to C4 or D4 (nearest) - let's say C4 (60)
# 0 -> C4 (60)
# 1 -> D4 (62)  
# 2 -> E4 (64)
```

## Files to Modify

1. **`trapscript.py`**
   - Add `_midi_to_scale_degree()` after `_quantize_to_scale()` (~line 1340)
   - Modify `_midi_n()` root calculation (~line 2648)
   - Add `_base_degree` to PatternChain storage
   - Modify pattern tick note resolution (~line 2743)
   - Optionally simplify `_parse_scale()` to ignore octave

2. **`README.md`**
   - Update scale documentation to reflect new behavior
   - Clarify that scale specifies the pitch grid, incoming voice determines register

## Testing

```python
# Test 1: Degree 0 should be the snapped incoming note
midi = ts.MIDI(incomingVoice, scale="c:major")  # incoming = E4 (64)
midi.n("0")  # Should play E4, not C3/C5

# Test 2: Degrees offset from snapped note
midi = ts.MIDI(incomingVoice, scale="c:major")  # incoming = G4 (67)
midi.n("0 1 2 -1")  # Should play G4, A4, B4, F4

# Test 3: Non-scale note snaps correctly
midi = ts.MIDI(incomingVoice, scale="c:major")  # incoming = F#4 (66)
midi.n("0")  # Should snap to F4 or G4 (nearest scale tone)

# Test 4: Octave in scale spec has no effect
midi1 = ts.MIDI(v, scale="c:major")
midi2 = ts.MIDI(v, scale="c5:major")
# Both should produce identical results
```

## Relationship to Chord Voicings (Phase 1.4)

The `anchor` parameter in `.voicing()` is **separate** from the scale spec:

| Concept | Purpose | Octave matters? |
|---------|---------|-----------------|
| Scale root in `scale="c:major"` | Defines pitch grid (which notes are valid) | No for `midi.n()`, Yes for `ts.n()` |
| Anchor in `.voicing(anchor='c5')` | Reference point for voice leading | **Yes** — determines chord register |

The chord voicing system uses anchor to position chords in a specific register for smooth voice leading. This is unrelated to the scale quantization fix.

Example:
```python
# Scale: octave ignored for midi.n() (incoming voice determines register)
midi = ts.MIDI(v, scale="c:major")
midi.n("0 2 4")  # Plays from incoming voice's register

# Chord anchor: octave matters (sets voicing register)
midi.chord("<Am C D F>").voicing(anchor='c5')  # Chords positioned near C5
```

## Backward Compatibility

This is a **breaking change** for existing scripts that relied on the old behavior where `scale="c5:major"` meant all patterns start from C5 regardless of incoming note.

However, the old behavior was arguably a bug — if you wanted fixed-pitch patterns independent of incoming voice, you should use `ts.n()` (standalone patterns) rather than `midi.n()`.

Consider adding a deprecation warning or a flag like `absolute=True` if backward compat is critical.
