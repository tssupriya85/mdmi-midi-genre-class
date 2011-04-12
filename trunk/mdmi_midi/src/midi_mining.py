#!/usr/bin/python

import sys
import midiparser
import os

def scan(file, artist, genre):
    song_data = {}

    midi = midiparser.File(file)

    song_data["filename"] = file
    song_data["artist"] = artist
    song_data["genre"] = genre
    song_data["num_tracks"] = midi.num_tracks
    song_data["midi_division"] = midi.division
    song_data["tempo"] = set()
    song_data["intruments"] = set()
    #print "MIDI Format:", midi.format

    for track in midi.tracks:
        #print "--- track ---"
        for event in track.events:
	    if event.type == midiparser.voice.NoteOn:
                pass
                #print "{NoteOn}", "Absolute:", event.absolute, "Note_no:", event.detail.note_no, "Velocity:", event.detail.velocity
            if event.type == midiparser.meta.SetTempo:
                song_data["tempo"] = song_data["tempo"] | set([event.detail.tempo])
                #print "SetTempo:", event.detail.tempo
            if event.type == midiparser.meta.InstrumentName:
                song_data["instruments"] = song_data["instruments"] | set([event.detail.text.strip()])
                print "Instrument:", event.detail.text.strip()
            if event.type == midiparser.meta.TrackName:
		pass
                #print "TrackName:", event.detail.text.strip()
	    if event.type == midiparser.meta.CuePoint:
		print "CuePoint:", event.detail.text.strip()
	    if event.type == midiparser.meta.Lyric:
		print "Lyric:", event.detail.text.strip()
	    #if event.type == midiparser.meta.KeySignature:
		# ...
    return song_data

def main(argv):
    path = '..\\data\\Library\\'

    # ignore = [".svn", "all-wcprops"]
    # Scan all files in directory
    for genre in os.listdir(path):
        if genre[0] == ".": continue
        if os.path.isdir(path + genre):
            for artist in os.listdir(path + genre):
                if artist[0] == ".": continue
                for song in os.listdir(path + genre + "\\" + artist):
                    if not os.path.isdir(path + genre + "\\" + artist + "\\" + song):
                        print "Genre:", genre, "| Artist:", artist, "| Song:", song
                        print scan(path + genre + "\\" + artist + "\\" + song, artist, genre)

if __name__ == "__main__":
    main(sys.argv)