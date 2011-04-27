#Info on the programmer
__author__ = "Perry D Christensen"
__date__ = "$18-04-2011 14:13:20$"

#imports inorder to run the program
import itertools
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
        print 'list of frequent sequences: ' + str(self.seq_pats)

    def prefixspan(self, a, l, S):

        '''
        All items in each sequence of the projected sequence database, S, are
        iterated to check for frequent items. Only the first instance in each
        sequence are taken into account.
        Items with a support count larger than the minimum support requirements
        (supp) are kept in a datastructure freq holding item and supportcount.
        '''

        #print 'alpha (prefix) passed: ' + str(a)
        #print 'length \'l\' passed: ' + str(l)
        #print 'S_a (alphaprojected db) passed: ' + str(S)
        print 'S: ', S
        if not S:
            return a                                            #base case for recursion

        freq = {}
        _freq = {}
        for songs in S:
            tabu = []
            _tabu = []
            for num, seq in enumerate(songs):
                isInSeq = False
                for no, item in enumerate(seq):
                    if len(a) > 0 and item == a[-1:][0]:#[0]:     #Testing if the current item is equal to the last item in alpha
                        isInSeq = True                          #If that is the case, seq is eligible for assembly items
                    length_residual_seq = len(seq[seq.index(item)+1:])
                    if (len(a) > 0 and isInSeq and length_residual_seq > 0 and num == 0) or (seq[0] == '_' and length_residual_seq > 0 and num == 0): #item == '_':
                        # if a is not empty, the item is equal to the last element of a
                        #and if there are still items left in that sequence
                        #(i.e. an item immediately to the right of the current item)
                        #Implement something to handle assembly items (i.e. iterate through items and find
                            #print 'seq', seq
                            #print 'seq[seq.index(item)+1:]', seq[seq.index(item)+1:], seq.index(item)+1
                        if seq[seq.index(item)+1] not in _freq:
                            _freq[seq[seq.index(item)+1]] = 1                   #Add item to _freq
                        elif item in _tabu:                                     #Only consider the first element in the sequence
                            continue
                        else:
                            _freq[seq[seq.index(item)+1]] += 1                  #Increment support count
                            _tabu.append(item)
                    if no < 2 and num == 0 and seq[0] == '_':#no < 2 and                    #disregard assemble marker '_' and the
                        continue                                                #first element in the first sequence in a

                    if item not in freq:                                        #Other items not applying to the above
                        #print 'new freq item: ', item, freq, seq
                        freq[item] = 1
                        tabu.append(item)
                    elif item in tabu:       #tabu is used to ensure that only the first item in each sequence is taken into account
                        continue
                    else:
                        #print 'increment freq item: ', item, freq, seq
                        freq[item] += 1
                        tabu.append(item)

        #print 'FREQ BEFORE PRUNING', freq
        #print '_FREQ BEFORE PRUNING', _freq

        for k, v in freq.items():
            if v < self.supp:
                del freq[k]

        for k, v in _freq.items():
            if v < self.supp:
                del _freq[k]

        print 'FREQ', freq
        print '_FREQ', _freq

        '''
        All frequent items are appended to the prefix sequence alpha' (a_p) to
        be used for later generation of frequent sequences of length l+1.
        Furthermore frequent sequences of length l are appended to the set of
        all frequent sequences (seq_pats)
        '''

        if l == 0:
            a_p = [a + [k] for k, v in freq.items()]            #concatenate a with frequent items to generate new frequent sequential patterns of length 1
            freq2 = [([k], v) for k, v in freq.items()]
            _a_p = []
            _freq2 = []
            #No frequent assemble items in first iteration
        else:
            a_p = [a + [k] for k, v in freq.items()]    #concatenate each frequent sequence with the frequent items from projected database
            freq2 = [(a + [k], v) for k, v in freq.items()] # replace a with x

            #print 'a: ', a
            #print 'a[-1:] ', a[-1:]
            #print 'a[:-1] ', a[:-1]

            _a_p = [a[:-1] + [a[-1:] + [k]] for k, v in _freq.items()]
            _freq2 = [(a[:-1] + [a[-1:] + [k]], v) for k, v in _freq.items()]
            '''_a_p = []
            _freq2 = ()
            for k, v in _freq.items():
                _a_p = _a_p + a[:-1] + [a[-1:] + [k]]
                if not _freq2:
                    _freq2 = [(a[:-1] + [a[-1:] + [k]], v)]
                else:
                    _freq2 = _freq2, [( a[:-1] + [a[-1:] + [k]], v )]'''

            #print 'a_p, freq2: ', a_p, freq2
            #print '_a_p, _freq2: ', _a_p, _freq2
            #print 'new partitioned prefixes (alpha prime sequences): ' + str(a_p)

        if not not freq2:                                       #as long as freq2 is not empty, append it to the overall list of frequent sequences
            [self.seq_pats.append(pattern) for pattern in freq2]
        if not not _freq2:
            [self.seq_pats.append(pattern) for pattern in _freq2]
        '''
        The new projected database (suffix) are generated. Here the currently
        alpha projected db are reduced to contain only items subsequent to the
        current frequent item, thus iteratively reducing the size of the alpha
        projected db.
        '''

        print 'a_p: ', a_p
        print '_a_p: ', _a_p
        #print 'S: ', S
        suffixDB = []
        _suffixDB = []

        #for alpha in a_p:                              #in practice not different from iterating over frequent items
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
                            #print 'seq for suffix creation: ', seq
                            i = seq.index(k)
                            itemNotFound = False
                            if len(seq[i + 1:]) > 0:                            #if the subsequence in which the frequent item
                                residual = ['_']+seq[i + 1:]                    #is resident has more items after the frequent
                                #print 'residual: ', residual                    #item, then append the residual to the projected
                                projectedDB.append(residual)                    #database. If not, ignore the sequence. (i.e. no else clause)
                        except:
                            #print 'no match in subsequence, moving on to next subsequence'
                            continue
                    else:
                        #print 'projectedDB before: ', projectedDB
                        projectedDB.append(seq)
                        #print 'projectedDB after: ', projectedDB
                if not not projectedDB:
                    DB.append(projectedDB)
            if not not DB:#projectedDB:#DB:
                suffixDB.append(DB)#projectedDB])

        for k, v in _freq.items():
            DB = []
            for song in S:
                projectedDB = []
                itemNotFound = True
                for num, seq in enumerate(song):
                    if itemNotFound and len(seq) > 1:
                        try:
                            #print 'seq for suffix creation: ', seq
                            #print 'k: ', k
                            i = seq.index(k)
                            print 'found k at index (k,i): ', k, i
                            print 'a is: ', a
                            if num == 0 and i != 0:             #Only if we are in the first sequence and the first item
                                itemNotFound = False            #in that sequence is not the key item is the item truly found (i.e. the correct assembly item)
                            if itemNotFound == False and len(seq[i + 1:]) > 0:                            #if the subsequence in which the frequent item
                                #itemNotFound = False
                                residual = ['_']+seq[i + 1:]                    #is resident has more items after the frequent
                                #print '_residual: ', residual                    #item, then append the residual to the projected
                                projectedDB.append(residual)                    #database. If not, ignore the sequence. (i.e. no else clause)
                        except:
                            #print 'no match in subsequence, moving on to next subsequence'
                            continue
                    elif itemNotFound == False:
                        #continue
                        #print 'projectedDB before: ', projectedDB
                        projectedDB.append(seq)
                        #print 'projectedDB after: ', projectedDB
                if not not projectedDB:
                    DB.append(projectedDB)
            if not not DB:#projectedDB:#DB:
                _suffixDB.append(DB)#projectedDB])

        '''
        The new alpha projected database are passed in recursive calls to the
        prefixspan method along with the new prefix of length l+1.
        '''

        print 'suffix: ', suffixDB
        print '_suffix: ', _suffixDB
        [self.prefixspan(alpha, l+1, S_a) for (alpha, S_a) in zip(a_p, suffixDB)]
        [self.prefixspan(alpha, l+1, S_a) for (alpha, S_a) in zip(_a_p, _suffixDB)]
if __name__ == "__main__":
    main()