from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

dna_sequence = Seq("ATGCGTACGTAGCTAGCTAG")

record = SeqRecord(
  dna_sequence,
  id="seq1",
  name="Example_Gene",
  description="An example DNA sequence for gene annotation.",
)

record.annotations["gene"] = "ExampleGene"
record.annotations["function"] = "Hypothetical protein"
record.annotations["organism"] = "Synthetic organism"

from Bio.SeqFeature import SeqFeature, FeatureLocation

gene_feature = SeqFeature(FeatureLocation(0, 21), type="gene", qualifiers={"gene": "ExampleGene"})
record.features.append(gene_feature)
record.annotations["function"] = "Hypothetical protein with modified function"

print(f"ID: {record.id}")
print(f"Name: {record.name}")
print(f"Description: {record.description}")
print(f"Annotations: {record.annotations}")
print(f"Features: {record.features}")
