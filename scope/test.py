# TrapScript Bus System Tests
import flvfx as vfx
import trapscript as ts

ts.debug(True, level=1)

def createDialog():
    ui = ts.UI()
    ui.Knob(name='Cycle', d=2, min=0.5, max=4, export='bind')
    return ui.form

def onTriggerVoice(incomingVoice):
    midi = ts.MIDI(incomingVoice)
    
    # === BUS SYSTEM TESTS ===
    # Uncomment one test at a time
    
    # --- Test 1: Basic bus registration ---
    # Register pattern to 'melody' bus, access state in onTick
    #chain = midi.n("<[c4,e4,g4] [d4,f#4,a4] [e4,g#4,b4]>", c=ts.par.Cycle, bus='melody')
    
    # --- Test 2: Ghost pattern (mute=True) ---
    # Pattern ticks but produces no sound, state only
    midi.n("[0 2 <<5!2 6!4 6!2>!2 <4!2 5!4 5!2>!2 >]*2", c=ts.par.Cycle, mute=False, bus='melody')
    
    # --- Test 3: Multiple voices on same bus ---
    # Play two different notes, both register to 'melody'
    # midi.n("<0 4 7>", c=ts.par.Cycle, bus='melody')
    
    # --- Test 4: Chained access test ---
    # midi.n("<[c4,e4,g4] [d4,f#4,a4] [e4,g#4,b4]>", c=4, bus='chords')

def onReleaseVoice(incomingVoice):
    ts.stop_patterns_for_voice(incomingVoice)
    
    for v in vfx.context.voices:
        if ts.get_parent(v) == incomingVoice:
            v.release()

def onTick():
    melody = ts.bus('melody')
    pattern = melody.newest()
    if pattern and pattern['n'] == [0]:
        print(pattern.dict())
    ts.update()
