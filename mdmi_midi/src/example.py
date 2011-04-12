#!/usr/bin/python

import sys
import midiparser

def main(argv):
    if len(argv) < 2:
	print "midicsv.py [filename]"
	return

    midi = midiparser.File(argv[1])

    print midi.file, midi.format, midi.num_tracks, midi.division

    for track in midi.tracks:
	print "Track: ", track
        for event in track.events:
	    if event.type == midiparser.voice.NoteOn:
		print "NoteOn", vent.absolute,
		print event.detail.note_no, event.detail.velocity
	    if event.type == midiparser.meta.TrackName: 
		print event.detail.text.strip()
	    if event.type == midiparser.meta.CuePoint:
		print event.detail.text.strip()
	    if event.type == midiparser.meta.Lyric:
		print event.detail.text.strip()
	    #if event.type == midiparser.meta.KeySignature: 
		# ...
    
if __name__ == "__main__":
    main(sys.argv)

