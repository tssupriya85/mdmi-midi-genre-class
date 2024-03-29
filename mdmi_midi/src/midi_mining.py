#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
  Batch MIDI File Information Extractor & Preprocessor
  Made for the MDMI-F2011 Data Mining Project
  by Martin Kjaer Svendsen & Perry Dahl Christensen
"""


note_formats = ["RAW", "ONE_OCTAVE", "SIMPLE_DIFF", "ADVANCED_DIFF"]

octave_discretize_notes = False
""" Note sequence loader configuration """
# RAW: Sequences consists of plain MIDI note numbers
# ONE_OCTAVE: MIDI note numbers discretized to (0..11)
# SIMPLE_DIFF: Each new node is changed to the difference to the previous one
# ADVANCED_DIFF: Ignores consecutive instances of the same note; Differences in notes and between notes inside chords
note_format = "ADVANCED_DIFF"
# Lets sequences contain tuples of (time, note) instead of just notes. Time is discretized.
timestamp_notes = False
# Allow empty slots in the array corresponding to gaps (pauses) between notes
allow_gaps_in_sequences = False
# Notes per midi division, higher value means less change of note timing during time discretization, but more gaps between notes
discretization_granularity = 4

""" Frequent sequence occurrence counter configuration """
# Minimum length of sequences to count occurrences for
min_sequence_length = 2
# Minimum support for frequent patterns as a percentage of total songs
min_support_percentage = 25

""" File loader configuration """
# Path of midi library. Should be set to local MDMI Dropbox folder
midi_library_path = 'E:\\My Documents\\My Dropbox\\MDMI\\midi_library\\genre_sorted\\' # MKS Stationary machine
#midi_library_path = 'C:\\Users\\mks\\Documents\\My Dropbox\\MDMI\\' # MKS Laptop
#output_filename = 'C:\\Users\\mks\\Documents\\My Dropbox\\MDMI\\output_1000files_min_seq_2_min_sup_40pct.arff' # No filename means print to standard output
output_filename = 'C:\Skod.arff'
file_limit = 25 # Indicates how many files should be processed before stopping. -1 means that all files will be processed
print_note_sequences = 0 # Prints x first note sequences when done processing MIDI files

################################################################################

import sys
import midiparser
import os
import time
import types
import prefixSpan_noassembly_gap_song
from math import copysign
from sets import Set

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

# Entry 0 = MIDI intrument no. 24
non_standard_percussion_lower =\
["Zap/High Q/Click sound", "Brush hit hard", "Brush circle", "Brush hit soft", "Brush hit and circle", "Drumroll", "Castanets", "Snare Drum 3 (same tone as drumroll snare)", "Drumsticks hitting each other", "Bass Drum 3", "Hard hit snare"]
# Entry 0 = MIDI intrument no. 35
standard_percussion = ["Bass Drum 2", "Bass Drum 1", "Side Stick/Rimshot", "Snare Drum 1", "Hand Clap", "Snare Drum 2", "Low Tom 2", "Closed Hi-hat", "Low Tom 1",
"Pedal Hi-hat", "Mid Tom 2", "Open Hi-hat", "Mid Tom 1", "High Tom 2", "Crash Cymbal 1", "High Tom 1", "Ride Cymbal 1", "Chinese Cymbal",
"Ride Bell", "Tambourine", "Splash Cymbal", "Cowbell", "Crash Cymbal 2", "Vibra Slap", "Ride Cymbal 2", "High Bongo", "Low Bongo",
"Mute High Conga", "Open High Conga", "Low Conga", "High Timbale",  "Low Timbale", "High Agog�", "Low Agog�", "Cabasa", "Maracas"
"Short Whistle", "Long Whistle", "Short G�iro", "Long G�iro", "Claves", "High Wood Block", "Low Wood Block", "Mute Cu�ca", "Open Cu�ca",
"Mute Triangle", "Open Triangle"]
# Entry 0 = MIDI intrument no. 82
non_standard_percussion_higher = ["Shaker", "Jingle bell/Sleigh bells", "Bell tree"]

percussion = non_standard_percussion_lower + standard_percussion + non_standard_percussion_higher

notes = ["C-", "C#", "D-", "D#", "E-", "F-", "F#", "G-", "G#", "A-", "A#", "B-"]

# ARFF

arff_attribute_types = {"artist" : "STRING", "filename" : "STRING", "midi_division" : "NUMERIC", "midi_format" : "NUMERIC", "num_tracks" : "NUMERIC", "genre" : "NOMINAL", "tempo" : "RELATIONAL", "unknown_events" : "NUMERIC", "sequences" : "RELATIONAL"}
arff_nominal_attribute_values = {"instrument_groups" : instrument_groups, "instruments" : instruments, "genre" : []}

# Translate MIDI note numbers to international note format
def note(note_number):
    return notes[note_number % 12] + str((note_number // 12) - 1)

# Translate drum notes (found in MIDI channel 10) into names of drum sounds
def drum(note_number):
    return percussion[note_number - 24]

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

def all_same(items): # Return True if all elements in the list are the same
    return all(x == items[0] for x in items)

# Prints a vertical line with text on it to the standard output
# Example: == Hello world! ==========================
def print_seperator(seperator_char, text):
   if len(text) != 0: text = " " + text + " "
   print(seperator_char * 2 + text + seperator_char * (80-len(text)))

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

global_notes = [] # Note sequences, indexed by [song][sequence][item in sequence]
global_info = [] # Song information, indexed by [song]

# Scans a midi file and adds dictionary containing information from file to global_info and note sequences to global_notes
# Returns error message if a problem problem is encountered, otherwise None.
def scan(file, artist, genre):
    info = {}
    try: midi = midiparser.File(file)
    except AssertionError: # Error reading headers
        return "File corrupt or not a MIDI file."
    except IndexError: # File just suddently stops in the middle of something (IndexError on the variable containing the file contents)
        return "Unexpected end of file."
    
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
        previous_note = 0
        track_notes = []
        last = -1
        for event in track.events:
            if event.type == midiparser.voice.NoteOn:
                if event.channel+1 == 10: # Ignore percussion track
                    continue
                tick = int(round(event.absolute / (float(info["midi_division"]) / discretization_granularity)))
                if tick >= last + 1:
                    if track_notes: track_notes[len(track_notes)-1].sort() # Sort notes so that e.g. [1, 2] == [2, 1]
                    if allow_gaps_in_sequences: 
                        for _ in range(int(round(tick)-round(last))): track_notes.append([])
                    else:
                        track_notes.append([])
                    last = tick
                if timestamp_notes: new_note = tuple([tick, event.detail.note_no])
                else:
                    if   octave_discretize_notes: new_note = event.detail.note_no % 12
                    elif note_format == "RAW" or note_format == "ADVANCED_DIFF": new_note = event.detail.note_no
                    elif note_format == "ONE_OCTAVE": new_note = event.detail.note_no % 12 # Discretize to 12 distinct notes (0..11)
                    elif note_format == "SIMPLE_DIFF": new_note = (event.detail.note_no - previous_note)

                track_notes[len(track_notes)-1].append(new_note)
                #print "{NoteOn}", "Absolute:", event.absolute, "Note_no:", note(event.detail.note_no), "Velocity:", event.detail.velocity
                if note_format == "SIMPLE_DIFF": previous_note = event.detail.note_no
            if event.type == midiparser.voice.ProgramChange:
                try:
                    if instrument(event.detail.amount) not in info["instruments"]: info["instruments"].append(instrument(event.detail.amount))
                    if instrument_group(event.detail.amount) not in info["instrument_groups"]: info["instrument_groups"].append(instrument_group(event.detail.amount))
                except IndexError:
                    return "Instrument number " + str(event.detail.amount) + " out of bounds."
            if event.type == midiparser.meta.SetTempo:
                if event.detail.tempo not in info["tempo"]: info["tempo"].append(event.detail.tempo)
	    if event.type == midiparser.meta.KeySignature:
		pass
                #print "  KeySignature - Fifths:", event.detail.fifths, "Mode:", event.detail.mode
            if event.type == midiparser.meta.TimeSignature:
                pass
                #print "  TimeSignature - Numerator:", event.detail.numerator, "Log_denominator:", event.detail.log_denominator, \
                #"Midi_clocks:", event.detail.midi_clocks, "Thirty_seconds:", event.detail.thirty_seconds
        pp = False
        sign = lambda x: int(copysign(1, x))
        uniqify = lambda x: list(Set(x))
        if track_notes and note_format == "ADVANCED_DIFF":
            if pp: old_track_notes = [list(item) for item in track_notes]
            new_track_notes = []
            old_chord, last_solo = [], -1
            for i in range(1, len(track_notes)):
                if not track_notes[i]: continue # Neccessary if gaps are allowed
                if len(track_notes[i]) > 1:
                    new_chord = []
                    for j in range (1, len(track_notes[i])):
                        diff2 = track_notes[i][j] - track_notes[i][j-1]
                        new_chord.append(abs(diff2) % 12 * sign(diff2))
                    new_chord = uniqify(new_chord)
                    if new_chord == old_chord: continue
                    old_chord = new_chord[:]
                    new_track_notes.append(new_chord)
                else:
                    old_chord = []
                    diff = track_notes[i][0] - last_solo
                    new = [abs(diff) % 12 * sign(diff)]
                    if track_notes[i] == last_solo: continue
                    last_solo = track_notes[i][0]
                    new_track_notes.append(new)

                #for j in range (1, len(track_notes[i])):
                #    diff2 = track_notes[i][j] - track_notes[i][j-1]
                #    new_track_notes[-1].append(abs(diff2) % 12 * sign(diff2))
            track_notes = new_track_notes
            '''
            old = 0
            for i in range(len(track_notes)):
                if not track_notes[i]: continue
                diff = track_notes[i][0] - old
                old  = track_notes[i][0]
                if i != 0: track_notes[i][0] = diff
                else: track_notes[i][0] = 0
                old2 = old
                for j in range (1, len(track_notes[i])):
                    diff = track_notes[i][j] - old2
                    old2 = track_notes[i][j]
                    track_notes[i][j] = diff
#                for j in range (1, len(track_notes[i])):
#                    track_notes[i][j] = track_notes[i][0] + track_notes[i][j] - old
#            if track_notes[0]: track_notes[0][0] = 0
            '''
            if pp:
                for i in range(len(old_track_notes)):
                    try: print "%-50s %-50s" % (old_track_notes[i], track_notes[i])
                    except: pass
                print
        if track_notes: song_notes.append(track_notes)
    #info["unknown_events"] = midi.UnknownEvents
    if song_notes:
        global_notes.append(song_notes)
        global_info.append(info)
    else:
        return "No note sequences could be extracted from file."
    return

# Processes files in library, one by one. Returns a count of the number of files processed, and files skipped due to errors
def process_files():
    # Scan all midi files in library. Directory format is expected to be \Genre\Artist\
    file_count = 0 # Counts the number of MIDI files processed
    files_skipped = 0
    files_processed = 0 # Counts the number of files where information can actually be extracted
    for genre in os.listdir(midi_library_path): # Search all genre directories
        if genre[0] == ".": continue # Ignore hidden files
        if os.path.isdir(midi_library_path + genre):
            arff_nominal_attribute_values["genre"].append(genre) # Add genre to list of values of nominal attribute "genre" (ARFF header)
            for artist in os.listdir(midi_library_path + genre): # Search all artist directories
                if artist[0] == ".": continue # Ignore hidden files
                for song in os.listdir(midi_library_path + genre + "\\" + artist): # Search for midi files in artist directory
                    if not os.path.isdir(midi_library_path + genre + "\\" + artist + "\\" + song): # Ignore any subpaths in artist directory
                        error = scan(midi_library_path + genre + "\\" + artist + "\\" + song, artist, genre) # Scan found midi file
                        file_count += 1
                        if file_count % 1000 == 0:
                            print
                            print_seperator("-", str(file_count / 1000) + ".000 files done.")
                        if error: # Skip files with errors
                            print
                            print "Error processing " + genre + "\\" + artist + "\\" + song + ":", error
                            files_skipped += 1
                            continue
                        files_processed += 1
                        sys.stdout.write(".")
                        if file_count == file_limit:
                            print
                            return files_processed, files_skipped # If file_count limit reached, stop scanning
    print
    return files_processed, files_skipped

# Converts a timestamt to a pretty human-readable string, e.g. "2 hours, 46 minutes and 12.30 seconds"
def pretty_time(timestamp):
    min, sec = divmod(timestamp, 60)
    hour, min = divmod(min, 60)
    hour, min = int(hour), int(min)
    s = ""
    if hour:
        s += str(hour)
        if hour == 1: s += " hour, "
        else: s += " hours, "
    if min:
        s += str(min)
        if min == 1: s += " minute and "
        else: s += " minutes and "
    if sec: s += "%.1f seconds" % sec
    return s

# Writes content of global_info to a file in the CSV format, with or without an ARFF header telling WEKA about the attribute types
def write_file(arff_header=True):
    # If no output_filename chosen, print to standard output, else to the chosen file
    if not output_filename: output = sys.stdout # No output_filename given, use standard output for csv data
    if output_filename: output = open(output_filename, 'wb') # output_filename given, open this file for writing csv data

    def writeln(s): output.write(s + "\n")

    """ Write ARFF Header """
    if arff_header:
        attributes = sorted(global_info[0].keys())
        longest_attribute = max([len(attribute) for attribute in attributes])
        attribute_format = "@ATTRIBUTE %-" + str(longest_attribute) + "s %s"
        relation = output_filename.split("\\")
        relation = relation[len(relation)-1]
        writeln("@RELATION " + relation)
        writeln("")
        for attribute in sorted(attributes):
            if arff_attribute_types[attribute] == "NOMINAL":
                line = attribute_format % (attribute, "")
                line += "{"
                line += ", ".join([(str(value) if (isinstance(value, types.IntType) or value == "?") else "\"" + value + "\"") for value in arff_nominal_attribute_values[attribute]])
                line += "}"
                writeln(line)
            else:
                writeln(attribute_format % (attribute, arff_attribute_types[attribute]))
                if arff_attribute_types[attribute] == "RELATIONAL":
                    for i in range(len(global_info[0][attribute])):
                        writeln("  @ATTRIBUTE " + attribute + str(i) + " NUMERIC")
                    writeln("@END " + attribute)
        writeln("")
        writeln("@DATA")

    """ Write ARFF Body """
    #csv_writer = csv.writer(output, delimiter=',', quotechar='\"', quoting=csv.QUOTE_NONE) # Create a CSV Writer instance for output
    for info in global_info:
        #writeln(",".join([(str(value) if (isinstance(value, types.IntType) or value == "?") else "\"" + value + "\"") for value in info]))
        writeln(",".join([(str(value)[1:-1] if isinstance(value, types.ListType) else "\"" + value + "\"" if isinstance(value, types.StringType) and value != "?" else str(value)) for key, value in sorted(info.items())]))
        #csv_writer.writerow([(str(value)[1:-1] if isinstance(value, types.ListType) else "\"" + value + "\"" if isinstance(value, types.StringType) and value != "?" else value) for key, value in sorted(info.items())])

# Main method
if __name__ == "__main__":
    # Check command line arguments and set parameters accordingly
    if len(sys.argv) > 1:
        print "Command line arguments:"
        for arg_no, arg in enumerate(sys.argv):
            if arg_no == 1:
                print "  midi_library_path =", arg + "\\"
                midi_library_path = arg + "\\"
            if arg_no == 2:
                print "  output_filename =", arg
                output_filename = arg
            if arg_no == 3:
                try: val = int(arg)
                except: sys.exit(arg + " is not a number.")
                print "  file_limit =", val
                file_limit = val
            if arg_no == 4:
                try: val = int(arg)
                except: sys.exit(arg + " is not a number.")
                if val < 0 or val > 100: sys.exit("min_support_percentage out of bounds (should be between 0 and 100).")
                print "  min_support_percentage =", val
                min_support_percentage = val
            if arg_no == 5:
                try: val = int(arg)
                except: sys.exit(arg + " is not a number.")
                if val < 0: sys.exit("min_sequence_length out of bounds (should be >0).")
                print "  min_sequence_length =", val
                min_sequence_length = val
            if arg_no == 6:
                if arg not in note_formats: sys.exit("Unknown note_format. Possible values: " + note_formats)
                print "  note_format =", arg
                note_format = arg
    # No command line parameters set, inform user about the possibilites
    else:
        print "No command line arguments, using default values."
        print "Usage: midi_mining.py midi_library_path output_filename file_limit min_support_percentage min_sequence_length note_format"

    global_start_time = time.time() # Remember starting time for whole program

    # If all files are processed, write this
    if file_limit < 0: print_seperator("=", "Processing all files.")
    # If some files processed, write how many
    else: print_seperator("=", "Processing " + str(file_limit) + " files.")

    start_time = time.time() # Remember starting time
    files_processed, files_skipped = process_files() # Do file processing
    elapsed = (time.time() - start_time) # Compute processing time

    # Print time elapsed
    print "Information extracted from", files_processed, "files (" + str(files_skipped), "files skipped) in", pretty_time(elapsed) + "."

    # Determine size of data structure containing note sequences (and print a selected number of note sequences to standard output if print_note_sequences > 0)
    sequence_size, sequence_count = 0, 0
    sequence_lengths = []
    for song in global_notes:
        for track in song:
            if sequence_count < print_note_sequences: print_note_sequence(track)
            sequence_count += 1
            sequence_size += sys.getsizeof(track)
            sequence_lengths.append(len(track))
    print "Sequence data structure contains", sequence_count, "sequences, and uses", sequence_size // 1024.0**2, "MiB of memory."
    print "Max track length:", max(sequence_lengths), "  Min track length:", min(sequence_lengths)
    print "Average track length:", sum(sequence_lengths) / len(sequence_lengths), "  Median track length:", sorted(sequence_lengths)[len(sequence_lengths) / 2]

    # Compute minimum support according to chosen percentage
    min_support = int(round(files_processed * (min_support_percentage / 100.0)))
    print_seperator("=", "Mining sequences with minimum support " + str(min_support) + " (" + str(min_support_percentage) + "%)")

    start_time = time.time() # Remember starting time
    frequent_sequences = prefixSpan_noassembly_gap_song.frequent_sequences(global_notes, min_support) # Run algorithm
    elapsed = (time.time() - start_time) # Compute processing time

    # Display number of files processed and time elapsed in easily readable format
    print len(frequent_sequences), "frequent sequences mined in", pretty_time(elapsed) + "."

    # Print initially mined frequent patterns
    repetetive = 0
    for sequence, support in frequent_sequences:
        if len(sequence) == 1 or not all_same(sequence):
            print sequence, ":", support
        else:
            print "*", sequence, ":", support
            repetetive += 1
    if repetetive > 0: print repetetive, "sequences marked with (*) contains only repetitions of the same element."

    # Prune frequent sequences having too short length (< min_sequence_length) or containing only duplicate items
    if note_format not in ["SIMPLE_DIFF", "ADVANCED_DIFF"]:
        len_before = len(frequent_sequences)
        frequent_sequences = [(sequence, frequency) for sequence, frequency in frequent_sequences if len(sequence) == 1 or not all_same(sequence)]
        diff_percent = int(round( ((len_before - len(frequent_sequences)) / (len_before * 1.0)) * 100 ))
        print len_before - len(frequent_sequences), "(" + str(diff_percent) + "%) of the sequences pruned because they only contains repetitions of the same element."
    len_before = len(frequent_sequences)
    frequent_sequences = [(sequence, frequency) for sequence, frequency in frequent_sequences if len(sequence) >= min_sequence_length]
    diff_percent = int(round( ((len_before - len(frequent_sequences)) / (len_before * 1.0)) * 100 ))
    print len_before - len(frequent_sequences), "(" + str(diff_percent) + "%) of the sequences pruned because they have a length less than", min_sequence_length

    # Attribute naming format: (seq001, seq002, seq003, ...)
    sequence_attribute_naming_format = "seq%0" + str(len(str(len(frequent_sequences)))) + "d"

    # Print remaining frequent sequences after pruning
    print_seperator("=", "Remaining frequent sequences:")
    for seq_no, (sequence, support) in enumerate(frequent_sequences):
        print sequence_attribute_naming_format % seq_no, "=", sequence, ":", support
        arff_attribute_types[sequence_attribute_naming_format % seq_no] = "NUMERIC"

    # Frequent sequences as a list (without the frequency count of the dictionary)
    found_sequences = [sequence for sequence, frequency in frequent_sequences]

    # Counts the occurrence of each sequence in each song
    occurrence_count = [[0 for _ in range(len(frequent_sequences))] for _ in range(len(global_notes))]

    # Count occurrences of each sequence in each song
    start_time = time.time() # Remember starting time
    print_seperator("=", "Counting occurences of " + str(len(found_sequences)) + " frequent sequences in " + str(len(global_info)) + " songs.")
    for song_no, song in enumerate(global_notes):
        for track in song:
            cursors = [0 for _ in range(len(found_sequences))]
            for item in track:
                for i in range(len(found_sequences)):
                    if item == found_sequences[i][cursors[i]]: # Hit
                        cursors[i] += 1
                        if cursors[i] == len(found_sequences[i]): # Occurrence of whole frequence sequence found
                            cursors[i] = 0
                            occurrence_count[song_no][i] += 1
                    else: # Miss
                        cursors[i] = 0
    elapsed = (time.time() - start_time) # Compute processing time
    print "Done in", pretty_time(elapsed) + "."

    # Convert instrument and global_instrument lists into a number of boolean variables (to make WEKA happy)
    for instrument_no, instrument in enumerate(instruments):
        new_name = "instrument_%03d_%s" % (instrument_no, instrument.replace(" ", "_"))
        arff_attribute_types[new_name] = "NOMINAL"
        arff_nominal_attribute_values[new_name] = [0,1]
    for instrument_group_no, instrument_group in enumerate(instrument_groups):
        new_name = "instrument_group_%02d_%s" % (instrument_group_no, instrument_group.replace(" ", "_"))
        arff_attribute_types[new_name] = "NOMINAL"
        arff_nominal_attribute_values[new_name] = [0,1]
    arff_attribute_types["tempo"] = "NUMERIC" # Because we take average of all tempi now (WEKA does not like variable length lists)
    for i in range(len(global_info)):
        for instrument_no, instrument in enumerate(instruments):
            new_name = "instrument_%03d_%s" % (instrument_no, instrument.replace(" ", "_"))
            if instrument in global_info[i]["instruments"]: global_info[i][new_name] = 1
            else: global_info[i][new_name] = 0
        del global_info[i]["instruments"]
        for instrument_group_no, instrument_group in enumerate(instrument_groups):
            new_name = "instrument_group_%02d_%s" % (instrument_group_no, instrument_group.replace(" ", "_"))
            if instrument_group in global_info[i]["instrument_groups"]: global_info[i][new_name] = 1
            else: global_info[i][new_name] = 0
        del global_info[i]["instrument_groups"]
        # Make tempo equal to the average of all tempi (no tempo means tempo = ? (= "unknown", according to the WEKA ARFF standard)
        if global_info[i]["tempo"]:
            global_info[i]["tempo"] = sum(global_info[i]["tempo"]) / len(global_info[i]["tempo"])
        else: global_info[i]["tempo"] = "?"
        for j in range(len(found_sequences)):
            global_info[i][sequence_attribute_naming_format % j] = occurrence_count[i][j]
            #global_info[i]["sequences"].append(occurrence_count[i][j])

    # Write ARFF file, either to file og standard output if output_filename = ''
    print "Writing result in ARFF format."
    write_file(arff_header=True)
    print_seperator("=", "Done writing ARFF.")

    global_elapsed = (time.time() - global_start_time) # Compute processing time for whole program

    # Print total processing time for whole program and say goodbye.
    print "Program done. Total runtime was " + pretty_time(global_elapsed) + "."
    print "Bye." # \A makes a beep sound
    print chr(7) # Beep!

    '''
    # Print the occurrence counts for each individual song
    for song_no, song in enumerate(global_notes):
        print "Song", song_no
        for track in song:
            print " ", track
        print "-----------------------------------------------------------------------------------------------------------------------------------------"
        for i in range(len(found_sequences)):
            print found_sequences[i], ":", occurrence_count[song_no][i]
    '''
