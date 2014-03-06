#!/usr/bin/python
# -*- coding: utf-8 -*-
import numpy as np


# http://en.wikipedia.org/wiki/Category:String_similarity_measures

class Entropy(object):

    """ duplicate bigrams in a word should be counted distinctly
    (per discussion), otherwise 'AA' and 'AAAA' would have a
    dice coefficient of 1...
    """

    def dice_coefficient(self, a, b):
        if not len(a) or not len(b):
            return 0.0
        if a == b:
            return 1.
        if len(a) == 1 or len(b) == 1:
            return 0.0

        a_bigram_list = [a[i:i + 2] for i in range(len(a) - 1)]
        b_bigram_list = [b[i:i + 2] for i in range(len(b) - 1)]

        a_bigram_list.sort()
        b_bigram_list.sort()

        # assignments to save function calls

        lena = len(a_bigram_list)
        lenb = len(b_bigram_list)

        # initialize match counters

        matches = i = j = 0
        while i < lena and j < lenb:
            if a_bigram_list[i] == b_bigram_list[j]:
                matches += 2
                i += 1
                j += 1
            elif a_bigram_list[i] < b_bigram_list[j]:
                i += 1
            else:
                j += 1

        score = float(matches) / float(lena + lenb)
        return score

    def compute_jaccard_index(self, s1, s2):
        set_1 = set(s1)
        set_2 = set(s2)
        n = len(set_1.intersection(set_2))
        return n / float(len(set_1) + len(set_2) - n)

    def winklerCompareP(self, str1, str2):
        """Return approximate string comparator measure (between 0.0 and 1.0)

      USAGE:
        score = winkler(str1, str2)

      ARGUMENTS:
        str1  The first string
        str2  The second string

      DESCRIPTION:
        As described in 'An Application of the Fellegi-Sunter Model of
        Record Linkage to the 1990 U.S. Decennial Census' by William E. Winkler
        and Yves Thibaudeau.

        Based on the 'jaro' string comparator, but modifies it according to whether
        the first few characters are the same or not.
      """

      # Quick check if the strings are the same - - - - - - - - - - - - - - - - - -
      #

        jaro_winkler_marker_char = chr(1)
        if str1 == str2:
            return 1.

        len1 = len(str1)
        len2 = len(str2)
        halflen = max(len1, len2) / 2 - 1

        ass1 = ''  # Characters assigned in str1
        ass2 = ''  # Characters assigned in str2

      # ass1 = ''
      # ass2 = ''

        workstr1 = str1
        workstr2 = str2

        common1 = 0  # Number of common characters
        common2 = 0

      # print "'len1', str1[i], start, end, index, ass1, workstr2, common1"
      # Analyse the first string    - - - - - - - - - - - - - - - - - - - - - - - - -
      #

        for i in range(len1):
            start = max(0, i - halflen)
            end = min(i + halflen + 1, len2)
            index = workstr2.find(str1[i], start, end)

          # print 'len1', str1[i], start, end, index, ass1, workstr2, common1

            if index > -1:  # Found common character
                common1 += 1

              # ass1 += str1[i]

                ass1 = ass1 + str1[i]
                workstr2 = workstr2[:index] + jaro_winkler_marker_char \
                    + workstr2[index + 1:]

      # print "str1 analyse result", ass1, common1

      # print "str1 analyse result", ass1, common1
      # Analyse the second string - - - - - - - - - - - - - - - - - - - - - - - - -
      #

        for i in range(len2):
            start = max(0, i - halflen)
            end = min(i + halflen + 1, len1)
            index = workstr1.find(str2[i], start, end)

          # print 'len2', str2[i], start, end, index, ass1, workstr1, common2

            if index > -1:  # Found common character
                common2 += 1

              # ass2 += str2[i]

                ass2 = ass2 + str2[i]
                workstr1 = workstr1[:index] + jaro_winkler_marker_char \
                    + workstr1[index + 1:]

        if common1 != common2:
            print 'Winkler: Wrong common values for strings "%s" and "%s"' \
                % (str1, str2) + ', common1: %i, common2: %i' \
                % (common1, common2) + ', common should be the same.'
            common1 = float(common1 + common2) / 2.0  # #### This is just a fix #####

        if common1 == 0:
            return 0.0

      # Compute number of transpositions    - - - - - - - - - - - - - - - - - - - - -
      #

        transposition = 0
        for i in range(len(ass1)):
            if ass1[i] != ass2[i]:
                transposition += 1
        transposition = transposition / 2.0

      # Now compute how many characters are common at beginning - - - - - - - - - -
      #

        minlen = min(len1, len2)
        for same in range(minlen + 1):
            if str1[:same] != str2[:same]:
                break
        same -= 1
        if same > 4:
            same = 4

        common1 = float(common1)
        w = 1. / 3. * (common1 / float(len1) + common1 / float(len2)
                       + (common1 - transposition) / common1)

        wn = w + same * 0.1 * (1. - w)
        return wn

    def getAllEntropies(self, one, two):
        """ one and two are the two states to compare in number array form. """

        if type(one) != type(''):
            convertOne = ''.join(chr(val) for val in one)
        else:
            convertOne = one
        if type(two) != type(''):
            convertTwo = ''.join(chr(val) for val in two)
        else:
            convertTwo = two
        result = [
            'dice_coefficient (1) ',
            str(self.dice_coefficient(convertOne, convertTwo)),
            '\nlevenshtein (0) ',
            str(self.levenshtein(convertOne, convertTwo)),
            '\ndameraulevenshtein (0) ',
            str(self.dameraulevenshtein(convertOne, convertTwo)),
            '\ncompute_jaccard_index closer (1)  ',
            str(self.compute_jaccard_index(one, two)),
            '\nwinklerCompareP (1)  ',
            str(self.winklerCompareP(convertOne, convertTwo)),
            ]
        out = ''
        for x in range(0, len(result)):
            if x % 2 == 0:
                out = out + result[x] + '    '
            else:
                out = out + result[x] + ''
        return out

    def dameraulevenshtein(self, seq1, seq2):
        """Calculate the Damerau-Levenshtein distance between sequences.

      This distance is the number of additions, deletions, substitutions,
      and transpositions needed to transform the first sequence into the
      second. Although generally used with strings, any sequences of
      comparable objects will work.

      Transpositions are exchanges of *consecutive* characters; all other
      operations are self-explanatory.

      This implementation is O(N*M) time and O(M) space, for N and M the
      lengths of the two sequences.

      >>> dameraulevenshtein('ba', 'abc')
      2
      >>> dameraulevenshtein('fee', 'deed')
      2

      It works with arbitrary sequences too:
      >>> dameraulevenshtein('abcd', ['b', 'a', 'c', 'd', 'e'])
      2
      """

      # codesnippet:D0DE4716-B6E6-4161-9219-2903BF8F547F
      # Conceptually, this is based on a len(seq1) + 1 * len(seq2) + 1 matrix.
      # However, only the current and two previous rows are needed at once,
      # so we only store those.

        oneago = None
        thisrow = range(1, len(seq2) + 1) + [0]
        for x in xrange(len(seq1)):

          # Python lists wrap around for negative indices, so put the
          # leftmost column at the *end* of the list. This matches with
          # the zero-indexed strings and saves extra calculation.

            (twoago, oneago, thisrow) = (oneago, thisrow, [0]
                    * len(seq2) + [x + 1])
            for y in xrange(len(seq2)):
                delcost = oneago[y] + 1
                addcost = thisrow[y - 1] + 1
                subcost = oneago[y - 1] + (seq1[x] != seq2[y])
                thisrow[y] = min(delcost, addcost, subcost)

              # This block deals with transpositions

                if x > 0 and y > 0 and seq1[x] == seq2[y - 1] \
                    and seq1[x - 1] == seq2[y] and seq1[x] != seq2[y]:
                    thisrow[y] = min(thisrow[y], twoago[y - 2] + 1)
        return thisrow[len(seq2) - 1]

    def levenshtein(self, source, target):
        if len(source) < len(target):
            return levenshtein(target, source)

        # So now we have len(source) >= len(target).

        if len(target) == 0:
            return len(source)

        # We call tuple() to force strings to be used as sequences
        # ('c', 'a', 't', 's') - numpy uses them as values by default.

        source = np.array(tuple(source))
        target = np.array(tuple(target))

        # We use a dynamic programming algorithm, but with the
        # added optimization that we only need the last two rows
        # of the matrix.

        previous_row = np.arange(target.size + 1)
        for s in source:

            # Insertion (target grows longer than source):

            current_row = previous_row + 1

            # Substitution or matching:
            # Target and source items are aligned, and either
            # are different (cost of 1), or are the same (cost of 0).

            current_row[1:] = np.minimum(current_row[1:],
                    np.add(previous_row[:-1], target != s))

            # Deletion (target grows shorter than source):

            current_row[1:] = np.minimum(current_row[1:],
                    current_row[0:-1] + 1)

            previous_row = current_row

        return previous_row[-1]



      