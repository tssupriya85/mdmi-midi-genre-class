#!/usr/bin/python
import sys
import midiparser
import os
import csv

""" (Groups) """;          instrument_groups = ["Piano", "Chromatic Percussion", "Organ", "Guitar", "Bass", "Strings", "Ensemble", "Brass", "Reed", "Pipe", "Synth Lead", "Synth Pad", "Synth Effects", "Ethnic", "Percussive", "Sound effects"]

""" Piano """;                  instruments  = ["Acoustic Grand Piano", "Bright Acoustic Piano", "Electric Grand Piano", "Honky-tonk Piano", "Electric Piano 1", "Electric Piano 2", "Harpsichord", "Clavinet"]
""" Chromatic Percussion """;   instruments += ["Celesta", "Glockenspiel", "Music Box", "Vibraphone", "Marimba", "Xylophone", "Tubular Bells", "Dulcimer"]
""" Organ """;                  instruments += ["Drawbar Organ", "Percussive Organ", "Rock Organ", "Church Organ", "Reed Organ", "Accordion", "Harmonica", "Tango Accordion"]
""" Guitar """;                 instruments += ["Acoustic Guitar (nylon)", "Acoustic Guitar (steel)", "Electric Guitar (jazz)", "Electric Guitar (clean)", "Electric Guitar (muted)", "Overdriven Guitar", "Distortion Guitar", "Guitar Harmonics"]
""" Bass """;                   instruments += ["Acoustic Bass", "Electric Bass (finger)", "Electric Bass (pick)", "Fretless Bass", "Slap Bass 1", "Slap Bass 2", "Synth Bass 1", "Synth Bass 2"]
""" Strings """;                instruments += ["Violin", "Viola", "Cello", "Contrabass", "Tremolo Strings", "Pizzicato Strings", "Orchestral Harp", "Timpani"]
""" Ensemble """;               instruments += ["String Ensemble 1", "String Ensemble 2", "Synth Strings 1", "Synth Strings 2", "Choir Aahs", "Voice Oohs", "Synth Choir", "Orchestra Hit"]
""" Brass """;                  instruments += ["Trumpet", "Trombone", "Tuba", "Muted Trumpet", "French Horn", "Brass Section", "Synth Brass 1", "Synth Brass 2"]
""" Reed """;                   instruments += ["Soprano Sax", "Alto Sax", "Tenor Sax", "Baritone Sax", "Oboe", "English Horn", "Bassoon", "Clarinet"]
""" Pipe """;                   instruments += ["Piccolo", "Flute", "Recorder", "Pan Flute", "Blown Bottle", "Shakuhachi", "Whistle", "Ocarina"]
""" Synth Lead """;             instruments += ["Lead 1 (square)", "Lead 2 (sawtooth)", "Lead 3 (calliope)", "Lead 4 (chiff)", "Lead 5 (charang)", "Lead 6 (voice)", "Lead 7 (fifths)", "Lead 8 (bass + lead)"]
""" Synth Pad """;              instruments += ["Pad 1 (new age)", "Pad 2 (warm)", "Pad 3 (polysynth)", "Pad 4 (choir)", "Pad 5 (bowed)", "Pad 6 (metallic)", "Pad 7 (halo)", "Pad 8 (sweep)"]
""" Synth Effects """;          instruments += ["FX 1 (rain)", "FX 2 (soundtrack)", "FX 3 (crystal)", "FX 4 (atmosphere)", "FX 5 (brightness)", "FX 6 (goblins)", "FX 7 (echoes)", "FX 8 (sci-fi)"]
""" Ethnic """;                 instruments += ["Sitar", "Banjo", "Shamisen", "Koto", "Kalimba", "Bagpipe", "Fiddle", "Shanai"]
""" Percussive """;             instruments += ["Tinkle Bell", "Agogo", "Steel Drums", "Woodblock", "Taiko Drum", "Melodic Tom", "Synth Drum"]
""" Sound effects """;          instruments += ["Reverse Cymbal", "Guitar Fret Noise", "Breath Noise", "Seashore", "Bird Tweet", "Telephone Ring", "Helicopter", "Applause", "Gunshot"]

# Translate MIDI note numbers to internatinal note format
notes = ["C-", "C#", "D-", "D#", "E-", "F-", "F#", "G-", "G#", "A-", "A#", "B-"]
def note(note_number):
    return notes[note_number % 12] + str((note_number // 12) - 1)

# Translate instrument number to instrument name
def instrument(instrument_number):
    return instruments[instrument_number]

# Translate instrument number to the instrument group to which it belongs
def instrument_group(instrument_number):
    return instrument_groups[instrument_number // 8]

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

    info["filename"]          = file.lstrip(midi_library_path)
    info["artist"]            = artist
    info["genre"]             = genre
    info["num_tracks"]        = midi.num_tracks
    info["midi_division"]     = midi.division
    info["tempo"]             = []
    info["instruments"]       = []
    info["instrument_groups"] = []
    info["midi_format"]       = midi.format

    for track in midi.tracks:
        timings = []
        for event in track.events:
            if event.type == midiparser.voice.NoteOn:
                pass
                timings.append(event.absolute)
                #print "{NoteOn}", "Absolute:", event.absolute, "Note_no:", note(event.detail.note_no), "Velocity:", event.detail.velocity
                #print note(event.detail.note_no),
            if event.type == midiparser.voice.ProgramChange:
                if instrument(event.detail.amount) not in info["instruments"]: info["instruments"].append(instrument(event.detail.amount))
                if instrument_group(event.detail.amount) not in info["instrument_groups"]: info["instrument_groups"].append(instrument_group(event.detail.amount))
            if event.type == midiparser.meta.SetTempo:
                if event.detail.tempo not in info["tempo"]: info["tempo"].append(event.detail.tempo)
            if event.type == midiparser.meta.InstrumentName:
                if event.detail.text.strip() not in info["instruments"]: info["instruments"].append(event.detail.text.strip())
            if event.type == midiparser.meta.TrackName:
		pass #print "TrackName:", event.detail.text.strip()
	    if event.type == midiparser.meta.CuePoint:
		print "CuePoint:", event.detail.text.strip()
	    if event.type == midiparser.meta.Lyric:
		print "[Lyric]", event.detail.text.strip(),
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