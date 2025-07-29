from Bio.Seq import Seq

dna_sequence = Seq("ATGCTAGCTAGCTAGCTG")

sliced_sequence = dna_sequence[3:11]
print("Sliced Sequence:", sliced_sequence)

another_sequence = Seq("GGCTAG")
concatenated_sequence = sliced_sequence + another_sequence 
print("Concatenated Sequence:", concatenated_sequence)

rna_sequence = concatenated_sequence.transcribe() 
print("RNA Sequence:", rna_sequence)
 
protein_sequence = rna_sequence.translate()
print("Protein Sequence:", protein_sequence)
