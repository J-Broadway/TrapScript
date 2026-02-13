# Phase 1.3.3: ts.comp() — Standalone Pattern Context

## Problem

`ts.MIDI` provides OOP defaults (scale, c) that `.n()` inherits. `ts.n()` has no equivalent — it's stateless and doesn't support scales. This creates an architectural gap.

## Solution

Introduce `ts.comp()` — a standalone pattern context with the same OOP structure as `ts.MIDI`, minus voice binding.

## Design: Abstract Base Class + Template Method

```python
class _CompContext:
    """Base: shared defaults, scale handling, pattern creation."""
    
    def __init__(self, c=4, scale=None, root=None, v=1.0, pan=0.0, parent=None):
        # Store defaults, parse scale
    
    def note(self, pattern_str, c=None, scale=None, ...) -> PatternChain:
        """Canonical method for pattern creation."""
        chain._root = self._resolve_root(scale, scale_root)  # Template method
        self._on_pattern_created(chain)  # Template method
    
    n = note  # Alias (per alias_refactor.md)
    
    def _resolve_root(self, scale, scale_root):
        raise NotImplementedError
    
    def _on_pattern_created(self, chain):
        pass  # Override for lifecycle behavior


class MIDI(vfx.Voice, _CompContext):
    """Voice-bound context. Auto-triggers, auto-releases."""
    
    def _resolve_root(self, scale, scale_root):
        # Root = incoming voice note (snapped to scale if active)
    
    def _on_pattern_created(self, chain):
        # Auto-start, register for voice lifecycle


class Comp(_CompContext):
    """Standalone context. Manual trigger/release."""
    
    def __init__(self, c=4, scale=None, root=60, v=1.0, pan=0.0, parent=None):
        # root is required (no incoming voice)
    
    def _resolve_root(self, scale, scale_root):
        # Root = explicit root param (snapped to scale if active)
    
    def _on_pattern_created(self, chain):
        pass  # No auto-start; user calls .trigger()
```

## API Comparison

| Aspect | `ts.MIDI(v)` | `ts.comp()` |
|--------|-------------|-------------|
| Root source | `v.note` | Explicit `root=` |
| Lifecycle | Auto (bound to `v`) | Manual (`.trigger()` / `.release()`) |
| Context | `onTriggerVoice` | `onTick` / anywhere |
| Parent binding | Required (`v`) | Optional (`parent=`) |

## Usage

```python
# Voice-reactive
def onTriggerVoice(v):
    midi = ts.MIDI(v, scale="c:major")
    midi.n("0 2 4")  # Auto-triggered

# Compositional
def onTick():
    pat = ts.comp(scale="a:minor", root="c4")
    pat.n("0 2 4").trigger()

# Compositional with optional voice binding
def onTriggerVoice(v):
    pat = ts.comp(scale="c:major", root="e4", parent=v)
    pat.n("0 2 4").trigger()  # Manual trigger, auto-release with v
```

## Deprecation

`ts.n()` is deprecated in favor of `ts.comp().n()`.
