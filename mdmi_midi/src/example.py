#!/usr/bin/python
import midi_mining

print "Processing MIDI files..."
midi_mining.process_files(write_csv=False) # Asks midi_mining to process MIDI files
print "Done."

# The note sequence data structure can now be accessed using midi_mining.global_notes

# Example of using global_notes: Print all sequences
for song in midi_mining.global_notes:
    for track in song:
        midi_mining.print_note_sequence(track)

