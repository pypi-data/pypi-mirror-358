from Bio.PDB import PDBList, PDBParser
import matplotlib.pyplot as plt
import numpy as np

pdb_id = "1A3N"
pdbl = PDBList()
pdbl.retrieve_pdb_file("1A3N", pdir=".", file_format="pdb")

parser = PDBParser(QUIET = True)
structure = parser.get_structure("1A3N", "pdb1a3n.ent")

atoms = []
for model in structure:
  for chain in model:
    for residue in chain:
      for atom in residue:
        atoms.append(atom.coord)

atoms = np.array(atoms)

fig = plt.figure(figsize=(8,6))
ax = fig.add_subplot(1, 1, 1, projection="3d")
ax.scatter(atoms[:,0], atoms[:,1], atoms[:,2], c="blue", marker="o", s=10)
ax.set_title(f"3D Structure of {pdb_id}")
ax.set_xlabel("X-axis")
ax.set_ylabel("Y-axis")
ax.set_zlabel("Z-axis")
plt.show()
