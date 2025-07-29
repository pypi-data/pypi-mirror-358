from Bio import SeqIO
 
def read_fasta(file_path):
  for record in SeqIO.parse(file_path, "fasta"):
    print(f"Description: {record.description}") 
    print(f"Sequence: {record.seq}")
    print() 
    
fasta_file = "data/fasta_1.fasta" 
read_fasta(fasta_file)
