# Voice Triggering — Open Questions

Active questions for the voice triggering API design. Move to `voice_triggering.md` once resolved.

---

## Q1: API Style — Factory vs Chaining vs Context

**Option A: Simple Factory (current proposal)**
```python
note = ts.Note(72, v=100).trigger()
note.release()
```

**Option B: Context-Aware Factory**
```python
with ts.voices() as v:
    v.note(72).trigger()
    v.note(76).trigger()
# Auto-release all on exit
```

**Option C: Direct Functions**
```python
handle = ts.trigger(72, v=100)
ts.release(handle)
```

**Initial leaning**: Option A with Option B available for complex patterns.

**Status**: Open

---

## Q2: Timing — How to Express Duration

VFX Script provides:
- `vfx.context.PPQ` — pulses per quarter note
- `vfx.context.ticks` — current tick position

**Option A: Raw ticks**
```python
ts.Note(72).duration(480).trigger()  # 480 ticks
```

**Option B: Beat fractions**
```python
ts.Note(72).duration(1/4).trigger()  # Quarter note
ts.Note(72).duration(1/8).trigger()  # Eighth note
```

**Option C: Named durations**
```python
ts.Note(72).quarter().trigger()
ts.Note(72).eighth().trigger()
```

**Option D: PPQ-relative constants**
```python
ts.Note(72).duration(ts.Q).trigger()      # Quarter
ts.Note(72).duration(ts.Q * 1.5).trigger() # Dotted quarter
ts.Note(72).duration(ts.Q / 3).trigger()   # Triplet eighth
# Where ts.Q reads PPQ at runtime
```

**Sub-questions:**
- How do we handle dotted notes (1.5x duration)?
- How do we handle triplets (2/3x duration)?
- How do we handle ties across bars?
- How do we handle tempo changes mid-song?

**Status**: Open

---

## Q3: Timing — How to Express Offsets/Scheduling

Sometimes you want to trigger a note in the future, not immediately.

**Option A: Delay parameter**
```python
ts.Note(72).delay(ts.Q).trigger()  # Trigger 1 beat from now
```

**Option B: Schedule at absolute tick**
```python
ts.Note(72).at(1920).trigger()  # Trigger at tick 1920
```

**Option C: Quantized triggering**
```python
ts.Note(72).quantize(ts.bar).trigger()  # Trigger at next bar
```

**Sub-question**: Do we need a central scheduler/queue that processes pending events in `onTick()`?

**Status**: Open

---

## Q4: Rests and Silence

How to express "do nothing for X duration"?

**Option A: Explicit rest function**
```python
ts.rest(ts.Q)  # Wait a quarter note before next event
```

**Option B: Pattern-based (Strudel-inspired)**
```python
ts.pattern("C4 ~ E4 ~")  # ~ is rest
```

**Option C: Just use delays**
```python
# No explicit rest — just schedule notes with appropriate offsets
```

**Status**: Open

---

## Q5: Polyphony Management

**Option A: Unlimited (current)**
```python
# Every trigger creates a new voice, no limits
```

**Option B: Voice pool with stealing**
```python
pool = ts.VoicePool(max=8, steal='oldest')
note = pool.note(72).trigger()
```

**Option C: Automatic tracking by note number**
```python
# ts.Note(72) always refers to "the C5 voice"
# Re-triggering same note retriggers the existing voice
ts.Note(72).trigger()  # C5 on
ts.Note(72).release()  # C5 off
ts.Note(72).trigger()  # C5 on again (same voice reused)
```

**Status**: Open

---

## Q6: Separation of Concerns

**Current thinking:**
- `ts.MIDI(incomingVoice)` — for passthrough/modification of incoming notes
- `ts.Note(...)` — for programmatic note creation

Should these share any base class or API? Or stay completely separate?

**Status**: Open

---

## Q7: Duration Location — Builder vs Trigger

Should duration be set on the builder or passed to trigger?

**Option A: Builder method**
```python
ts.Note(72).duration(ts.Q).trigger()
```

**Option B: Trigger parameter**
```python
ts.Note(72).trigger(duration=ts.Q)
```

**Option C: Both (builder sets default, trigger can override)**
```python
note_template = ts.Note(72).duration(ts.Q)
note_template.trigger()  # Uses Q
note_template.trigger(duration=ts.E)  # Overrides to eighth
```

**Status**: Open

---
