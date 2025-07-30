from Bio import Phylo, AlignIO
from Bio.Phylo.TreeConstruction import DistanceCalculator, DistanceTreeConstructor
import matplotlib.pyplot as plt

alignment = AlignIO.read("data/aligned_sequences.aln", "clustal")

calculator = DistanceCalculator("identity")
distance_matrix = calculator.get_distance(alignment)

constructor = DistanceTreeConstructor()
tree = constructor.upgma(distance_matrix)

Phylo.write(tree, "data/phylogenetic_tree.nwk", "newick")

fig = plt.figure(figsize=(8, 5))
ax = fig.add_subplot(1, 1, 1) 
Phylo.draw(tree, axes=ax) 
plt.show()
