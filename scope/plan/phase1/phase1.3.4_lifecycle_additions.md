# Phase 1.3.4: Lifecycle Additions (`pause` / `play` / `restart` + trigger modes)

## Purpose

Extend post-`1.3.3` lifecycle ergonomics for `PatternChain` and `ts.comp()` while keeping behavior deterministic and explicit.

This phase assumes:

- `1.3.2.2` unified construction is complete + legacy systems removed
- `1.3.2.3` lifecycle ownership is in `PatternChain` + `_CompContextMixin` introduced
- `1.3.3` `Comp` class is implemented (`MIDI` auto, `Comp` manual)

## Target API

```python
.pause()                     # Pause pattern, keep current phase position
.play()                      # Resume from paused position (not equivalent to trigger)
.stop()                      # Stop and reset to cycle start (phase = 0)
.restart()                   # Reset to start, then play immediately
.trigger(mode='cut')         # trigger mode: cut | overlap | oneshot
```

## Semantics (explicit contract)

### `.pause()`

- Halts ticking/output generation
- Preserves phase position and step context
- Keeps chain identity/state available for inspection and resume
- Safe/idempotent if already paused

### `.play()`

- Resumes a paused chain from preserved phase
- No phase reset
- If already running, no-op
- If stopped (reset state), call `trigger(mode='cut')`

### `.stop()`

- Stops playback and resets to beginning (`phase=0`)
- Clears "currently running" runtime state
- Should not duplicate cleanup side effects on repeated calls
- If bus/history behavior differs from pause, document clearly

### `.restart()`

- Equivalent to `stop()` then immediate play from start
- Guaranteed deterministic restart point

### `.trigger(mode='cut')`

- `cut` (default): cuts self (if playing) then resets to start to run immediately
- `overlap`: allow simultaneous playback layers
- `oneshot`: play one full pattern cycle then stop

## Trigger Mode Notes

### `cut` (default)

- Best deterministic default for live coding and repeated retriggers
- Prevents accidental duplicate registrations for same chain

### `overlap`

- Enables stacked texture from repeated trigger calls
- Requires instance policy decision:
  - spawn child/clone runner, or
  - maintain internal active runner list
- Must define cleanup behavior for overlapped runners on `stop()`
- Explicit note: registry invariants from `1.3.2.3` still apply. Overlap must be implemented intentionally and must not rely on accidental duplicate registrations.

### `oneshot`

- Plays exactly one cycle (respecting current cycle length at start)
- Auto-stops at cycle boundary
- Completion rule: when phase delta since trigger reaches 1.0 (100% of one cycle)
- Use cycle length latched at trigger time for termination boundary

## Suggested Internal State Model

- `created`
- `running`
- `paused`
- `stopped`
- optional `disposed` (if terminal cleanup is retained separately)

Allowed transitions:

- `created -> running` via `trigger()` / `play()` (if chosen)
- `running -> paused` via `pause()`
- `paused -> running` via `play()`
- `running|paused -> stopped` via `stop()`
- `stopped -> running` via `restart()` or `trigger(mode='cut')`

## What was missing (now captured)

1. Clear difference between `play()` and `trigger()`
2. Behavior of `play()` when called from `stopped`
3. Overlap implementation ownership and cleanup rules
4. Oneshot completion boundary definition
5. Idempotency requirements across all lifecycle methods
6. Explicit state transitions for testing and debugging

## Compatibility Notes

- `MIDI` context auto policy is `trigger(mode='cut')` on creation, then `stop()` on parent release.
- `MIDI` chains still expose and respect full `PatternChain` lifecycle methods (`pause()`, `play()`, `restart()`, `stop()`) just like `Comp`.
- `Comp` context remains manual and can use all trigger modes directly.

## Pre-implementation decision gate

Before implementing `trigger(mode='overlap')`, choose and document ownership model:

- clone/child runner per overlap trigger, or
- multi-runner list owned by a single chain

Implementation should not begin until one model is selected.

## Verification Checklist

- `pause()` preserves phase and `play()` resumes from same phase
- `stop()` resets phase to 0 and halts output
- `restart()` always starts at beginning and outputs immediately
- `trigger(mode='cut')` replays deterministically
- `trigger(mode='overlap')` creates audible/state overlap without registry corruption
- `trigger(mode='oneshot')` stops at exactly one cycle boundary
- repeated lifecycle calls are safe (idempotent where expected)

## Nice-to-have follow-ups

- `status()` helper (`running/paused/stopped`)
- optional `playhead()` helper (phase, cycle, step snapshot)
- debug tracing for mode transitions
