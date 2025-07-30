# Dictionary to store all program texts
program_texts = {
    1: """### **#1: DNA Manipulation and Translation**

```python
from Bio.Seq import Seq
dna_sequence = Seq("ATGCGTACGTAGCTAGCTAGCTAGCTAGCTAGC")  # Define a DNA sequence

sliced_sequence = dna_sequence[3:11]  # Slice DNA from index 3 to 10
print("Sliced Sequence:", sliced_sequence)

another_sequence = Seq("ATGCGTACGTAGCTAGCTAGCTAGCTAGCTAGC")  # Define another DNA sequence
concatenated_sequence = sliced_sequence + another_sequence  # Concatenate both sequences
print("Concatenated Sequence:", concatenated_sequence) 

rna_sequence = concatenated_sequence.transcribe()  # Transcribe DNA to RNA
print("RNA Sequence:", rna_sequence)

protein_sequence = rna_sequence.translate()  # Translate RNA to Protein
print("Protein Sequence:", protein_sequence)

```""",

    2: """### **#2: Reading a FASTA File**

```python
from Bio import SeqIO

def read_fasta(example):
    # Parse and read each sequence from a FASTA file
    for record in SeqIO.parse(example, "fasta"):
        print("Description:", record.description)
        print("Sequence:", record.seq)
        print()

fasta_file = "example.fasta"  # FASTA file path
read_fasta(fasta_file)

```""",

    3: """### **#3: Writing and Reading GenBank Format**

```python
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

# Create a DNA sequence
dna_seq = Seq("AGTCTACGTACCCTAGGCCAAA")

# Create a SeqRecord with annotations
record = SeqRecord(
    dna_seq,
    id="seq1",
    name="Example_gene",
    description="Example gene sequence",
    annotations={
        "molecule_type": "DNA",
        "gene": "Example gene",
        "function": "hypothetical protein"
    }
)

output_file = "example.gb"  # Output GenBank file name

# Open file manually and write the record in GenBank format
ofile = open(output_file, "w")
SeqIO.write(record, ofile, "genbank")
ofile.close()  # Close file manually

print("Written successfully")

# Read the same GenBank file back into a record object
ifile = open(output_file, "r")
record_read = SeqIO.read(ifile, "genbank")
ifile.close()

print(record_read)

```""",

    4: """### **#4: Converting FASTA to GenBank with Annotations**

```python
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord

records = []

# Parse FASTA records and convert to GenBank format
for record in SeqIO.parse("example.fasta", "fasta"):
    new = SeqRecord(
        record.seq,
        id=record.id,
        name="gene",
        description=record.description,
        annotations={
            "molecule_type": "DNA"
        }
    )
    records.append(new)

# Write all records to a GenBank file
file = open("4th_genbank.gb", "w")
SeqIO.write(records, file, "genbank")
file.close()

# Read back GenBank file and print content
file = open("4th_genbank.gb", "r")
for content in SeqIO.parse(file, "genbank"):
    print(content)
file.close()

```""",

    5: """### **#5: Adding Features and Annotations to SeqRecord**

```python
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

# Define a DNA sequence
dna_sequence = Seq("ATGCTAGCATGCATATGC")

# Create SeqRecord with basic info
record = SeqRecord(
    dna_sequence,
    id="seq1",
    name="please",
    description="help",
)

# Add annotations manually
record.annotations["gene"] = "ExampleGene"
record.annotations["function"] = "hypothtectial protein"
record.annotations["organism"] = "Synhtetic protein"

from Bio.SeqFeature import SeqFeature, FeatureLocation

# Add a gene feature covering full sequence
gene_feature = SeqFeature(FeatureLocation(0, 21), type="gene", qualifiers={"gene": "Example gene"})
record.features.append(gene_feature)

# Modify function annotation
record.annotations["function"] = "Hypothetical protein with modified function"

# Print all information
print("ID:", record.id)
print("Name:", record.name)
print("Description:", record.description)
print("Annotation:", record.annotations)
print("Feautures:", record.features)

```""",

    6: """### **#6: Fetching Sequence from NCBI using Entrez**

```python
from Bio import Entrez, SeqIO

Entrez.email = "ayushkumar.is22@bmsce.ac.in"  # Required for NCBI access

# Fetch GenBank data for a specific nucleotide ID
handle = Entrez.efetch(db="nucleotide", id="NM_001301717", rettype="gb", retmode="text")
record = SeqIO.read(handle, "genbank")

# Print details of the record
print("Accession Number:", record.id)
print("Description:", record.description)
print("Organism", record.annotations['organism'])
print("Sequence:", record.seq)
print("Length of sequence", len(record.seq))

```""",

    7: """### **#7: Pairwise Sequence Alignment**

```python
from Bio.Align import PairwiseAligner

# Define two DNA sequences
seq1 = "ATGCGTATAGC"
seq2 = "ATTAGCAGAGC"

# Create a pairwise aligner
aligner = PairwiseAligner()

# Perform pairwise alignment
alignment = aligner.align(seq1, seq2)

# Print aligned sequences and score
print("Aligned Sequences:")
print(alignment[0])
print("Alignment Score:", alignment[0].score)

```""",

    8: """### **#8: Multiple Sequence Alignment using MUSCLE**

```python
import subprocess
from Bio import AlignIO

# Create FASTA file with three sequences
sequences = \">\"\"\">seq1
ATGCGTACGTA
>seq2
ATGCGTACGTC
>seq3
ATGCGTACGAG
\"\"\"

# Save to file
with open(\"input_sequences.fasta\", \"w\") as f:
    f.write(sequences)

# Path to MUSCLE executable
muscle_path = r\"C:\\Users\\ayush\\Downloads\\muscle-win64.v5.3.exe\"

# Command to align using MUSCLE
command = [muscle_path, \"-align\", \"input_sequences.fasta\", \"-output\", \"aligned_sequences.fasta\"]

# Run command using subprocess
result = subprocess.run(command, capture_output=True, text=True)

# Check and print results
if result.returncode != 0:
    print(\"Error running MUSCLE:\")
    print(result.stderr)
else:
    print(\"MUSCLE alignment completed successfully.\")
    alignment = AlignIO.read(\"aligned_sequences.fasta\", \"fasta\")
    print(alignment)

```""",

    9: """### **#9: Constructing Phylogenetic Tree**

```python
from Bio import Phylo, AlignIO
from Bio.Phylo.TreeConstruction import DistanceCalculator, DistanceTreeConstructor

# Read aligned sequences
alignment = AlignIO.read("aligned.fasta", "fasta")

# Calculate distance matrix using identity
dm = DistanceCalculator("identity").get_distance(alignment)

# Construct UPGMA tree
tree = DistanceTreeConstructor().upgma(dm)

# Visualize tree
Phylo.draw(tree)
Phylo.draw_ascii(tree)

# Save tree to file in Newick format
Phylo.write(tree, "tree.newick", "newick")

```""",

    10: """### **#10: PDB 3D Structure Visualization**

```python
from Bio.PDB import *
import matplotlib.pyplot as plt
import numpy as np

pdb_id = "1A3N"  # PDB ID for structure (e.g., Hemoglobin)

# Download mmCIF file for the structure
pdbl = PDBList()
cif_file = pdbl.retrieve_pdb_file(pdb_id, pdir=".", file_format="mmCif")

# Parse the structure from mmCIF file
structure = MMCIFParser().get_structure(pdb_id, cif_file)

# Extract all atom coordinates
atoms = np.array([atom.coord for atom in structure.get_atoms()])

# Plot atoms in 3D space
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(*atoms.T, s=5, alpha=0.5)
ax.set_title(f"{pdb_id} Structure")
plt.tight_layout()
plt.show()
```"""
}

def print_program(program_number):
    """
    Print the text of a specific program.
    
    Args:
        program_number (int): The number of the program to print (1-10)
    """
    if program_number not in program_texts:
        print(f"Error: Program {program_number} not found. Available programs are 1-10.")
        return
    
    print(program_texts[program_number]) 