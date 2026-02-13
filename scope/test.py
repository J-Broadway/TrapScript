# Phase 1.3.2.1: Explicit/Implicit Scale Root Tests
import flvfx as vfx
import trapscript as ts

ts.debug(True, level=1)

# ============================================================
# SELECT TEST TO RUN
# ============================================================
ACTIVE_TEST = 1

def createDialog():
    ui = ts.UI()
    ui.Knob(name='Cycle', d=2, min=0.5, max=4, export='bind')
    return ui.form

def onTriggerVoice(incomingVoice):
    """
    Test the explicit vs implicit scale root behavior.
    Play different MIDI notes to see how explicit/implicit roots respond.
    
    Expected behavior:
    - Implicit root ("c:major"): degree 0 follows incoming voice's position
    - Explicit root ("c4:major"): degree 0 always plays C4 (60)
    """
    
    if ACTIVE_TEST == 1:
        # Test 1: Implicit root - degree 0 = incoming voice's scale position
        # Try: Play E4 (64), G4 (67), C4 (60), A4 (69)
        # Expected: Each plays its own snapped note at degree 0
        midi = ts.MIDI(incomingVoice, scale="c:major")
        midi.n("0", cycle=2)
        print(f"Test 1 (Implicit): incoming={incomingVoice.note}")
    
    elif ACTIVE_TEST == 2:
        # Test 2: Explicit root C4 - degree 0 = C4 (60), ignores incoming
        # Try: Play E4 (64), G4 (67), C4 (60), A4 (69)
        # Expected: All play C4 (60) at degree 0
        midi = ts.MIDI(incomingVoice, scale="c4:major")
        midi.n("0", cycle=2)
        print(f"Test 2 (Explicit C4): incoming={incomingVoice.note}, should play C4=60")
    
    elif ACTIVE_TEST == 3:
        # Test 3: Explicit root C5 - degree 0 = C5 (72)
        # Try: Play any note
        # Expected: All play C5 (72) at degree 0
        midi = ts.MIDI(incomingVoice, scale="c5:major")
        midi.n("0", cycle=2)
        print(f"Test 3 (Explicit C5): incoming={incomingVoice.note}, should play C5=72")
    
    elif ACTIVE_TEST == 4:
        # Test 4: Explicit root with triad - C5 E5 G5
        # Try: Play any note
        # Expected: All play C5 (72), E5 (76), G5 (79)
        midi = ts.MIDI(incomingVoice, scale="c5:major")
        midi.n("0 2 4", cycle=2)
        print(f"Test 4 (Explicit triad): should play C5=72, E5=76, G5=79")
    
    elif ACTIVE_TEST == 5:
        # Test 5: Implicit root with triad - follows incoming voice
        # Try: Play C4 (60), E4 (64), G4 (67)
        # C4 → C4 E4 G4, E4 → E4 G4 B4, G4 → G4 B4 D5
        midi = ts.MIDI(incomingVoice, scale="c:major")
        midi.n("0 2 4", cycle=2)
        print(f"Test 5 (Implicit triad): incoming={incomingVoice.note}, degrees relative to incoming")
    
    elif ACTIVE_TEST == 6:
        # Test 6: Negative degrees with explicit root
        # degree -1 in C4 major = B3 (59)
        midi = ts.MIDI(incomingVoice, scale="c4:major")
        midi.n("-1 0 1", cycle=2)
        print(f"Test 6 (Negative deg): should play B3=59, C4=60, D4=62")
    
    elif ACTIVE_TEST == 7:
        # Test 7: Letter names with explicit root (quantization)
        # "c4 e4 g4" in C5 major snaps to nearest scale tones
        midi = ts.MIDI(incomingVoice, scale="c5:major")
        midi.n("c4 e4 g4", cycle=2)
        print(f"Test 7 (Letter names): should snap to C4=60, E4=64, G4=67")
    
    elif ACTIVE_TEST == 8:
        # Test 8: Different scale - A4 minor explicit root
        # degree 0 = A4 (69), degree 2 = C5 (72)
        midi = ts.MIDI(incomingVoice, scale="a4:minor")
        midi.n("0 2 4", cycle=2)
        print(f"Test 8 (A4 minor): should play A4=69, C5=72, E5=76")
    
    elif ACTIVE_TEST == 9:
        # Test 9: Override at .n() level - explicit over implicit
        # MIDI has implicit, .n() overrides with explicit
        midi = ts.MIDI(incomingVoice, scale="c:major")  # implicit
        midi.n("0 2 4", cycle=2, scale="a4:minor")  # explicit A4 minor
        print(f"Test 9 (Override explicit): should play A4=69, C5=72, E5=76")
    
    elif ACTIVE_TEST == 10:
        # Test 10: Override at .n() level - implicit over explicit
        # MIDI has explicit C5, .n() overrides with implicit
        midi = ts.MIDI(incomingVoice, scale="c5:major")  # explicit
        midi.n("0 2 4", cycle=2, scale="c:major")  # implicit
        print(f"Test 10 (Override implicit): incoming={incomingVoice.note}, follows incoming")
    
    elif ACTIVE_TEST == 11:
        # Test 11: Octave wrapping with explicit root
        # C4 major: degrees 7, 8, 9 = C5, D5, E5
        midi = ts.MIDI(incomingVoice, scale="c4:major")
        midi.n("7 8 9", cycle=2)
        print(f"Test 11 (Octave wrap): should play C5=72, D5=74, E5=76")
    
    elif ACTIVE_TEST == 12:
        # Test 12: Slowcat pattern with explicit root
        midi = ts.MIDI(incomingVoice, scale="c5:major")
        midi.n("<0!2 2 4 6>", cycle=2)
        print(f"Test 12 (Slowcat): C5 held 2 cycles, then E5, G5, B5")
    
    elif ACTIVE_TEST == 13:
        # Test 13: Default octave is now 4 (not 3)
        # "c:major" without octave uses C4 (60) as internal root
        midi = ts.MIDI(incomingVoice, scale="c:major")
        midi.n("0 7 14", cycle=2)  # degree 0, 7 (one octave up), 14 (two octaves up)
        print(f"Test 13 (Default oct 4): implicit, but internal root is C4=60")
    
    elif ACTIVE_TEST == 14:
        # Test 14: Compare C3 vs C4 explicit roots
        # First half: C3 major (48), second half: C4 major (60)
        midi = ts.MIDI(incomingVoice, scale="c3:major")
        midi.n("0", cycle=1)
        print(f"Test 14: Play C3=48, then change ACTIVE_TEST to 15")
    
    elif ACTIVE_TEST == 15:
        # Test 15: C4 major for comparison with test 14
        midi = ts.MIDI(incomingVoice, scale="c4:major")
        midi.n("0", cycle=1)
        print(f"Test 15: Play C4=60 (one octave higher than test 14)")

def onReleaseVoice(incomingVoice):
    ts.stop_patterns_for_voice(incomingVoice)
    
    for v in vfx.context.voices:
        if ts.get_parent(v) == incomingVoice:
            v.release()

def onTick():
    ts.update()
