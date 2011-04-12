#!/usr/bin/python
import sys
import midiparser
import os
import csv

# Translate MIDI note numbers to internatinal note format

instrument_groups = ["Piano", "Chromatic Percussion", "Organ", "Guitar", "Bass", "Strings", "Ensemble", "Brass", "Reed", "Pipe", "Synth Lead", "Synth Pad", "Synth Effects", "Ethnic", "Percussive", "Sound effects"]
# Piano
instruments  = ["Acoustic Grand Piano", "Bright Acoustic Piano", "Electric Grand Piano", "Honky-tonk Piano", "Electric Piano 1", "Electric Piano 2", "Harpsichord", "Clavinet"]
# Chromatic Percussion
instruments += ["Celesta", "Glockenspiel", "Music Box", "Vibraphone", "Marimba", "Xylophone", "Tubular Bells", "Dulcimer"]
# Organ
instruments += ["Drawbar Organ", "Percussive Organ", "Rock Organ", "Church Organ", "Reed Organ", "Accordion", "Harmonica", "Tango Accordion"]
# Guitar
instruments += ["24 Acoustic Guitar (nylon)", "25 Acoustic Guitar (steel)", "26 Electric Guitar (jazz)", "27 Electric Guitar (clean)", "28 Electric Guitar (muted)", "29 Overdriven Guitar", "30 Distortion Guitar", "31 Guitar Harmonics"]
# Bass
instruments += ["32 Acoustic Bass", "33 Electric Bass (finger)", "34 Electric Bass (pick)", "35 Fretless Bass", "36 Slap Bass 1", "37 Slap Bass 2", "38 Synth Bass 1", "39 Synth Bass 2"]
# Strings
instruments += ["40 Violin", "41 Viola", "42 Cello", "43 Contrabass", "44 Tremolo Strings", "45 Pizzicato Strings", "46 Orchestral Harp", "47 Timpani"]
# Ensemble
instruments += ["48 String Ensemble 1", "49 String Ensemble 2", "50 Synth Strings 1", "51 Synth Strings 2", "52 Choir Aahs", "53 Voice Oohs", "54 Synth Choir", "55 Orchestra Hit"]
# Brass
instruments += ["56 Trumpet", "57 Trombone", "58 Tuba", "59 Muted Trumpet", "60 French Horn", "61 Brass Section", "62 Synth Brass 1", "63 Synth Brass 2"]
# Reed
instruments += ["64 Soprano Sax", "65 Alto Sax", "66 Tenor Sax", "67 Baritone Sax", "68 Oboe", "69 English Horn", "70 Bassoon", "71 Clarinet"]
# Pipe
instruments += ["72 Piccolo", "73 Flute", "74 Recorder", "75 Pan Flute", "76 Blown Bottle", "77 Shakuhachi", "78 Whistle", "79 Ocarina"]
# Synth Lead
instruments += ["80 Lead 1 (square)", "81 Lead 2 (sawtooth)", "82 Lead 3 (calliope)", "83 Lead 4 (chiff)", "84 Lead 5 (charang)", "85 Lead 6 (voice)", "86 Lead 7 (fifths)", "87 Lead 8 (bass + lead)"]
# Synth Pad
instruments += ["88 Pad 1 (new age)", "89 Pad 2 (warm)", "90 Pad 3 (polysynth)", "91 Pad 4 (choir)", "92 Pad 5 (bowed)", "93 Pad 6 (metallic)", "94 Pad 7 (halo)", "95 Pad 8 (sweep)"]
# Synth Effects
instruments += ["96 FX 1 (rain)", "97 FX 2 (soundtrack)", "98 FX 3 (crystal)", "99 FX 4 (atmosphere)", "100 FX 5 (brightness)", "101 FX 6 (goblins)", "102 FX 7 (echoes)", "103 FX 8 (sci-fi)"]
# Ethnic
instruments += ["104 Sitar", "105 Banjo", "106 Shamisen", "107 Koto", "108 Kalimba", "109 Bagpipe", "110 Fiddle", "111 Shanai"]
# Percussive
instruments += ["112 Tinkle Bell", "113 Agogo", "114 Steel Drums", "115 Woodblock", "116 Taiko Drum", "117 Melodic Tom", "118 Synth Drum"]
# Sound effects
instruments += ["119 Reverse Cymbal", "120 Guitar Fret Noise", "121 Breath Noise", "122 Seashore", "123 Bird Tweet", "124 Telephone Ring", "125 Helicopter", "126 Applause", "127 Gunshot"]

notes = ["C-", "C#", "D-", "D#", "E-", "F-", "F#", "G-", "G#", "A-", "A#", "B-"]
def note(note_number):
    return notes[note_number % 12] + str((note_number / 12) - 1)

# Return greatest common divisor amongst list of numbers using Euclid's Algorithm.
def greatest_common_divisor(list):
    def gcd(a, b): # GCD for two numbers
        while b: a, b = b, a % b
        return a
    return reduce(gcd, list) # Return gcd(...(gcd(a,b),c))...)

# Scans a midi file and returns a dictionary containing information about the file
def scan(file, artist, genre):
    info = {}
    midi = midiparser.File(file)

    info["filename"]        = file.lstrip(midi_library_path)
    info["artist"]          = artist
    info["genre"]           = genre
    info["num_tracks"]      = midi.num_tracks
    info["midi_division"]   = midi.division
    info["tempo"]           = []
    info["instruments"]     = []
    info["MIDI Format"]     = midi.format

    for track in midi.tracks:
        timings = []
        for event in track.events:
            if event.type == midiparser.voice.NoteOn:
                pass
                timings.append(event.absolute)
                #print "{NoteOn}", "Absolute:", event.absolute, "Note_no:", note(event.detail.note_no), "Velocity:", event.detail.velocity
                #print note(event.detail.note_no),
            if event.type == midiparser.voice.ProgramChange:
                print "ProgramChange: ", instruments[event.detail.amount]
            if event.type == midiparser.meta.SetTempo:
                if event.detail.tempo not in info["tempo"]: info["tempo"].append(event.detail.tempo)
            if event.type == midiparser.meta.InstrumentName:
                if event.detail.text.strip() not in info["instruments"]: info["instruments"].append(event.detail.text.strip())
            if event.type == midiparser.meta.TrackName:
		pass #print "TrackName:", event.detail.text.strip()
	    if event.type == midiparser.meta.CuePoint:
		print "CuePoint:", event.detail.text.strip()
	    if event.type == midiparser.meta.Lyric:
		print "Lyric:", event.detail.text.strip(),
	    #if event.type == midiparser.meta.KeySignature:
		# ...
        if timings:
            gcd = greatest_common_divisor(timings)
            timings = [x / gcd for x in timings]
            #print("gcd:", gcd, "-", timings)
            #print "(timing)"
    info["unknown_events"] = midi.UnknownEvents
    return info

########################################################################################

midi_library_path = '..\\data\\Library\\'
output_filename = ''

def main(argv):
    # If no output_filename chosen, print to standard output, else to the chosen file
    if output_filename: output = open(output_filename, 'wb') # output_filename given, use this
    if not output_filename: output = sys.stdout # No output_filename given, use standard output
    csv_writer = csv.writer(output, delimiter=';', quotechar='\"', quoting=csv.QUOTE_MINIMAL) # Create a CSV Writer instance for output

    # Scan all midi files in library. Directory format is expected to be \Genre\Artist\
    first = True # Used for checking if this is the first file, and attribute headers therefore should be printed
    for genre in os.listdir(midi_library_path): # Search all genre directories
        if genre[0] == ".": continue # Ignore hidden files
        if os.path.isdir(midi_library_path + genre):
            for artist in os.listdir(midi_library_path + genre): # Search all artist directories
                if artist[0] == ".": continue # Ignore hidden files
                for song in os.listdir(midi_library_path + genre + "\\" + artist): # Search for midi files in artist directory
                    if not os.path.isdir(midi_library_path + genre + "\\" + artist + "\\" + song): # Ignore any subpaths in artist directory
                        info = scan(midi_library_path + genre + "\\" + artist + "\\" + song, artist, genre) # Scan found midi file
                        if first: csv_writer.writerow(info.keys()); first = False # Print attribute header if this is the first file
                        csv_writer.writerow([value for key, value in info.items()]) # Print values

if __name__ == "__main__":
    main(sys.argv)