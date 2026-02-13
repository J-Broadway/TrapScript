# Phase 1.3.3: ts.comp() — Standalone Pattern Context

## Problem

`ts.MIDI` provides OOP defaults (scale, c) that `.n()` inherits. `ts.n()` has no equivalent — it's stateless and doesn't support scales. This creates an architectural gap.

## Solution

Introduce `ts.comp()` — a standalone pattern context with the same OOP structure as `ts.MIDI`, minus voice binding.

## Scale Root Resolution (see Phase 1.3.2.1)

`ts.comp()` follows the explicit/implicit scale root behavior:

| Scale String | Root Resolution | Example |
|-------------|-----------------|---------|
| `a4:minor` (explicit) | Use scale root directly | `n("0")` → A4 |
| `a:minor` (implicit) | Use scale root as default | `n("0")` → A4 (default octave 4) |
| `a:minor` + `root="c4"` | Use `root=` param, snap to scale | `n("0")` → C4's degree in A minor |

**Key difference from ts.MIDI:** Since `ts.comp()` has no incoming voice, implicit scales default to the scale root (octave 4). The `root=` parameter is optional and only needed when you want degree 0 to be something other than the scale root.

```python
# Explicit scale — root= ignored, degree 0 = A4
ts.comp(scale="a4:minor").n("0")  # Plays A4

# Implicit scale — defaults to scale root (A4)
ts.comp(scale="a:minor").n("0")  # Plays A4

# Implicit scale with root override — degree 0 = C4's position
ts.comp(scale="a:minor", root="c4").n("0")  # Plays C4 (snapped, it's in scale)
```

## Design: Abstract Base Class + Template Method

```python
class _CompContext:
    """Base: shared defaults, scale handling, pattern creation."""
    
    def __init__(self, c=4, scale=None, root=None, v=1.0, pan=0.0, parent=None):
        # Store defaults, parse scale (returns is_explicit flag)
    
    def note(self, pattern_str, c=None, scale=None, ...) -> PatternChain:
        """Canonical method for pattern creation."""
        chain._root = self._resolve_root(scale_root, is_explicit)  # Template method
        self._on_pattern_created(chain)  # Template method
    
    n = note  # Alias (per alias_refactor.md)
    
    def _resolve_root(self, scale_root, is_explicit):
        raise NotImplementedError
    
    def _on_pattern_created(self, chain):
        pass  # Override for lifecycle behavior


class MIDI(vfx.Voice, _CompContext):
    """Voice-bound context. Auto-triggers, auto-releases."""
    
    def _resolve_root(self, scale_root, is_explicit):
        if is_explicit:
            # Explicit: degree 0 = scale root, ignore incoming voice
            return scale_root, 0  # (root, base_degree)
        else:
            # Implicit: degree 0 = incoming voice's position
            snapped = _quantize_to_scale(self.note, scale, scale_root)
            base_deg = _midi_to_scale_degree(self.note, scale, scale_root)
            return snapped, base_deg
    
    def _on_pattern_created(self, chain):
        # Auto-start, register for voice lifecycle


class Comp(_CompContext):
    """Standalone context. Manual trigger/release."""
    
    def __init__(self, c=4, scale=None, root=None, v=1.0, pan=0.0, parent=None):
        # root is optional (defaults to scale root if not provided)
    
    def _resolve_root(self, scale_root, is_explicit):
        if is_explicit:
            # Explicit: degree 0 = scale root, ignore root= param
            return scale_root, 0
        elif self._root_param is not None:
            # Implicit with root=: snap root param to scale
            snapped = _quantize_to_scale(self._root_param, scale, scale_root)
            base_deg = _midi_to_scale_degree(self._root_param, scale, scale_root)
            return snapped, base_deg
        else:
            # Implicit without root=: default to scale root
            return scale_root, 0
    
    def _on_pattern_created(self, chain):
        pass  # No auto-start; user calls .trigger()
```

## API Comparison

| Aspect | `ts.MIDI(v)` | `ts.comp()` |
|--------|-------------|-------------|
| Root source | `v.note` (or scale root if explicit) | Scale root (or `root=` if implicit) |
| Lifecycle | Auto (bound to `v`) | Manual (`.trigger()` / `.release()`) |
| Context | `onTriggerVoice` | `onTick` / anywhere |
| Parent binding | Required (`v`) | Optional (`parent=`) |

## Usage

```python
# Voice-reactive (implicit scale, root from incoming voice)
def onTriggerVoice(v):
    midi = ts.MIDI(v, scale="c:major")
    midi.n("0 2 4")  # degree 0 = incoming voice's position

# Voice-reactive (explicit scale, root is C5 regardless of incoming)
def onTriggerVoice(v):
    midi = ts.MIDI(v, scale="c5:major")
    midi.n("0 2 4")  # Plays C5, E5, G5

# Compositional (explicit scale)
def onTick():
    pat = ts.comp(scale="a4:minor")
    pat.n("0 2 4").trigger()  # Plays A4, C5, E5

# Compositional (implicit scale, defaults to scale root)
def onTick():
    pat = ts.comp(scale="a:minor")
    pat.n("0 2 4").trigger()  # Plays A4, C5, E5 (same result)

# Compositional (implicit scale with root override)
def onTick():
    pat = ts.comp(scale="a:minor", root="c4")
    pat.n("0 2 4").trigger()  # degree 0 = C4's position in A minor

# Compositional with optional voice binding
def onTriggerVoice(v):
    pat = ts.comp(scale="c5:major", parent=v)
    pat.n("0 2 4").trigger()  # Manual trigger, auto-release with v
```

## Deprecation

`ts.n()` is deprecated in favor of `ts.comp().n()`.
