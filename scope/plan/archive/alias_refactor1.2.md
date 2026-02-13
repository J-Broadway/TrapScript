# Alias Refactor 1.2 — Remaining Work

This document tracks what still needs to be done from the original alias refactor plan.

**Completed in 1.0:**
- Part 1: `_NOTE_PARAM_SCHEMA` ✅
- Part 4: `get_note_param_info()` ✅
- Part 6: `Note` → `Single` rename ✅

**Remaining:**
- Part 2: Pattern params (`c` → `cycle`, `r` alias, `bus_name` → `bus`)
- Part 5: Method params (`Single.trigger(l=)` → `length=`)

---

## Part 2: Pattern Parameter Aliases (cycle, root, bus)

### Current State

| Current | Proposed Canonical | Alias | Location |
|---------|-------------------|-------|----------|
| `c` | `cycle` | `c` | `note()`, `n()`, `MIDI.__init__()`, `MIDI.n()` |
| `root` | `root` | `r` | `note()`, `n()`, `MIDI.n()` |
| `bus_name` | `bus` | — | `note()` (consolidate with `n()`) |

### Schema

```python
_PATTERN_PARAM_SCHEMA = {
    'cycle': {'aliases': ['c'], 'default': 4, 'clamp': (0.01, None)},
    'root':  {'aliases': ['r'], 'default': 60, 'clamp': (0, 127)},
}
```

### Changes Required

**trapscript.py:**

1. `MIDI.__init__()` (line ~248):
   - `c=4` → `cycle=4`
   - `self._c` → `self._cycle`
   - Add kwarg alias: accept `c` as alias for `cycle`

2. `note()` (line ~2583):
   - `c=4` → `cycle=4`
   - `bus_name=None` → `bus=None`
   - Add kwarg aliases: `c` → `cycle`, `r` → `root`
   - Line 2625: `chain._cycle_beats = c` → `= cycle`
   - Line 2632: `if bus_name:` → `if bus:`
   - Line 2634: `chain._bus_name = bus_name` → `= bus`
   - Line 2641: `_register_chain(parent, chain, c, root)` → `..., cycle, root)`

3. `n()` (line ~2646):
   - `c=4` → `cycle=4`
   - Add kwarg aliases: `c` → `cycle`, `r` → `root`
   - Line 2653: `note(..., c=c, ..., bus_name=bus)` → `cycle=cycle, ..., bus=bus`

4. `_midi_n()` (line ~2672):
   - `c=None` → `cycle=None`
   - `bus_name=None` → `bus=None`
   - Add kwarg alias: `c` → `cycle`
   - Line 2695: `cycle_beats = c if c is not None else self._c` → `cycle ... self._cycle`
   - Line 2734: `if bus_name:` → `if bus:`
   - Line 2735-2738: `bus_name` → `bus`
   - Line 2748: debug log `c={cycle_beats}` (cosmetic, can keep as-is)

5. `_midi_note_wrapper()` (line ~2754):
   - `c=None` → `cycle=None`
   - `bus=None` stays as-is
   - Line 2756: `_midi_n(..., c=c, ..., bus_name=bus)` → `cycle=cycle, ..., bus=bus`

6. Internal usages:
   - Line 251: `self._c = c` → `self._cycle = cycle`
   - (Line 2695 covered in item 4 above)

### Backwards Compatibility

Both forms work:
- `midi.n("0 1 2", cycle=8)` ✅ canonical
- `midi.n("0 1 2", c=8)` ✅ alias
- `ts.note("0 1 2", c=8, r=60)` ✅ aliases
- `ts.note("0 1 2", cycle=8, root=60)` ✅ canonical

---

## Part 5: Method Parameter Aliases

### Single.trigger()

Current (line ~908):
```python
def trigger(self, l=None, cut=True, parent=None):
```

Should be:
```python
def trigger(self, length=None, cut=True, parent=None):
```

With `l` accepted as kwarg alias.

### Changes Required

1. Rename signature param: `l=None` → `length=None`
2. Add kwarg alias resolution at start of method:
   ```python
   if 'l' in kwargs:
       length = kwargs.pop('l')
   ```
   Or use `**kwargs` pattern with resolution helper.

### Backwards Compatibility

Both work:
- `note.trigger(length=2)` ✅ canonical
- `note.trigger(l=2)` ✅ alias

---

## Part 3: MIDI.n() — No Canonical Change Needed

**Status:** ✅ Complete (no changes needed)

`MIDI.note()` cannot exist because it conflicts with `vfx.Voice.note` attribute (line 2758 comment). `MIDI.n()` is the only pattern method, not an alias.

For `_PatternContext` in Phase 1.3.3:
- Base class will have `.n()` method (not `.note()`)
- `Comp` class will also use `.n()` for consistency
- Module-level `tc.note()` / `tc.n()` remain separate (different namespace, no conflict)

---

## Testing Checklist

After implementation, verify:

- [ ] `ts.MIDI(v, cycle=4)` works
- [ ] `ts.MIDI(v, c=4)` works (alias)
- [ ] `midi.n("0 1 2", cycle=8)` works
- [ ] `midi.n("0 1 2", c=8)` works (alias)
- [ ] `ts.note("0 1 2", root=72)` works
- [ ] `ts.note("0 1 2", r=72)` works (alias)
- [ ] `ts.note("0 1 2", bus="melody")` works
- [ ] `note.trigger(length=2)` works
- [ ] `note.trigger(l=2)` works (alias)
- [ ] All existing patterns still fire correctly

---

## Files to Modify

### trapscript.py

1. Add `_PATTERN_PARAM_SCHEMA` (or inline resolution)
2. Update `MIDI.__init__()`: `c` → `cycle`, `self._c` → `self._cycle`
3. Update `note()`: `c` → `cycle`, `bus_name` → `bus`, add aliases
4. Update `n()`: `c` → `cycle`, add aliases, fix `note()` call
5. Update `_midi_n()`: `c` → `cycle`, `bus_name` → `bus`
6. Update `_midi_note_wrapper()`: `c` → `cycle`
7. Update `Single.trigger()`: `l` → `length`, add alias
8. Update all internal `self._c` → `self._cycle` references

### trapscript.py Docstrings

1. `note()` docstring (lines 2587-2617):
   - `c:` → `cycle:`
   - `bus_name:` → `bus:`
   - Examples: `c=4` → `cycle=4` (or keep as-is to show alias usage)

2. `_midi_n()` docstring (lines 2673-2693):
   - Examples show `c=4`, `c=2` — update or keep to show alias

### README.md

1. Update pattern function docs to show `cycle` as canonical
2. Update examples: `c=4` → `cycle=4` (with note that `c` still works)
