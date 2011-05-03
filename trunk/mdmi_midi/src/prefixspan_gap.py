#Info on the programmer
__author__ = "Perry D Christensen"
__date__ = "$18-04-2011 14:13:20$"

#imports inorder to run the program
import itertools
#import midi_mining

#Main method
def main():
    pfs = Prefixspan([[[1], [1, 2, 3], [1, 3], [4], [3, 6]], [[1, 4], [3], [2, 3], [1, 5]], [[5, 6], [1, 2], [4, 6], [3], [2]], [[5], [7], [1, 6], [3], [2], [3]]], 2)
    #The sequence passed to the prefixspan method above is identical to that of the example in the book (letters replaced with integers)
class Prefixspan:

    def __init__(self, S, supp):
        self.S = S
        self.supp = supp
        self.seq_pats = []
        self.gap = 1
        self.prefixspan([], 0, self.S)
        print 'list of frequent sequences: ' + str(self.seq_pats)

    def prefixspan(self, a, l, S):

        '''
        All items in each sequence of the projected sequence database, S, are
        iterated to check for frequent items. Only the first instance in each
        sequence are taken into account.
        Items with a support count larger than the minimum support requirements
        (supp) are kept in a datastructure freq holding item and supportcount.
        When considering sequences we differ between individual items and
        subsets with multiple items (i.e. individual items and items part of a
        subsequence of items). Items in longer subsequences are events that happens
        concurrently.
        '''

        print 'S: ', S
        #Base case for recursion
        if not S:
            return a

        freq = {}  # Initialize frequent item list for singular items
        _freq = {} # Initialize frequent item list for concatenatable items

        for songs in S: # Iterate the projected database to find frequent items
            tabu = []
            _tabu = []
            for s_num, seq in enumerate(songs):
                concatenatedSeq = False
                for item_num, item in enumerate(seq):
                    # First check if the first sequence in the projected database is already part of a
                    # potentially concatenatable sequence and if that sequence has more items left for
                    # concatenation. If that is the case, check the first sequence for frequent concatenatable
                    # items.
                    # If this is not the case, than alternatively check if the last item in the prefix
                    # is equal to the current item and again only consider the first sequence and only if
                    # the first residual sequence after the item matching the last item in the prefix is
                    # larger than 0.
                    # The reason for this check is to ensure that concatanatable items are counted correctly
                    # (i.e. we wish to avoid overlooking items that has an incorrectly low support count).
#HUSK AT TAGE HOEJDE FOR gap stoerrelsen
                    length_residual_seq = len(seq[seq.index(item)+1:])
                    if (seq[0] == '_' and length_residual_seq > 0 and s_num == 0)\
                    or (len(a) > 0 and item == a[-1:][0] and length_residual_seq > 0 and s_num == 0):
                        #Add item to _freq and increment count to 1, if the is not already in the frequent item list
                        if seq[seq.index(item)+1] not in _freq:
                            _freq[seq[seq.index(item)+1]] = 1
                        #Only consider the first element in the sequence.
                        elif item in _tabu:
                            continue
                        else:
                            _freq[seq[seq.index(item)+1]] += 1
                            _tabu.append(item)

                    # Next step is to check for individual frequent items
                    # These items are not the same as the assembly items, and
                    # we therefore need to disregard items in the sequence  that
                    # is considered concatenatable items.
                    if s_num == 0 and seq[0] == '_':    #item_num < 2 and this extra condition was not needed
                        concatenatedSeq = True
                        continue



                    # After disregarding concatenatable items, items are appended to
                    # a frequent list in the same way as concatenatable items are

                    # Only consider 1st item (i.e. either first after concatenated sequence
                    # or first non concatenated sequence
                    if s_num == 0 or s_num <= self.gap and concatenatedSeq:
                        if item not in freq:
                            freq[item] = 1
                            tabu.append(item)
                        elif item in tabu:
                            continue
                        else:
                            freq[item] += 1
                            tabu.append(item)

        # Items that does not have the required frequent support count are pruned from the frequent item lists.
        for k, v in freq.items():
            if v < self.supp:
                del freq[k]

        for k, v in _freq.items():
            if v < self.supp:
                del _freq[k]

        '''
        All frequent items are appended to the prefix sequence alpha' (a_p) to
        be used for later generation of frequent sequences of length l+1.
        Furthermore frequent sequences of length l are appended to the set of
        all frequent sequences (seq_pats). The same goes for frequent concatenatable
        items. Since concatenatable items obviously does not apply when l = 0, only
        individual items are considered and appended to the list of sequential patterns.
        '''

        if l == 0:
            a_p = [a + [k] for k, v in freq.items()]
            freq2 = [([k], v) for k, v in freq.items()]
            _a_p = []
            _freq2 = []
        else:
            a_p = [a + [k] for k, v in freq.items()]
            freq2 = [(a + [k], v) for k, v in freq.items()] # Concatenate frequent list to get frequent list of l+1 sequences
            _a_p = [a[:-1] + [a[-1:] + [k]] for k, v in _freq.items()] # last item in a-prefix are concatenated with frequent item.
            _freq2 = [(a[:-1] + [a[-1:] + [k]], v) for k, v in _freq.items()] # Concatenate frequent list to get frequent list of l+1 sequences

        # If the concatenated frequent item lists are not empty, then append them to the overall list of frequent sequential patterns
        if not not freq2:
            [self.seq_pats.append(pattern) for pattern in freq2]
        if not not _freq2:
            [self.seq_pats.append(pattern) for pattern in _freq2]

        '''
        The new projected database (suffixDB and _suffixDB) are generated. Here the currently
        alpha projected db are reduced to contain only items subsequent to the
        current frequent item, thus iteratively reducing the size of the alpha
        projected db.
        '''

        print 'a_p: ', a_p
        print '_a_p: ', _a_p
        suffixDB = []
        _suffixDB = []

        # Iterating all items in frequent item list.
        # For each item in the frequent item list, we find the first item in the sequence.
        # If the sequence is prefixed with "_" we disregard it, as we are only looking for individual items.
        # When the item in the frequent list is found, we append the residual sequence (if any) to the projected
        # database along with a prefixed "_". All subsequent sequences after this, is appended to the projected
        # database in their entirity.
        # Finally the new build a-projected database, with respect to the frequent item k, is appended to a list
        # of projected databases used in subsequent recursions.
        for k, v in freq.items():
                DB = []
                for song in S:
                    projectedDB = []
                    itemNotFound = True
                    for seq in song:
                        if seq[0] == '_':
                            continue
                        if itemNotFound:
                            try:
                                i = seq.index(k)
                                itemNotFound = False
                                if len(seq[i + 1:]) > 0:         # only if the sequence contains more items after the frequent item k, should
                                    residual = ['_']+seq[i + 1:] # the residual sequence be appended
                                    projectedDB.append(residual)
                            except:
                                continue
                        else:
                            projectedDB.append(seq)
                    if not projectedDB: # If the projectedDB is empty (i.e. no sequential pattern is evident
#HER HANDLES HVIS DER IKKE FINDES ET PATTERN I DEN AKTUELLE SEQUENCE
                        # There is not apparent pattern. We therefore need to find out if there is another pattern,
                        # identical to the prefix, later on in the sequence. If this pattern, with the frequent item
                        # k appended to it exist, then return it and append it to DB.
                        hiddenSuffix = checkAndProcessHiddenPatterns(song, a, k, False) #False indicates that the item is not concatenatable
                        if hiddenSuffix:
                            DB.append(hiddenSuffix)
                    else:
                        DB.append(projectedDB)
                if not not DB:
                    suffixDB.append(DB)

        # Iterating all items in the list of frequent concatenatable items
        # The items in this list a treated differently than the other frequent items,
        # as only items that are part of a larger subsequence (i.e. subsequence of length at least 2)
        # If the item is found in the subsequence, and the subsequence is the first subsequence in the
        # sequence and the frequent item k is not the first item in the sequence (i.e. the first item in the
        # subsequence will always be "_"), then we consider the item to be found, and we can append the suffix
        # to a build of the projected database with respect to that frequent item. If such an item does not exist,
        # then the projected database will just be empty (itemNotFound will continue to be true).
        # If the item is found however, and it is found in the first subsequence, then we have found the correct
        # item that is eligible for concatenation. itemNotFound will be set to False, an the residual subsequence
        # will be added, if any. All subsequent individual items or subsequences will be appended to the new projected
        # database as well.

        if not _freq:
            pass
        else:
            for k, v in _freq.items():
                DB = []
                for song in S:
                    projectedDB = []
                    itemNotFound = True
                    for num, seq in enumerate(song):
                        if itemNotFound and len(seq) > 1:
                            try:
                                i = seq.index(k)
                                if num == 0 and i != 0:  # Only if item is found in the first subsequence, and it is not
                                    itemNotFound = False # the first item, can we claim that we found the right concatenatable item
                                if itemNotFound == False and len(seq[i + 1:]) > 0:
                                    residual = ['_']+seq[i + 1:]  # only append if the residual subsequence contains at least 1 more item
                                    projectedDB.append(residual)
                                # If item is never found, do nothing, therefore no elif clause.
                            except:
                                continue
                        elif itemNotFound == False:
                            projectedDB.append(seq)
                    if not not projectedDB:
                        DB.append(projectedDB)
                if not not DB:
                    _suffixDB.append(DB)

        '''
        The new alpha projected database are passed in recursive calls to the
        prefixspan method along with the new prefix of length l+1.
        Since the alpha projected database shrinks with each recursion, the algorithm
        terminates when reaching the base case (when the projected database is empty)
        '''

        [self.prefixspan(alpha, l+1, S_a) for (alpha, S_a) in zip(a_p, suffixDB)]
        [self.prefixspan(alpha, l+1, S_a) for (alpha, S_a) in zip(_a_p, _suffixDB)]

    def findPrefix(track, a):

        return prefixExists, projDB

    def checkAndProcessHiddenPatterns(song, a, k, isConcat):
        # We check if a pattern, equivalent to the prefix a, exist in the song/track.
        # If it does, we check if we can append the frequent item k to the pattern.
        # If we can do this, then we return the projected database relative to the
        # concatenation of a and [k].
        # isConcat is a boolean operator that is used to determine if the k we are
        # looking for is to be concatenated to the last item of the prefix a.
        index = 0
        for num, element in enumerate(song):
            e_no = 0
            # If a[index] holds more than one element, we have to iterate the list
            if isinstance(a[index], list):
                i = 0
                for one in a[index]:
                    if index == len(a): # We reached the end of the prefix (i.e. we found a new hidden prefix)
                        pass #temporary
                    if not element[i:]:
                        index = 0
                        break
                    if one in element[i:]:
                        i = element.index(all)+1
                        index += 1
                    else:
                        index = 0
            else:
                if a[index] in element:
                    index += 1 # move on to next element as a[index] is a singular item, we don't wish to check other items in that element of 'song'
                else:
                    index = 0
            if index == len(a):     # We reached the end of the prefix (i.e. we found a new hidden prefix)

                break

if __name__ == "__main__":
    main()