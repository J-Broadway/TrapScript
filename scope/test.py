# TrapScript Alias Refactor Tests
# Tests canonical and alias forms for all refactored parameters
import flvfx as vfx
import trapscript as ts

ts.debug(True, level=1)

# ============================================================
# SELECT TEST TO RUN (set to number 1-15, or 0 for default)
# ============================================================
ACTIVE_TEST = 0

def createDialog():
    ui = ts.UI()
    ui.Knob(name='Cycle', d=2, min=0.5, max=4, export='bind')
    return ui.form

def onTriggerVoice(incomingVoice):
    # --------------------------------------------------------
    # ALIAS REFACTOR 1.2 TESTS
    # Tests both canonical and alias parameter forms
    # --------------------------------------------------------
    
    if ACTIVE_TEST == 0:
        # === DEFAULT: Original slowcat test with canonical params ===
        midi = ts.MIDI(incomingVoice, scale="c5:major")
        midi.n("<0!2 3 5 7>", cycle=2)  # canonical: cycle=
    
    # --------------------------------------------------------
    # MIDI.__init__() - cycle parameter
    # --------------------------------------------------------
    
    elif ACTIVE_TEST == 1:
        # Test: MIDI with canonical 'cycle' parameter
        midi = ts.MIDI(incomingVoice, cycle=2, scale="c5:major")
        midi.n("0 2 4")  # Should inherit cycle=2
    
    elif ACTIVE_TEST == 2:
        # Test: MIDI with alias 'c' parameter (backwards compat)
        midi = ts.MIDI(incomingVoice, c=2, scale="c5:major")
        midi.n("0 2 4")  # Should inherit cycle=2
    
    # --------------------------------------------------------
    # midi.n() - cycle parameter
    # --------------------------------------------------------
    
    elif ACTIVE_TEST == 3:
        # Test: midi.n() with canonical 'cycle' parameter
        midi = ts.MIDI(incomingVoice, scale="c5:major")
        midi.n("0 2 4", cycle=2)  # canonical
    
    elif ACTIVE_TEST == 4:
        # Test: midi.n() with alias 'c' parameter
        midi = ts.MIDI(incomingVoice, scale="c5:major")
        midi.n("0 2 4", c=2)  # alias
    
    # --------------------------------------------------------
    # ts.note() / ts.n() - cycle and root parameters
    # --------------------------------------------------------
    
    elif ACTIVE_TEST == 5:
        # Test: ts.note() with canonical parameters
        ts.note("0 3 5 7", cycle=4, root=60, parent=incomingVoice)
    
    elif ACTIVE_TEST == 6:
        # Test: ts.note() with alias parameters
        ts.note("0 3 5 7", c=4, r=60, parent=incomingVoice)
    
    elif ACTIVE_TEST == 7:
        # Test: ts.n() with canonical parameters
        ts.n("0 3 5 7", cycle=4, root=72, parent=incomingVoice)
    
    elif ACTIVE_TEST == 8:
        # Test: ts.n() with alias parameters
        ts.n("0 3 5 7", c=4, r=72, parent=incomingVoice)
    
    elif ACTIVE_TEST == 9:
        # Test: ts.n() with mixed canonical and alias
        ts.n("0 3 5 7", cycle=4, r=60, parent=incomingVoice)
    
    # --------------------------------------------------------
    # ts.note() / ts.n() - bus parameter
    # --------------------------------------------------------
    
    elif ACTIVE_TEST == 10:
        # Test: ts.note() with bus parameter (was bus_name)
        ts.note("0 1 2 3", cycle=1, root=60, parent=incomingVoice, bus='test_bus')
        # Verify bus registration (BusRegistry is a dict, use len() directly)
        print(f"Bus 'test_bus' count: {len(ts.bus('test_bus'))}")
    
    elif ACTIVE_TEST == 11:
        # Test: ts.n() with bus parameter
        ts.n("0 1 2 3", cycle=1, root=60, parent=incomingVoice, bus='test_bus')
        print(f"Bus 'test_bus' count: {len(ts.bus('test_bus'))}")
    
    elif ACTIVE_TEST == 12:
        # Test: midi.n() with bus parameter
        midi = ts.MIDI(incomingVoice, scale="c5:major")
        midi.n("0 2 4", cycle=2, bus='midi_bus')
        print(f"Bus 'midi_bus' count: {len(ts.bus('midi_bus'))}")
    
    # --------------------------------------------------------
    # Single.trigger() - length parameter
    # --------------------------------------------------------
    
    elif ACTIVE_TEST == 13:
        # Test: Single.trigger() with canonical 'length' parameter
        note = ts.Single(midi=60, velocity=100)
        note.trigger(length=0.5)  # canonical
    
    elif ACTIVE_TEST == 14:
        # Test: Single.trigger() with alias 'l' parameter
        note = ts.Single(midi=60, velocity=100)
        note.trigger(l=0.5)  # alias
    
    elif ACTIVE_TEST == 15:
        # Test: Single with various alias params then trigger with length
        note = ts.Single(m=72, v=80, l=2)  # aliases for midi, velocity, length
        note.trigger(length=1)  # override length at trigger time
    
    # --------------------------------------------------------
    # SCALE SYSTEM TESTS (unchanged, for regression)
    # --------------------------------------------------------
    
    elif ACTIVE_TEST == 100:
        # Chromatic mode (no scale)
        midi = ts.MIDI(incomingVoice)
        midi.n("0 3 5 7", cycle=2)
    
    elif ACTIVE_TEST == 101:
        # Scale mode - major triad
        midi = ts.MIDI(incomingVoice, scale="c5:major")
        midi.n("0 2 4", cycle=2)
    
    elif ACTIVE_TEST == 102:
        # Scale mode with inheritance
        midi = ts.MIDI(incomingVoice, cycle=1, scale="c5:major")
        midi.n("0 2 4")  # Inherits cycle=1

def onReleaseVoice(incomingVoice):
    ts.stop_patterns_for_voice(incomingVoice)
    
    for v in vfx.context.voices:
        if ts.get_parent(v) == incomingVoice:
            v.release()

def onTick():
    ts.update()
