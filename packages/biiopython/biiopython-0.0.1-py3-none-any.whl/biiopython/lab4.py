from Bio import SeqIO
from Bio.SeqRecord import SeqRecord

def convert_fasta_to_genbank(fasta_file, genbank_file):
  records = []

  for record in SeqIO.parse(fasta_file, "fasta"):
  
    sequence = record.seq
    description = record.description
    
    genbank_record = SeqRecord(
      sequence,
      id=record.id,
      name="Example_Gene",
      description=description, 
      annotations={
        "molecule_type": "DNA", 
        "gene": "ExampleGene",
        "function": "Hypothetical protein"
      }
    )

    records.append(genbank_record) 

  with open(genbank_file, "w") as output_handle:
    SeqIO.write(records, output_handle, "genbank")

  print(f"All FASTA sequences converted to GenBank format and saved as {genbank_file}")

fasta_file = "data/fasta_1.fasta"  
genbank_file = "data/example_output.gb" 

convert_fasta_to_genbank(fasta_file, genbank_file)
