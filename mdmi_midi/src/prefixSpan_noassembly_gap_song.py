# TEST!
# Info on the programmer
__author__ = "Perry D Christensen"
__date__ = "$18-04-2011 14:13:20$"

from collections import defaultdict

# Main method
def main():
    # This database is identical to that of the example in the book (letters replaced with integers)
    p1 = [[[1], [1, 2, 3], [1, 3], [4], [4], [4], [3, 6]], [[1, 4], [3], [2, 3], [1, 5]], [[5, 6], [1, 2], [4, 6], [3], [2]], [[5], [7], [1, 6], [3], [2], [3]]]

    # More interesting example (for this simplified version without assembly)
    p2 = [[[9], [9], [4], [2], [3], [4], [4], [4], [2]], [[2], [3], [4], [3], [2]], [[2], [3], [9], [4]], [[7], [2], [3], [4], [2], [3], [4], [2], [4], [4], [4], [3], [4]]]

    # Another (simple) test database
    p3 = [ [ [0, 0], [1, 1], [2, 2] ], [ [0, 0], [1, 1], [2, 2] ], [ [2],[4],[4],[4],[4,3],[3] ] ]

    # Choose your database ...
    input = [p1,p2,p3] # Three "songs"

    # Print chosen database
    print "Input:"
    for song in input:
        print "Song:"
        for seq in song:
            print seq
    print

    # Run algorithm
    pfs = frequent_sequences(input, 3)

    # Print result
    print "Result:"
    for sequence, support in pfs:
        print sequence, ":", support


# Returns all frequent patterns with minimum support from sequence database S
def frequent_sequences(S, min_support):
    # Recursive PrefixSpan sequence pattern mining algorithm
    def prefixspan(a, l, S):
        # Count support for items in projected database
        freq = defaultdict(int) # Dictionary that automatically creates an int key if it is not already in it (means that "if item not in freq: freq[item] = 1" can be avoided)
        for song in S:
            found_items = []
            for sequence in song:
                i = len(a) # This is to make first item count
                for item in sequence:
                    if i == len(a): # Zero-Gap Constraint: Item must be either the first item in projected sequence or be prefixed by alfa to count
                        if tuple(item) not in found_items: found_items.append(tuple(item))
                        i = 0
                        if len(a) == 0: continue
                    if item == a[i]:
                        i += 1
                    else: i = 0
            for item in found_items: freq[item] += 1

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
            song_suffixes = []
            for song in S:
                sequence_suffixes = []
                for sequence in song:
                    i = len(prefix) - 1 # This is to make first item count
                    for j, item in enumerate(sequence):
                        if item == prefix[i]: i += 1
                        else: i = 0
                        if i == len(prefix): # Zero-Gap Constraint: Either first item in sequence or an item prefixed by prefix is frequent
                            if j < len(sequence) - 1: # Only project if one or more items are left in sequence
                                sequence_suffixes.append(sequence[j+1:])
                                i = 0
                            break
                if sequence_suffixes: song_suffixes.append(sequence_suffixes)
            if song_suffixes: prefix_suffix.append((prefix, song_suffixes))

        '''
        for prefix, suffix in prefix_suffix:
            print "prefix",prefix
            for song in suffix:
                print "  song"
                for s in song:
                    print "   ", s
        '''

        # Recurse on projected database(s)
        for prefix, suffix in prefix_suffix:
            prefixspan(prefix, l+1, suffix)

    # Execute algorithm and return result
    sequence_patterns = []
    prefixspan([], 0, S)
    return sequence_patterns

if __name__ == "__main__":
    main()
