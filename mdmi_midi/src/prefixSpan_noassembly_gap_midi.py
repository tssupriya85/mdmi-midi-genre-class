#Info on the programmer
__author__ = "Perry D Christensen"
__date__ = "$18-04-2011 14:13:20$"

#import itertools
import midi_mining

# Main method
def main():
    print_input = False

    print "Processing MIDI files..."
    midi_mining.process_files(write_csv=False) # Asks midi_mining to process MIDI files
    print "Done."

    input = [item for sublist in midi_mining.global_notes for item in sublist] # Toss all sequences into one big list (no song division anymore)

    # Example of using global_notes: Print all sequences
#    for track in input:
#        midi_mining.print_note_sequence(track)

    # Print chosen database
    if print_input:
        print "Input:"
        for seq in input:
            print seq
        print

    # Run algorithm
    pfs = frequent_sequences(input, 5)

    # Print result
    print "Result:"
    for sequence, support in pfs:
        print sequence, ":", support


# Returns all frequent patterns with minimum support from sequence database S
def frequent_sequences(S, min_support):
    # Recursive PrefixSpan sequence pattern mining algorithm
    def prefixspan(a, l, S):
        # Count support for items in projected database
        freq = {}
        for sequence in S:
            found_items = []
            i = len(a) # This is to make first item count
            for item in sequence:
                if i == len(a): # Zero-Gap Constraint: Item must be either the first item in projected sequence or be prefixed by alfa to count
                    if tuple(item) not in found_items: found_items.append(tuple(item))
                    i = 0
                    if len(a) == 0: continue
                if item == a[i]:
                    i += 1
                else: i = 0
            for item in found_items:
                if item not in freq: freq[item] = 1
                else: freq[item] += 1

        # Prune items with support below minimum
        freq = dict((k,v) for k, v in freq.items() if v >= min_support)

        # Frequent items are appended to a to get a'
        a_new = [a + [list(k)] for k, v in freq.items()]

        # Concatenate frequent list to get frequent list of l+1 sequences
        freq_new = [(a + [list(k)], v) for k, v in freq.items()]

        # Append new frequent items to the overall list of frequent sequential patterns
        for pattern in freq_new: sequence_patterns.append(pattern)

        # Construct projected databases S|a'
        prefix_suffix = []
        for prefix in a_new:
            suffix = []
            for sequence in S:
                i = len(prefix) - 1 # This is to make first item count
                for j, item in enumerate(sequence):
                    if item == prefix[i]: i += 1
                    else: i = 0
                    if i == len(prefix): # Zero-Gap Constraint: Either first item in sequence or an item prefixed by prefix is frequent
                        if j < len(sequence) - 1: # Only project if one or more items are left in sequence
                            suffix.append(sequence[j+1:])
                            i = 0
                        break
            if suffix:
                prefix_suffix.append((prefix, suffix))

        # Recurse on projected database(s)
        for prefix, suffix in prefix_suffix:
            prefixspan(prefix, l+1, suffix)

    # Execute algorithm and return result
    sequence_patterns = []
    prefixspan([], 0, S)
    return sequence_patterns

if __name__ == "__main__":
    main()
