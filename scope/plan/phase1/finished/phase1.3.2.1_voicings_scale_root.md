# Phase 1.3.2.1: Explicit Scale Root Behavior

## Problem

Currently, `scale("c5:major")` sets the scale root to C5 (MIDI 72), but `n("0")` still plays the incoming voice's scale degree, not C5. The octave in the scale string affects internal calculations but doesn't provide an intuitive way to say "degree 0 = this specific note."

Users expect:
- `scale("c5:major")` with `n("0")` → plays C5
- `scale("a4:minor")` with `n("0")` → plays A4

## Solution

Distinguish between **explicit** and **implicit** scale roots:

| Scale String | Root Type | `n("0")` Plays | Use Case |
|-------------|-----------|----------------|----------|
| `a:minor` | Implicit | Incoming voice's scale degree | Relative/reactive patterns |
| `a4:minor` | Explicit | A4 (MIDI 69) | Absolute/compositional patterns |

### Behavior Details

**Implicit root (`a:minor`):**
- Default octave = C4 (MIDI 60) for internal calculations
- `_base_degree` = incoming voice's position in scale
- `n("0")` = incoming voice's snapped note
- Current behavior, unchanged

**Explicit root (`a4:minor`):**
- `_base_degree` = 0 (ignore incoming voice position)
- `n("0")` = A4 (the explicit root)
- `n("2")` = C5 (3rd degree of A minor)

### Letter Names (Edge Case)

Letter names like `n("c4")` always snap to nearest scale tone regardless of root type:
- `scale("a4:minor")` with `n("c4")` → C4 snapped to A minor → C4 (it's in the scale)
- `scale("a4:minor")` with `n("c#4")` → C#4 snapped to A minor → C4 or D4

No change needed for letter handling.

## Implementation

### 1. Modify `_parse_scale()` Return Value

```python
def _parse_scale(scale_str):
    """
    Parse scale string into (intervals, root_midi, is_explicit).
    
    Examples:
        "c:major"    -> ([0,2,4,5,7,9,11], 60, False)   # C4 default, implicit
        "c5:major"   -> ([0,2,4,5,7,9,11], 72, True)    # C5, explicit
        "a4:minor"   -> ([0,2,3,5,7,8,10], 69, True)    # A4, explicit
    """
    parts = scale_str.lower().split(':')
    if len(parts) != 2:
        raise ValueError(f"Invalid scale format: {scale_str}. Use 'root:scale' (e.g., 'c5:major')")
    
    root_str, scale_name = parts
    
    intervals = scales.get(scale_name)
    if intervals is None:
        raise ValueError(f"Unknown scale: {scale_name}. Available: {scales.list()}")
    
    # Detect explicit octave: any digit in root_str
    has_explicit_octave = any(c.isdigit() for c in root_str)
    
    # Default octave is now 4 (middle C region)
    root_midi = _note_to_midi(root_str, default_octave=4)
    
    return intervals, root_midi, has_explicit_octave
```

### 2. Store Flag in PatternChain

```python
class PatternChain:
    def __init__(self, ...):
        # ... existing ...
        self._scale_explicit = False  # Whether scale root is explicit
```

### 3. Update MIDI._setup_chain() (line ~2770)

```python
# In MIDI.__init__ or _setup_chain
if scale:
    active_scale, active_scale_root, is_explicit = _parse_scale(scale)
    chain._scale = active_scale
    chain._scale_root = active_scale_root
    chain._scale_explicit = is_explicit
    
    if is_explicit:
        # Explicit root: degree 0 = scale root, ignore incoming voice
        chain._root = active_scale_root
        chain._base_degree = 0
    else:
        # Implicit root: degree 0 = incoming voice's position (current behavior)
        snapped_note = _quantize_to_scale(self.note, active_scale, active_scale_root)
        chain._root = snapped_note
        chain._base_degree = _midi_to_scale_degree(self.note, active_scale, active_scale_root)
```

### 4. Update All `_parse_scale()` Call Sites

Search for `_parse_scale(` and update to handle 3-tuple return:

| Location | Line | Context | Change |
|----------|------|---------|--------|
| `Single.__init__` | ~259 | Scale parsing for Single notes | Handle 3-tuple, store `_scale_explicit` |
| `MIDI.note()` | ~2753 | Scale parsing for `.n()` patterns | Handle 3-tuple, apply explicit/implicit logic |

Note: `_update_midi_patterns` (line ~2865) doesn't call `_parse_scale()` — it uses cached scale values from the PatternChain.

## Compatibility with ts.comp() (Phase 1.3.3)

This change aligns well with `ts.comp()`:

```python
# ts.comp() has no incoming voice, so explicit root is natural:
pat = ts.comp(scale="a4:minor")
pat.n("0 2 4")  # Plays A4, C5, E5

# With implicit scale, ts.comp() uses its root= parameter:
pat = ts.comp(scale="a:minor", root="c4")
pat.n("0 2 4")  # Plays C4's position in A minor
```

The `_CompContext._resolve_root()` template method will use `is_explicit` to decide:
- Explicit scale root → use scale root directly
- Implicit scale root → use `root=` parameter (required for ts.comp, derived for ts.MIDI)

## Test Cases

```python
# Test 1: Implicit root (current behavior)
midi = ts.MIDI(incomingVoice, scale="c:major")  # incoming = E4 (64)
midi.n("0")  # Should play E4 (degree 2 in C major)

# Test 2: Explicit root
midi = ts.MIDI(incomingVoice, scale="c4:major")  # incoming = E4 (64)
midi.n("0")  # Should play C4 (60), not E4

# Test 3: Explicit root with offset
midi = ts.MIDI(incomingVoice, scale="c5:major")
midi.n("0 2 4")  # Should play C5, E5, G5

# Test 4: Letter names unaffected
midi = ts.MIDI(incomingVoice, scale="a4:minor")
midi.n("c4")  # Should snap C4 to A minor → C4 (in scale)

# Test 5: Negative degrees with explicit root
midi = ts.MIDI(incomingVoice, scale="c4:major")
midi.n("-1")  # Should play B3 (one degree below C4)
```

## Checklist

- [ ] Update `_parse_scale()` to return `(intervals, root_midi, is_explicit)`
- [ ] Change default octave from 3 to 4 in `_parse_scale()`
- [ ] Add `_scale_explicit` attribute to `PatternChain`
- [ ] Update `MIDI` chain setup to use explicit flag
- [ ] Update all `_parse_scale()` call sites for 3-tuple
- [ ] Add test cases in `scope/test.py`
- [ ] Update README.md scale documentation
