from Bio import Entrez

Entrez.email = "jaigupta.is22@bmsce.ac.in"
accession_number = "NM_001301717" 

from Bio import SeqIO

handle = Entrez.efetch(db="nucleotide", id=accession_number, rettype="gb", retmode="text")
seq_record = SeqIO.read(handle, "genbank")

print(f"Accession Number: {seq_record.id}")
print(f"Description: {seq_record.description}")
print(f"Organism: {seq_record.annotations['organism']}")
print(f"Sequence: {seq_record.seq}")
print(f"Length of Sequence: {len(seq_record.seq)}") 
print(f"Features: {seq_record.features}")
