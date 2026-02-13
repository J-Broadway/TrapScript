# Alias Refactor 1.3 — Decorator Pattern
Status: MAYBE FUTURE IMPLEMENTAITON

Consolidate the three different alias resolution patterns into a single `@aliases` decorator for clean, scalable code.

---

## Problem: Three Alias Patterns

After alias_refactor1.2, TrapScript has three different ways to handle parameter aliases:

### Pattern 1: Schema-based (Single class)
```python
# Single.__init__ — all params through **kwargs, resolved via schema
def __init__(self, **kwargs):
    params = _resolve_note_kwargs(kwargs)  # Uses _NOTE_PARAM_SCHEMA
    ...
```
**Pros:** Single source of truth, no per-site boilerplate.
**Cons:** All params must be kwargs (no positional), signature doesn't show defaults in IDE.

### Pattern 2: Manual resolution helper (pattern functions)
```python
def note(pattern_str: str, cycle=4, root=60, parent=None, mute=False, bus=None, **kwargs):
    aliases = _resolve_pattern_kwargs('note', kwargs)
    cycle = aliases.get('cycle', cycle)
    root = aliases.get('root', root)
    ...
```
**Pros:** Canonical params visible in signature, IDE autocomplete works.
**Cons:** 3-line boilerplate copy-pasted in every function. Easy to forget or mess up.

### Pattern 3: Inline pop (MIDI.__init__, Single.trigger)
```python
def __init__(self, incomingVoice, cycle=4, scale=None, **kwargs):
    cycle = kwargs.pop('c', cycle)
    if kwargs:
        raise TypeError(f"MIDI() got unexpected keyword arguments: {list(kwargs.keys())}")
    ...
```
**Pros:** Simple, no helper needed.
**Cons:** Ad-hoc, no schema, doesn't scale.

---

## Solution: `@aliases` Decorator

A decorator that transparently resolves aliases before the function executes. The function signature stays clean (no `**kwargs` needed), and adding an alias is a one-line change.

### Decorator Implementation

```python
import functools

def aliases(**alias_map):
    """
    Decorator that resolves kwarg aliases before calling the function.
    
    Usage:
        @aliases(cycle=['c'], root=['r'])
        def note(pattern_str, cycle=4, root=60, ...):
            ...
    
    When called as `note("0 1 2", c=8)`, the decorator converts `c=8` to `cycle=8`
    before the function sees it.
    
    Raises TypeError if:
        - Both canonical and alias are provided (e.g., cycle=4, c=8)
        - Unknown kwargs are passed (preserved from original behavior)
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for canonical, alias_list in alias_map.items():
                for alias in alias_list:
                    if alias in kwargs:
                        if canonical in kwargs:
                            raise TypeError(
                                f"{func.__name__}() got multiple values for '{canonical}'")
                        kwargs[canonical] = kwargs.pop(alias)
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

### Before/After Comparison

**Before (current):**
```python
def note(pattern_str: str, cycle=4, root=60, parent=None, mute=False, bus=None, **kwargs) -> 'PatternChain':
    # Resolve aliases: c -> cycle, r -> root
    aliases = _resolve_pattern_kwargs('note', kwargs)
    cycle = aliases.get('cycle', cycle)
    root = aliases.get('root', root)
    # ... rest of function
```

**After (with decorator):**
```python
@aliases(cycle=['c'], root=['r'])
def note(pattern_str: str, cycle=4, root=60, parent=None, mute=False, bus=None) -> 'PatternChain':
    # ... rest of function (no alias boilerplate)
```

---

## Functions to Update

| Function | Current Pattern | Aliases Needed |
|----------|-----------------|----------------|
| `MIDI.__init__()` | Inline pop | `cycle=['c']` |
| `Single.trigger()` | Inline pop | `length=['l']` |
| `note()` | Helper + manual | `cycle=['c'], root=['r']` |
| `n()` | Helper + manual | `cycle=['c'], root=['r']` |
| `_midi_n()` | Helper + manual | `cycle=['c']` |
| `_midi_note_wrapper()` | Passthrough | `cycle=['c']` |

### Special Cases

**`Single.__init__`**: Currently uses `**kwargs` with schema-based resolution (`_resolve_note_kwargs`). This is intentional — `Single` has 10 parameters, and we want full schema control (defaults, clamping). **Leave as-is.** The decorator is for functions with explicit signature params.

**`_midi_note_wrapper`**: Just a passthrough to `_midi_n`. After applying decorator to `_midi_n`, the wrapper can be simplified or removed.

---

## Implementation Plan

### Part 1: Add the Decorator

Add `@aliases` decorator near other alias infrastructure (~line 780 in trapscript.py):

```python
import functools

def aliases(**alias_map):
    """Decorator that resolves kwarg aliases before calling the function."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for canonical, alias_list in alias_map.items():
                for alias in alias_list:
                    if alias in kwargs:
                        if canonical in kwargs:
                            raise TypeError(
                                f"{func.__name__}() got multiple values for '{canonical}'")
                        kwargs[canonical] = kwargs.pop(alias)
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

### Part 2: Update MIDI.__init__()

```python
# Before
def __init__(self, incomingVoice, cycle=4, scale=None, **kwargs):
    cycle = kwargs.pop('c', cycle)
    if kwargs:
        raise TypeError(f"MIDI() got unexpected keyword arguments: {list(kwargs.keys())}")
    ...

# After
@aliases(cycle=['c'])
def __init__(self, incomingVoice, cycle=4, scale=None):
    ...
```

### Part 3: Update Single.trigger()

```python
# Before
def trigger(self, length=None, cut=True, parent=None, **kwargs):
    length = kwargs.pop('l', length)
    if kwargs:
        raise TypeError(f"trigger() got unexpected keyword arguments: {list(kwargs.keys())}")
    ...

# After
@aliases(length=['l'])
def trigger(self, length=None, cut=True, parent=None):
    ...
```

### Part 4: Update note()

```python
# Before
def note(pattern_str: str, cycle=4, root=60, parent=None, mute=False, bus=None, **kwargs) -> 'PatternChain':
    aliases = _resolve_pattern_kwargs('note', kwargs)
    cycle = aliases.get('cycle', cycle)
    root = aliases.get('root', root)
    ...

# After
@aliases(cycle=['c'], root=['r'])
def note(pattern_str: str, cycle=4, root=60, parent=None, mute=False, bus=None) -> 'PatternChain':
    ...
```

### Part 5: Update n()

```python
# Before
def n(pattern_str: str, cycle=4, root=60, parent=None, mute=False, bus=None, **kwargs) -> 'PatternChain':
    aliases = _resolve_pattern_kwargs('n', kwargs)
    cycle = aliases.get('cycle', cycle)
    root = aliases.get('root', root)
    return note(...)

# After
@aliases(cycle=['c'], root=['r'])
def n(pattern_str: str, cycle=4, root=60, parent=None, mute=False, bus=None) -> 'PatternChain':
    return note(...)
```

### Part 6: Update _midi_n() and wrapper

```python
# _midi_n — apply decorator
@aliases(cycle=['c'])
def _midi_n(self, pattern_str: str, cycle=None, scale=None, mute=False, bus=None) -> 'PatternChain':
    ...

# _midi_note_wrapper — simplify (just passes through, decorator on _midi_n handles aliases)
def _midi_note_wrapper(self, pattern_str: str, cycle=None, scale=None, mute=False, bus=None, **kwargs) -> 'PatternChain':
    return _midi_n(self, pattern_str, cycle=cycle, scale=scale, mute=mute, bus=bus, **kwargs)
```

Actually, since `_midi_n` has the decorator, `_midi_note_wrapper` can also be decorated and simplified:

```python
@aliases(cycle=['c'])
def _midi_note_wrapper(self, pattern_str: str, cycle=None, scale=None, mute=False, bus=None) -> 'PatternChain':
    return _midi_n(self, pattern_str, cycle=cycle, scale=scale, mute=mute, bus=bus)
```

Or remove the wrapper entirely and assign `_midi_n` directly (if the only reason for the wrapper was alias handling).

### Part 7: Cleanup

After applying decorators:

1. **Remove `_resolve_pattern_kwargs()`** — no longer needed
2. **Keep `_PATTERN_PARAM_SCHEMA`** — still useful for documentation, default values, potential future clamping
3. **Keep `_resolve_note_kwargs()`** — still used by `Single.__init__`

---

## Benefits

1. **Single pattern** — all alias-enabled functions use the same decorator
2. **Clean signatures** — no `**kwargs` pollution, IDE autocomplete works
3. **One-line changes** — adding a new alias = adding to decorator args
4. **Scalable** — Phase 1.3.3's `Comp.n()` just needs `@aliases(cycle=['c'], root=['r'])`
5. **Self-documenting** — decorator clearly shows which aliases exist

---

## Testing Checklist

After implementation, verify all these still work:

- [ ] `ts.MIDI(v, cycle=4)` — canonical
- [ ] `ts.MIDI(v, c=4)` — alias
- [ ] `midi.n("0 1 2", cycle=8)` — canonical
- [ ] `midi.n("0 1 2", c=8)` — alias
- [ ] `ts.note("0 1 2", root=72)` — canonical
- [ ] `ts.note("0 1 2", r=72)` — alias
- [ ] `ts.n("0 1 2", c=4, r=60)` — both aliases
- [ ] `note.trigger(length=2)` — canonical
- [ ] `note.trigger(l=2)` — alias
- [ ] `ts.Single(midi=60)` — canonical (unchanged)
- [ ] `ts.Single(m=60)` — alias (unchanged)
- [ ] Error: `ts.n("0 1 2", cycle=4, c=8)` — should raise TypeError

---

## Files to Modify

### trapscript.py

1. Add `aliases()` decorator function (near line 780)
2. Apply `@aliases(cycle=['c'])` to `MIDI.__init__()`
3. Apply `@aliases(length=['l'])` to `Single.trigger()`
4. Apply `@aliases(cycle=['c'], root=['r'])` to `note()`
5. Apply `@aliases(cycle=['c'], root=['r'])` to `n()`
6. Apply `@aliases(cycle=['c'])` to `_midi_n()` and `_midi_note_wrapper()`
7. Remove `**kwargs` from all updated function signatures
8. Remove alias resolution boilerplate from function bodies
9. Remove `_resolve_pattern_kwargs()` (no longer needed)
10. Remove `_get_bus` workaround (no longer needed — `bus` param doesn't require `**kwargs`)

Wait — actually `_get_bus` is still needed. The issue is that `bus` as a parameter name shadows the global `bus()` function. This is independent of the `**kwargs` pattern. **Keep `_get_bus`.**

