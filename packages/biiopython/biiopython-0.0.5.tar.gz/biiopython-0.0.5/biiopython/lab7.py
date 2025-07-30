from Bio.Align import PairwiseAligner

seq1 = "AGTACACTGGT"
seq2 = "AGTACGCTGGT"

aligner = PairwiseAligner()
alignments = aligner.align(seq1, seq2)

print(alignments[0])
print(alignments[0].score)
