#!/usr/bin/env python3
#
# Copyright  2017  Atlas Guide (Author : Lucas Jo)
#
# Apache 2.0
# 
import numpy as np

# Levenshtein Algorithm
def get_distance(s, t):
    prefix_matrix = np.zeros((len(s) + 1, len(t) + 1))
    prefix_matrix[:, 0] = list(range(len(s) + 1))
    prefix_matrix[0, :] = list(range(len(t) + 1))
    for i in range(1, len(s) + 1):
        for j in range(1, len(t) + 1):
            insertion = prefix_matrix[i, j - 1] + 1
            deletion = prefix_matrix[i - 1, j] + 1
            if s[i-1] == t[j-1]:
                match = prefix_matrix[i - 1, j - 1]
            else:
                match = prefix_matrix[i - 1, j - 1] + 2 # substitution
            prefix_matrix[i, j] = min(insertion, deletion, match)
        #print(prefix_matrix)
        #print("")
    i = len(s)
    j = len(t)

    # Return the minimum prefix_matrix using all the table cells
    def backtrace(i, j):
        if i>0 and j>0 and prefix_matrix[i-1][j-1] + 2 == prefix_matrix[i][j]:
            return backtrace(i-1, j-1) + "S"
        if i>0 and prefix_matrix[i-1][j] + 1 == prefix_matrix[i][j]:
            return backtrace(i-1, j) + "D"
        if j>0 and prefix_matrix[i][j-1] + 1 == prefix_matrix[i][j]:
            return backtrace(i, j-1) + "I"
        if i>0 and j>0 and prefix_matrix[i-1][j-1] == prefix_matrix[i][j]:
            return backtrace(i-1, j-1) + "M"
        return ""

    return int(prefix_matrix[i, j]), backtrace(i, j)

def get_alignment(strA, strB, backtrace):
    alignedA = []
    alignedB = []
    idxA = 0
    idxB = 0
    for symbol in backtrace:
        if symbol == 'D':
            alignedA.append(strA[idxA])
            alignedB.append('_')
            idxA += 1
        if symbol in ['M', 'S']:
            alignedA.append(strA[idxA])
            alignedB.append(strB[idxB])
            idxA += 1
            idxB += 1
        if symbol == 'I':
            alignedA.append('_')
            alignedB.append(strB[idxB])
            idxB += 1
    return ''.join(alignedA), ''.join(alignedB)


def main():
    strA = "곡된직선을직선으로질주하는낙체"
    strB = "곡이된직선을직선으로질는낙체"
    distance, backtrace = get_distance(strA, strB)
    alignedA, alignedB  = get_alignment(strA, strB, backtrace)

    print(alignedA)
    print(alignedB)
    print(backtrace)

if __name__ == '__main__':
    main()
