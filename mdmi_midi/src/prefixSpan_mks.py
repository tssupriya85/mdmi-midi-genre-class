#Info on the programmer
__author__ = "Perry D Christensen"
__date__ = "$18-04-2011 14:13:20$"

#imports inorder to run the program
#import itertools
import midi_mining

#Main method
def main():
    pfs = Prefixspan([[[1], [1, 2, 3], [1, 3], [4], [3, 6]], [[1, 4], [3], [2, 3], [1, 5]], [[5, 6], [1, 2], [4, 6], [3], [2]], [[5], [7], [1, 6], [3], [2], [3]]], 2)
    #The sequence passed to the prefixspan method above is identical to that of the example in the book (letters replaced with integers)
class Prefixspan:

    def __init__(self, S, supp):
        self.S = S
        self.supp = supp
        self.seq_pats = []
        self.seq_pats_as = []
        self.freq = self.prefixspan([], 0, self.S)
        print 'List of frequent sequences:'
        for sequence, support in self.seq_pats:
            print sequence, ":", support
        # Check for no fuckups in refactoring
        assert self.seq_pats == [([1], 4), ([2], 4), ([3], 4), ([4], 3), ([5], 3), ([6], 3), ([1, 1], 2), ([1, 2], 4), ([1, 3], 4), ([1, 4], 2), ([1, 6], 2), ([[1, 2]], 2), ([1, 2, 1], 2), ([1, 2, 3], 2), ([1, [2, 3]], 2), ([1, [2, 3], 1], 2), ([1, 3, 1], 2), ([1, 3, 2], 3), ([1, 3, 3], 3), ([1, 4, 3], 2), ([[1, 2], 3], 2), ([[1, 2], 4], 2), ([[1, 2], 6], 2), ([[1, 2], 4, 3], 2), ([2, 1], 2), ([2, 3], 3), ([2, 4], 2), ([2, 6], 2), ([[2, 3]], 2), ([2, 4, 3], 2), ([[2, 3], 1], 2), ([3, 1], 2), ([3, 2], 3), ([3, 3], 3), ([4, 2], 2), ([4, 3], 3), ([4, 3, 2], 2), ([5, 1], 2), ([5, 2], 2), ([5, 3], 2), ([5, 6], 2), ([5, 1, 2], 2), ([5, 1, 3], 2), ([5, 1, 3, 2], 2), ([5, 2, 3], 2), ([5, 3, 2], 2), ([5, 6, 2], 2), ([5, 6, 3], 2), ([5, 6, 3, 2], 2), ([6, 2], 2), ([6, 3], 2), ([6, 2, 3], 2), ([6, 3, 2], 2)]

    def prefixspan(self, a, l, S):

        '''
        SUPPORT COUNTING
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

        # TILF: Item freq count skal kun taelle op hvis det er 1) f0rste item 2) prefix ligger f0r den fundne indstans af item

        print 'S: ', S
        #Base case for recursion
        if not S: return a

        # Initialize frequent item list for singular and concatenable items
        freq, _freq = {}, {}

        for sequence in S: # Iterate the projected database to find frequent items
            freq_found, _freq_found = [], []
            for item_pos, item in enumerate(sequence):
                for i, object in enumerate(item):
                    """
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
                    """
                    #if item[0] == '_' and i == 1: _freq_found.append(object)
                    #else: freq_found.append(object)
                    length_residual_seq = len(item) - (item.index(object) + 1)
                    if item_pos == 0 and length_residual_seq > 0 and (item[0] == '_' or (len(a) > 0 and object == a[-1:][0])):
                        if item[item.index(object)+1] not in _freq_found: _freq_found.append(item[item.index(object)+1])

                    """
                    # Next step is to check for individual frequent items
                    # These items are not the same as the assembly items, and
                    # we therefore need to disregard items in the sequence  that
                    # is considered concatenatable items.
                    # SHOULD THE ENTIRE SEQUENCE BE DISREGARDED????
                    """
                    if item_pos == 0 and item[0] == '_': continue
                    if object not in freq_found: freq_found.append(object)

            for item in freq_found:
                if item not in freq: freq[item] = 1
                else: freq[item] += 1

            for item in _freq_found:
                if item not in _freq: _freq[item] = 1
                else: _freq[item] += 1

        print "FREQUENT ITEMSET"
        for aa, bb in freq.items(): print aa,":",bb
        for aa, bb in _freq.items(): print "_"+str(aa),":",bb

        # Items that does not have the required frequent support count are pruned from the frequent item lists.
        freq = dict((k,v) for k, v in freq.items() if v >= self.supp)
        _freq = dict((k,v) for k, v in _freq.items() if v >= self.supp)

        '''
        APPENDING ITEMS WITH MIN SUPPORT TO PREFIX
        All frequent items are appended to the prefix sequence alpha' (a_p) to
        be used for later generation of frequent sequences of length l+1.
        Furthermore frequent sequences of length l are appended to the set of
        all frequent sequences (seq_pats). The same goes for frequent concatenatable
        items. Since concatenatable items obviously does not apply when l = 0, only
        individual items are considered and appended to the list of sequential patterns.
        '''

        a_new = [a + [k] for k, v in freq.items()]
        freq_new = [(a + [k], v) for k, v in freq.items()] # Concatenate frequent list to get frequent list of l+1 sequences

        if l == 0: # Ingen underscore items
            _a_new = []
            _freq_new = []
        else:
            _a_new = [a[:-1] + [a[-1:] + [k]] for k, v in _freq.items()] # last item in a-prefix are concatenated with frequent item.
            _freq_new = [(a[:-1] + [a[-1:] + [k]], v) for k, v in _freq.items()] # Concatenate frequent list to get frequent list of l+1 sequences

        # If the concatenated frequent item lists are not empty, then append them to the overall list of frequent sequential patterns
        if freq_new:  [self.seq_pats.append(pattern) for pattern in freq_new]
        if _freq_new: [self.seq_pats.append(pattern) for pattern in _freq_new]

        '''
        The new projected database (suffixDB and _suffixDB) are generated. Here the currently
        alpha projected db are reduced to contain only items subsequent to the
        current frequent item, thus iteratively reducing the size of the alpha
        projected db.
        '''

        # TILF: Hvis ingen projected database skabes, skal der s0ges fremad for at se om prefix kommer senere

        print 'a_new: ', a_new
        print '_a_new: ', _a_new
        suffixDB = []
        _suffixDB = []

        """
        # Iterating all items in frequent item list.first item in the sequence.
        # If the sequence is prefixed with "_" we disregard it, as we are only looking for individual items.
        # When the item in the frequent list is found, we append the residual sequence (if any) to the projected
        # database along with a prefixed "_". All subsequent sequences after this, is appended to the projected
        # database in their entirity.
        # Finally the new build a-projected database, with respect to the frequent item k, is appended to a list
        # of projected databases used in subsequent recursions.
        """
        for k, v in freq.items():
            DB = []
            for sequence in S:
                projectedDB = []
                itemNotFound = True
                for item in sequence:
                    if item[0] == '_': continue
                    if itemNotFound:
                        try:
                            i = item.index(k)
                            itemNotFound = False
                            if len(item[i + 1:]) > 0:           # only if the sequence contains more items after the frequent item k, should
                                residual = ['_'] + item[i + 1:] # the residual sequence be appended
                                projectedDB.append(residual)                    
                        except: continue
                    else: projectedDB.append(item)
                if projectedDB: DB.append(projectedDB)
            if DB: suffixDB.append(DB)

        """
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
        """
        for k, v in _freq.items():
            DB = []
            for sequence in S:
                projectedDB = []
                itemNotFound = True
                for item_pos, item in enumerate(sequence):
                    if itemNotFound and len(item) > 1:
                        try:
                            i = item.index(k)
                            if item_pos == 0 and i != 0:  # Only if item is found in the first subsequence, and it is not
                                itemNotFound = False # the first item, can we claim that we found the right concatenatable item
                            if itemNotFound == False and len(item[i + 1:]) > 0:
                                residual = ['_']+item[i + 1:]  # only append if the residual subsequence contains at least 1 more item
                                projectedDB.append(residual)
                            # If item is never found, do nothing, therefore no elif clause.
                        except: continue
                    elif itemNotFound == False: projectedDB.append(item)
                if projectedDB: DB.append(projectedDB)
            if DB: _suffixDB.append(DB)

        '''
        The new alpha projected database are passed in recursive calls to the
        prefixspan method along with the new prefix of length l+1.
        Since the alpha projected database shrinks with each recursion, the algorithm
        terminates when reaching the base case (when the projected database is empty)
        '''

        [self.prefixspan(alpha, l+1, S_a) for (alpha, S_a) in zip(a_new, suffixDB)]
        [self.prefixspan(alpha, l+1, S_a) for (alpha, S_a) in zip(_a_new, _suffixDB)]

if __name__ == "__main__":
    main()
