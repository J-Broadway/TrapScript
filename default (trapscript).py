# TrapScript boilerplate
import flvfx as vfx
import trapscript as ts

def createDialog():
    ui = ts.UI()
    # Add controls here
    # ui.Knob(name='MyKnob', d=0.5, min=0, max=1)
    return ui.form

def onTriggerVoice(incomingVoice):
    midi = ts.MIDI(incomingVoice)
    # midi.trigger()

def onReleaseVoice(incomingVoice):
    ts.stop_patterns_for_voice(incomingVoice)
    for v in vfx.context.voices:
        if ts.get_parent(v) == incomingVoice:
            v.release()

def onTick():
    ts.update()



def onTriggerVoice(incomingVoice):
    midi_in = incomingVoice
    if midi_in.color == 0:
        midi_out = ts.MIDI(midi_in, cycle=0.75, scale="c:major")
        midi_out.n("0 3 5 7") # notes locked to c:major scale
    if midi_in.color == 1:
        midi_out = ts.MIDI(midi_in, cycle=0.75, scale="c:minor")
        midi_out.n("0 3 5 7", c=1) # notes locked to c:minor scale parent cycle overrided by child