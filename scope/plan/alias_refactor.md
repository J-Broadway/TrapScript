# Alias Refactoring Plan

Standardize parameter naming: full descriptive name is canonical, shorter forms are aliases.

---

## Naming Convention (PEP 8 + TrapScript)

### Standard Rule

| Type | Convention | Example |
|------|------------|---------|
| **Class** (instantiated by user) | PascalCase | `MIDI`, `Single`, `Comp`, `PatternChain` |
| **Function** | snake_case / lowercase | `note()`, `bus()`, `debug()`, `update()` |
| **Singleton instance** | lowercase | `par`, `output`, `scales`, `notes`, `chords` |
| **Internal/private** | Leading underscore | `_Registry`, `_fire_note()`, `_buses` |
| **Constant** | UPPER_SNAKE | `MAX_VELOCITY`, `DEFAULT_PPQ` |

### TrapScript-Specific Clarification

- **Classes** = things you `new` up and hold a reference to
  - `midi = ts.MIDI(v)` — you keep `midi` and call methods on it
  - `note = ts.Single(midi=60)` — you keep `note` and call `.trigger()`
  - `comp = ts.Comp(scale="c:major")` — you keep `comp` and call `.note()`

- **Functions** = actions that may return something, but focus is on the action
  - `tc.note("0 1 2")` — creates and auto-starts a pattern
  - `ts.bus("melody")` — gets/creates a bus
  - `ts.update()` — processes tick

### Edge Cases

| Name | Type | Reasoning |
|------|------|-----------|
| `ts.s()` | Alias for `Single` | Lowercase because it's a shorthand callable, but `s = Single` makes it a class reference |
| `midi.n()` | Method | Methods are lowercase per PEP 8 |
| `midi.note()` | Method | Canonical method name (lowercase) |

### Summary

> **PascalCase = Class you instantiate**  
> **lowercase = Function, method, or singleton instance**

---

## Part 1: Note Parameter Aliases

Refactor `Note` class kwargs and properties to use canonical (long) → alias (short) pattern.

### Current State (trapscript.py lines 757-880)
- **Canonical names are short**: `m`, `v`, `l`, `pan`, `output`, `fcut`, `fres`, `finePitch`
- **Long names are property aliases**: `midi`, `velocity`, `length` delegate to short names
- **Internal storage uses short names**: `self.m`, `self.v`, `self.l`, etc.

### Proposed Schema

```python
# Canonical name → list of aliases
_NOTE_PARAM_SCHEMA = {
    'midi':           {'aliases': ['m'], 'default': 60, 'clamp': (0, 127)},
    'velocity':       {'aliases': ['v'], 'default': 100, 'clamp': (0, 127)},
    'length':         {'aliases': ['l'], 'default': 1, 'clamp': None},
    'pan':            {'aliases': ['p'], 'default': 0, 'clamp': (-1, 1)},
    'output':         {'aliases': ['o'], 'default': 0, 'clamp': None},
    'fcut':           {'aliases': ['fc', 'x'], 'default': 0, 'clamp': (-1, 1)},
    'fres':           {'aliases': ['fr', 'y'], 'default': 0, 'clamp': (-1, 1)},
    'finePitch':      {'aliases': ['fp'], 'default': 0, 'clamp': None},
    'color':          {'aliases': [], 'default': 0, 'clamp': (0, 15)},  # No 'c' alias (conflicts with cycle)
    'releaseVelocity':{'aliases': ['rv'], 'default': 0, 'clamp': (0, 127)},
}

# Build reverse lookup (alias → canonical)
_NOTE_ALIASES = {}
for canonical, info in _NOTE_PARAM_SCHEMA.items():
    _NOTE_ALIASES[canonical] = canonical  # canonical maps to itself
    for alias in info['aliases']:
        _NOTE_ALIASES[alias] = canonical
```

### Changes Required
1. Flip `_NOTE_ALIASES` mapping
2. Change internal storage: `self.m` → `self.midi`, etc.
3. Invert property decorators (short aliases delegate to long canonical)
4. Update all internal usages (`Note(m=60)` → `Note(midi=60)`)

---

## Part 2: Function Aliases (tc.n / tc.note, MIDI.n)

### Current State

| Canonical | Alias | Location |
|-----------|-------|----------|
| `note()` | `n()` | Module-level (lines 2551, 2614) |
| `_midi_n()` | `MIDI.n` | Method attached to MIDI class (line 2726) |

**Implementation:**
- `note()` is the full function (lines 2551-2611)
- `n()` is a thin wrapper calling `note()` with `bus_name=bus` (lines 2614-2621)
- `MIDI.n` is attached via `MIDI.n = _midi_n_wrapper` (line 2726)

### Proposed: Centralized Function Alias Registry

```python
# Function alias registry
_FUNCTION_ALIASES = {
    # Module-level pattern functions
    'note': {'aliases': ['n'], 'type': 'function'},
    # MIDI method pattern (canonical is 'note', but 'n' is common usage)
    # Decide: should MIDI have .note() as canonical with .n() alias?
}
```

### Decision Points

1. **Should `MIDI.note()` exist?**
   - Currently only `MIDI.n()` exists
   - For consistency, could add `MIDI.note()` as canonical with `MIDI.n` as alias

2. **Naming symmetry:**
   - Module: `tc.note()` (canonical) / `tc.n()` (alias)
   - Class: `midi.note()` (canonical) / `midi.n()` (alias)

### Changes Required (if adding MIDI.note)
1. Rename `_midi_n` → `_midi_note`
2. Create alias: `MIDI.n = MIDI.note`
3. Update docstrings to reflect canonical/alias relationship

---

## Part 3: Cross-Class Schema Access

For classes like `Voicing`, `PatternChain` that may need to reference note parameters:

```python
def get_note_param_info(name):
    """Get param info by canonical name or alias."""
    canonical = _NOTE_ALIASES.get(name)
    if canonical:
        return canonical, _NOTE_PARAM_SCHEMA[canonical]
    return None, None

# Usage in Voicing class:
def _validate_param(self, name):
    canonical, info = get_note_param_info(name)
    if info and info['clamp']:
        return _clamp(value, *info['clamp'])
    return value
```

---

## Part 4: Class Rename - `ts.Note` → `ts.Single`

### Background

There's a naming collision/confusion:
- `ts.Note` (class) — one-shot programmatic note
- `tc.note()` (function) — pattern from mini-notation

This was identified in `strudel_mini_notation.md` with a decision to rename, but not yet implemented.

### Proposed Naming

| Canonical | Alias | Type | Purpose |
|-----------|-------|------|---------|
| `ts.Single(midi=60)` | `ts.s(midi=60)` | Class | One-shot programmatic note |
| `tc.note("0 1 2")` | `tc.n("0 1 2")` | Function | Pattern from mini-notation |
| `midi.note("0 1 2")` | `midi.n("0 1 2")` | Method | Pattern bound to incoming MIDI |

### Changes Required

1. Rename `class Note` → `class Single`
2. Create alias: `Note = Single` (for backwards compat, may deprecate later)
3. Add function alias: `s = Single` (for shorthand `ts.s(midi=60)`)
4. Update all internal usages of `Note(...)` → `Single(...)`
5. Update README documentation

### Benefits

- Clear distinction: `Single` = one note, `note()` = pattern of notes
- Aligns with Strudel convention where `note()` is pattern-based
- Reduces user confusion between class and function

---

## Summary

| Category | Canonical → Alias |
|----------|-------------------|
| **Note params** | `midi` → `m`, `velocity` → `v`, `length` → `l`, etc. |
| **One-shot class** | `ts.Single()` → `ts.s()` (renamed from `ts.Note`) |
| **Pattern functions** | `tc.note()` → `tc.n()` |
| **MIDI methods** | `midi.note()` → `midi.n()` |

---

## Relationship to phase1.3.3 (ts.comp / _PatternContext)

Phase 1.3.3 introduces `_PatternContext` as an abstract base class that both `MIDI` and `Comp` inherit from. This affects the alias refactor:

### What Changes

- `.n()` / `.note()` methods move from `MIDI`-specific into shared `_PatternContext`
- `tc.note()` / `tc.n()` deprecated in favor of `ts.comp().n()`
- New class hierarchy: `_PatternContext` → `MIDI`, `Comp`

### Dependency Order

```
Alias Refactor (this plan)
├── Part 1: _NOTE_PARAM_SCHEMA (foundation) ✓ Do now
├── Part 4: Note → Single rename ✓ Do now
├── Part 2: MIDI.note() ⏸ Defer to _PatternContext
└── Part 3: Cross-class access ✓ Do now (needed by _PatternContext)

Phase 1.3.3 (_PatternContext)
├── _PatternContext base class (inherits schema from Part 1)
├── .note() / .n() in base class (Part 2 happens here)
├── Comp class
└── Deprecate tc.note() / tc.n()
```

### Recommendation

1. **Do now (Alias Refactor):**
   - Part 1: `_NOTE_PARAM_SCHEMA` — foundational
   - Part 4: `Note` → `Single` — independent, clears naming confusion
   - Part 3: `get_note_param_info()` — needed by `_PatternContext`

2. **Defer to Phase 1.3.3:**
   - Part 2: `MIDI.note()` as canonical — will be implemented in `_PatternContext.note()`
   - `Comp` class — belongs in phase1.3.3

---

## Implementation Order (Revised)

### Alias Refactor (Do Now)
1. **Part 1: Note Parameter Schema** — Foundation for aliasing
2. **Part 4: Class Rename** — `Note` → `Single` (uses new param schema)
3. **Part 3: Cross-Class Access** — `get_note_param_info()` helper

### Defer to Phase 1.3.3 (_PatternContext)
4. **Part 2: MIDI.note()** — Implemented in `_PatternContext.note()` base method
5. **Comp class** — New class inheriting from `_PatternContext`
6. **tc.note() deprecation** — Replaced by `ts.comp().n()`

### Documentation
7. **Update README** — After alias refactor, before phase 1.3.3

---

## Critical Review: Items to Address

### Resolved Decisions

1. **`color` vs `c` conflict**: ✅ Resolved — Remove `c` as alias for `color`. Use only `color` (no short alias). This avoids collision with `c` = cycle beats in pattern functions.

2. **`output` clamping**: Leave as `clamp: None` (unclamped). Patcher output count varies by setup.

3. **`ts.Single` naming**: ✅ Confirmed — Use `ts.Single` as canonical name. Note: Will eventually become part of `ts.comp` in phase 1.3.3.

### Internal Code Updates Required

These files/locations use short param names and will need updating:

**trapscript.py:**
- `_fire_note()` (line ~915): `voice.note = src.m`
- `PatternChain` (line ~1645-1650): `Note(m=int(midi_note), l=duration_beats, v=...)`
- `_midi_n()` (line ~2685-2692): References to `self.note`
- All `Note(m=..., v=..., l=...)` constructor calls

**README.md sections to update:**
- Section 12: "Voice Triggering (Note API)" — lines 543-645
  - All `ts.Note(m=..., v=..., l=...)` examples
  - Parameter documentation table (lines 554-562)
  - Property access examples

### Backwards Compatibility

1. **`ts.Note` alias**: Keep `Note = Single` for backwards compat
2. **Short param names**: Both `midi=60` and `m=60` should work (aliases resolve either way)
3. **Property access**: Both `note.midi` and `note.m` should work

### Testing Considerations

After refactor, verify:
- `ts.Single(midi=60)` works
- `ts.Single(m=60)` works (alias)
- `ts.Note(midi=60)` works (backwards compat alias)
- `note.midi`, `note.m` both work (property access)
- `note.midi = 72` and `note.m = 72` both work (setter)
- Internal `_fire_note()` still works
- Pattern triggering still works

---

## Files to Modify

### trapscript.py
1. Replace `_NOTE_ALIASES` dict (lines ~757-775) with `_NOTE_PARAM_SCHEMA`
2. Add `_NOTE_ALIASES` auto-generated from schema
3. Add `_NOTE_DEFAULTS` auto-generated from schema
4. Update `_resolve_note_kwargs()` to use new schema
5. Rename `class Note` → `class Single`
6. Add `Note = Single` alias
7. Add `s = Single` alias
8. Update `Single.__init__` to use canonical names internally
9. Flip property decorators (short → long becomes long ← short)
10. Update all internal `Note(m=..., v=..., l=...)` calls
11. Add `get_note_param_info()` helper function

### README.md
1. Update Section 12 header: "Voice Triggering (Single API)" or keep "Note API" with explanation
2. Update parameter table to show canonical → alias pattern
3. Update all code examples to use `ts.Single()` (canonical) with note that `ts.Note()` still works
4. Update property access examples

---

## Resolved Questions

1. **Naming**: ✅ `ts.Single` confirmed
2. **`color` / `c` collision**: ✅ Remove `c` alias for `color`
3. **README update timing**: Update now with `ts.Single`, note that `ts.Note` still works for backwards compat