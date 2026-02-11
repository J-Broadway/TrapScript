# TrapScript boilerplate
import flvfx as vfx
import trapscript as ts

def createDialog():
    ui = ts.UI()
    return ui.form

def onTriggerVoice(incomingVoice):
    midi = ts.MIDI(incomingVoice)
    test = midi.n("<0 1 2 3>", export='test', c=1) # export object to be used in other scopes
    test = test.dict() # access objects internal dictionary

    # Looking to be able to do stuff like this:
    if test.dict()['pattern'] == 0:
        print('sup')

def onReleaseVoice(incomingVoice):
    ts.stop_patterns_for_voice(incomingVoice)
    for v in vfx.context.voices:
        if ts.get_parent(v) == incomingVoice:
            v.release()

def onTick():
    test = ts.midi.exports('test') # can now access original midi.n object
    print(test.dict()) # would print out a dicitonaroy state of test every tick similar to ts.debug('True', level=2)
    print(test.changed()) # would print out a dictionary state of test every event change similar to ts.debug('True', level=1) via has_onset()
    test.changed('pattern') # could perhaps check for changes for specific keys
    ts.update()