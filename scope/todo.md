- [ ] Consolodate ts.exports.update() into ts.update() to reduce boilerplate
- [ ] Allow add `bpm` to `ts.MIDI` where sepcifying `bpm` will use an internal function to appropriately convert to `cycle`.
`bpm` and `cycle` cannot be defined together it has to be one or the other
midi = ts.MIDI(incomingVoice, bpm=ts.Context.bpm) # we still need to implement ts.Context
midi = ts.MIDI(incomingVoice, bpm=ts.Context.bpm, cycle=1) # cannot use both 
- [ ] Need a way to catch memory leaks inside def onTick(): and throw an error to stop eating resources