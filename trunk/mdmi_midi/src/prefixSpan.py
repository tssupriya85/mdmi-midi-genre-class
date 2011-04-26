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
        if not S:
            return a                                            #base case for recursion
        freq = {}
        for songs in S:
            tabu = []
            tabu_as = []
            for seq in songs:
                for item in seq:                                #take open projected sequences into account!!!!!
                    if len(seq[seq.index(item):]) > 1:
                        if str(item) + '_' not in freq:
                            freq[str(item) + '_'] = 1
                            tabu.append(str(item) + '_')
                        elif str(item) + '_' in tabu:
                            continue
                        else:
                            freq[str(item) + '_'] += 1
                            tabu.append(str(item) + '_')
                    if item not in freq:                        #items in general
                        freq[item] = 1
                        tabu.append(item)
                    elif item in tabu:       #tabu is used to ensure that only the first item in each sequence is taken into account
                        continue
                    else:
                        freq[item] += 1
                        tabu.append(item)

        for k, v in freq.items():
            if v < self.supp:
                #print 'Deleting k, v from freq: ' + str(k) + ', ' + str(v)
                del freq[k]                                     #array is iterated and frequent distinct length-1 sequential patterns are found
        #print 'FREQUENT ITEMS ' + str(freq)
        '''
        All frequent items are appended to the prefix sequence alpha' (a_p) to
        be used for later generation of frequent sequences of length l+1.
        Furthermore frequent sequences of length l are appended to the set of
        all frequent sequences (seq_pats)
        '''
        if l == 0:
            a_p = [a + [k] for k, v in freq.items()]            #concatenate a with frequent items to generate new frequent sequential patterns of length 1
            #print 'a_p - 0: ' + str(a_p)
            freq2 = [([k], v) for k, v in freq.items()]
            #print 'freq2 - 0: ' + str(freq2)
        else:
            freq2 = []
            a_p = []
            for prefix in a:
                if len(prefix) == l:
                    for k,v in freq.items():
                        print 'k: ' + str(k)
                        if str(k).startswith('_') == True:                                  #The item can be assembled with
                            if str(prefix[len(prefix)-1]).endswith('_') == True:
                                print 'prefix[l-1:l] ' + str(prefix[l-1:l])#[0])[:-1]
                                temp = [int(str(prefix[l-1:l][0])[:-1])] + [int(k[1:])]     #Remove _ from '_k' and from 'prefix_'
                            else:
                                temp = prefix[l-1:] + [int(k[1:])]                          #Remove _ only from '_k'
                            print 'popping from prefix: ' + str(prefix.pop(l-1))
                            print 'appending to prefix: ' + str(temp)
                            prefix.append(temp)
                            temp2 = (temp, v)
                            freq2.append(temp2)
                        elif str(k).endswith('_') == True:
                            if str(prefix[len(prefix)-1]).endswith('_') == True:
                                print prefix
                                print 'prefix[l-1:l] ' + str(prefix[l-1:l])#[0])[:-1]
                                temp = [int(str(prefix[l-1:l][0])[:-1])] + [k]#[int(k[1:])]# : v
                                print 'popping from prefix: ' + str(prefix.pop(l-1))
                                print 'appending to prefix: ' + str(temp)
                                prefix.append(temp)
                                temp2 = (temp, v)
                            else:
                                #temp = prefix + [k]
                                temp = k
                                prefix.append(temp)
                                temp2 = (prefix, v)
                            freq2.append(temp2)
                        else:
                            #temp = prefix + [k]
                            temp = k
                            print 'appending to prefix: ' + str(temp)
                            prefix.append(temp)#temp)
                            temp2 = (prefix, v)
                            freq2.append(temp2)
                        a_p.append(temp)
                    print 'new partitioned prefixes (alpha prime sequences): ' + str(a_p)
            if not not freq2:                                       #as long as freq2 is not empty, append it to the overall list of frequent sequences
                [self.seq_pats.append(pattern) for pattern in freq2]
        '''
        The new projected database (suffix) are generated. Here the currently
        alpha projected db are reduced to contain only items subsequent to the
        current frequent item, thus iteratively reducing the size of the alpha
        projected db.
        '''
        suffix = []
        for k, v in freq.items():
            a_proj = []
            for song in S:
                s = []
                b = True
                for seq in song:
                    if b:
                        try:
                            i = seq.index(k)
                            b = False
                            #print 'k,i: ' + str(k) + ', ' + str(i)
                        except:
                            #print 'exception'
                            if str(k).endswith('_'):
                                try:
                                    #print 'trying'
                                    i = seq.index(int(k[:len(k)-1]))
                                    if len(seq[i + 1:]) > 0:
                                        j = seq[i + 1:]
                                        j[0] = '_'+str(j[0])
                                        s.append(j)
                                except:
                                    #print 'failing'
                                    continue
                            else:
                                continue
                        if len(seq[i + 1:]) > 0:# and song.index(seq) == 0:
                            #print 'seq[i + 1:] ' + str(seq[i + 1:])
                            j = seq[i + 1:]
                            j[0] = '_'+str(j[0])
                            s.append(j)                    #append all  items after i to temp
                        else:
                            pass#print ' single item sequence: ' + str(seq)
                    else:
                        s.append(seq)
                if not not s:
                    #print 's: ' + str(s)
                    a_proj.append(s)
            if not not a_proj:
                suffix.append(a_proj)
        '''
        The new alpha projected database are passed in recursive calls to the
        prefixspan method along with the new prefix of length l+1.
        '''
        #print 'suffix: ' + str(suffix)
        [self.prefixspan([alpha], l+1, a_proj_db) for (alpha, a_proj_db) in zip(a_p, suffix)]
if __name__ == "__main__":
    main()