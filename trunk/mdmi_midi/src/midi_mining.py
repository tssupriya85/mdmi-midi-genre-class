#!/usr/bin/python

#  Batch MIDI File Information Extractor & Preprocessor
#  Made for the MDMI-F2011 Data Mining Project
#  by Martin Kjaer Svendsen & Perry Dahl Christensen

""" Note sequence loader configuration """

# Lets sequences contain tuples of (time, note) instead of just notes. Time is discretized.
# (would undiscretized be better for the sequence pattern mining algorithm?)
timestamp_notes = False

# Should there be empty slots in the array corresponding to gaps (pauses) between notes?
allow_gaps_in_sequences = False

# Notes per midi division, higher value means less change of note timing during time discretization, but more gaps between notes
discretization_granularity = 4

""" File loader configuration """

# Path of midi library. Should be set to local MDMI Dropbox folder
#midi_library_path   = 'E:\\My Documents\\My Dropbox\\MDMI\\' # MKS Stationary machine
midi_library_path   = 'C:\\Users\\mks\\Documents\\My Dropbox\\MDMI\\' # MKS Laptop
output_filename = '' # No filename means print to standard output
file_limit = 5 # Indicates how many files should be processed before stopping. -1 means that all files will be processed
print_note_sequences = 0 # Prints x first note sequences when done processing MIDI files

################################################################################

import sys
import midiparser
import os
import csv
import time
import types

""" ( Groups ) """;        instrument_groups = ["Piano", "Chromatic Percussion", "Organ", "Guitar", "Bass", "Strings", "Ensemble", "Brass", "Reed", "Pipe", "Synth Lead", "Synth Pad", "Synth Effects", "Ethnic", "Percussive", "Sound effects"]
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

notes = ["C-", "C#", "D-", "D#", "E-", "F-", "F#", "G-", "G#", "A-", "A#", "B-"]

# Translate MIDI note numbers to internatinal note format
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

# Prints a vertical line with text on it to the standard output
# Example: == Hello world! ==========================
def print_seperator(seperator_char, text):
   if len(text) != 0: text = " " + text + " "
   print(seperator_char * 2 + text + seperator_char * (40-len(text)))

# Prints a note sequence to the standard output
def print_note_sequence(sequence):
    print_seperator("-", "Sequence of length " + str(len(sequence)))
    for i, t in enumerate(sequence):
        if i % (4**3) == 0: print "=" + str(i) + "=",
        elif i % (4**2) == 0: print "-" + str(i) + "-",
        else: print "[" + str(i) + "]",
        for n in t:
            if timestamp_notes: print "(" + str(n[0]) + ")", note(n[1]),
            else: print note(n),
        print

global_notes = []

# Scans a midi file and returns a dictionary containing information about the file
def scan(file, artist, genre):
    info = {}
    try: midi = midiparser.File(file)
    except AssertionError: return # Return nothing if file could not be parsed

    info["filename"]          = file.lstrip(midi_library_path)
    info["artist"]            = artist
    info["genre"]             = genre
    info["num_tracks"]        = midi.num_tracks
    info["midi_division"]     = midi.division
    info["tempo"]             = []
    info["instruments"]       = []
    info["instrument_groups"] = []
    info["midi_format"]       = midi.format

    song_notes = []
    for track in midi.tracks:
        track_notes = []
        last = -1
        for event in track.events:
            if event.type == midiparser.voice.NoteOn:
                tick = int(round(event.absolute / (float(info["midi_division"] / discretization_granularity))))
                if tick >= last + 1:
                    if allow_gaps_in_sequences:
                        for _ in range(int(round(tick)-round(last))): track_notes.append([])
                    else:
                        track_notes.append([])
                    last = tick
                if timestamp_notes: new_note = tuple([tick, event.detail.note_no])
                else: new_note = event.detail.note_no
                track_notes[len(track_notes)-1].append(new_note)
                #print "{NoteOn}", "Absolute:", event.absolute, "Note_no:", note(event.detail.note_no), "Velocity:", event.detail.velocity
            if event.type == midiparser.voice.ProgramChange:
                if instrument(event.detail.amount) not in info["instruments"]: info["instruments"].append(instrument(event.detail.amount))
                if instrument_group(event.detail.amount) not in info["instrument_groups"]: info["instrument_groups"].append(instrument_group(event.detail.amount))
            if event.type == midiparser.meta.SetTempo:
                if event.detail.tempo not in info["tempo"]: info["tempo"].append(event.detail.tempo)
	    if event.type == midiparser.meta.KeySignature:
		pass
                #print "  KeySignature - Fifths:", event.detail.fifths, "Mode:", event.detail.mode
            if event.type == midiparser.meta.TimeSignature:
                pass
                #print "  TimeSignature - Numerator:", event.detail.numerator, "Log_denominator:", event.detail.log_denominator, \
                #"Midi_clocks:", event.detail.midi_clocks, "Thirty_seconds:", event.detail.thirty_seconds
        if track_notes: song_notes.append(track_notes)
    if song_notes: global_notes.append(song_notes)
    info["unknown_events"] = midi.UnknownEvents
    return info

# Processes files in library, one by one. Returns a count of the number of files processed.
def process_files(write_csv=True):
    # If no output_filename chosen, print to standard output, else to the chosen file
    if not output_filename: output = sys.stdout # No output_filename given, use standard output for csv data
    if output_filename: output = open(output_filename, 'wb') # output_filename given, open this file for writing csv data
    csv_writer = csv.writer(output, delimiter=',', quotechar='\"', quoting=csv.QUOTE_NONNUMERIC) # Create a CSV Writer instance for output

    # Scan all midi files in library. Directory format is expected to be \Genre\Artist\
    file_count = 0 # Counts the number of MIDI files processed
    for genre in os.listdir(midi_library_path): # Search all genre directories
        if genre[0] == ".": continue # Ignore hidden files
        if os.path.isdir(midi_library_path + genre):
            for artist in os.listdir(midi_library_path + genre): # Search all artist directories
                if artist[0] == ".": continue # Ignore hidden files
                for song in os.listdir(midi_library_path + genre + "\\" + artist): # Search for midi files in artist directory
                    if not os.path.isdir(midi_library_path + genre + "\\" + artist + "\\" + song): # Ignore any subpaths in artist directory
                        info = scan(midi_library_path + genre + "\\" + artist + "\\" + song, artist, genre) # Scan found midi file
                        if not info: # Skip files with errors
                            print "Error in MIDI file, skipped. (" + genre + "\\" + artist + "\\" + song + ")"
                            break
                        if write_csv and file_count == 0: csv_writer.writerow(info.keys()); # Print attribute header if this is the first file
                        file_count += 1
                        # Write data using csv writer. If type is list, remove the enclosing "[" and "]" before writing.
                        if write_csv: csv_writer.writerow([(str(value)[1:-1] if isinstance(value, types.ListType) else value) for key, value in info.items()]) # Print values
                        if file_count == file_limit: return file_count # If file_count limit reached, stop scanning
    return file_count

if __name__ == "__main__":
    start_time = time.time() # Remember starting time
    file_count = process_files(write_csv=True) # Do file processing
    elapsed = (time.time() - start_time) # Compute processing time

    print_seperator("=", "Done.")

    # Display number of files processed and time elapsed in easily readable format
    m, s = divmod(elapsed, 60)
    h, m = divmod(m, 60)
    print file_count, "files processed in",
    if h: print int(h), "hours,",
    if m: print int(m), "minutes and",
    if s: print "%.2f seconds." % s

    # Determine and print size of data structure containing note sequences
    # Print a selected number of note sequences to standard output
    sequence_size, sequence_count = 0, 0
    for song in global_notes:
        for track in song:
            if sequence_count < print_note_sequences: print_note_sequence(track)
            sequence_count += 1
            sequence_size += sys.getsizeof(track)
    print "Sequence data structure contains", sequence_count, "sequences, and uses", sequence_size // 1024.0**2, "MiB of memory."
