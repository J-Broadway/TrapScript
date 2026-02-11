# TrapScript Phase 1.3 Scale Tests
import flvfx as vfx
import trapscript as ts

ts.debug(True, level=1)

def createDialog():
    ui = ts.UI()
    ui.Knob(name='Cycle', d=2, min=0.5, max=4, export='bind')
    return ui.form

def onTriggerVoice(incomingVoice):
    # === SLOWCAT REPLICATION BUG FIX TEST ===
    # Test: <0!2 3 5 7> should play: 0, 0, 3, 5, 7 (5 cycles, then loop)
    # Strudel reference: note("<0!2 3 5 7>").scale("c:major") → C3, C3, F3, A3, C4
    midi = ts.MIDI(incomingVoice, scale="c5:major")
    midi.n("<0!2 3 5 7>", c=2)  # Should play: C5, C5, F5, A5, C6 over 5 cycles
    
    # === SCALE SYSTEM TESTS ===
    # Uncomment one test at a time
    
    # --- Test 1: Chromatic mode (no scale) - existing behavior ---
    # Numbers are semitone offsets from incoming voice note
    # midi = ts.MIDI(incomingVoice)
    # midi.n("0 3 5 7", c=2)  # Minor triad arp from incoming note
    
    # --- Test 2: Scale mode - major triad (degrees 0, 2, 4) ---
    # Numbers are scale degree indices (0=root, 2=3rd, 4=5th)
    # midi = ts.MIDI(incomingVoice, scale="c5:major")
    # midi.n("0 2 4", c=2)  # C5, E5, G5 (C major triad)
    
    # --- Test 3: Scale mode - minor 7th chord ---
    # midi = ts.MIDI(incomingVoice, scale="a4:minor")
    # midi.n("[0,2,4,6]", c=4)  # A4, C5, E5, G5 (Am7 chord)
    
    # --- Test 4: Scale mode - pentatonic sequence ---
    # midi = ts.MIDI(incomingVoice, scale="c4:pentatonic")
    # midi.n("0 1 2 3 4 5 6", c=4)  # C D E G A C' D' (wraps octave)
    
    # --- Test 5: Inheritance test - c from MIDI ---
    # midi = ts.MIDI(incomingVoice, c=1, scale="c5:major")
    # midi.n("0 2 4")  # Inherits c=1, plays C5 E5 G5 fast
    
    # --- Test 6: Override at .n() level ---
    # midi = ts.MIDI(incomingVoice, c=4, scale="c5:major")
    # midi.n("0 2 4", scale="a4:minor")  # Overrides to A minor: A4 C5 E5
    
    # --- Test 7: Negative degrees (below root) ---
    # midi = ts.MIDI(incomingVoice, scale="c5:major")
    # midi.n("-1 0 1 2", c=2)  # B4, C5, D5, E5
    
    # --- Test 8: Note names with scale (quantization) ---
    # midi = ts.MIDI(incomingVoice, scale="c5:minor")
    # midi.n("c4 e4 g4", c=2)  # e4 quantizes to eb4 in C minor
    
    # --- Test 9: Custom scale ---
    # ts.scales.add('bebop', [0, 2, 4, 5, 7, 9, 10, 11])
    # midi = ts.MIDI(incomingVoice, scale="c4:bebop")
    # midi.n("0 1 2 3 4 5 6 7", c=4)  # C D E F G A Bb B
    
    # --- Test 10: Registry inspection ---
    # print(ts.scales)        # <scales: major, minor, dorian, ...>
    # print(ts.scales.list()) # ['major', 'minor', ...]
    # print(ts.notes['c#'])   # 1
    # print('dorian' in ts.scales)  # True

def onReleaseVoice(incomingVoice):
    ts.stop_patterns_for_voice(incomingVoice)
    
    for v in vfx.context.voices:
        if ts.get_parent(v) == incomingVoice:
            v.release()

def onTick():
    ts.update()
