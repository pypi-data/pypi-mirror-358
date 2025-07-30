# Biopythonn

This is a Python library named `biopythonn` for biological data operations.

## Installation


































from Bio import PDB
import os

# Step 1: Define PDB ID and fetch the structure from RCSB PDB
pdb_id = "1TUP"  # Example: Human p53 DNA-binding domain
pdb_filename = f"{pdb_id}.pdb"

# Use PDBList to download the structure if not already present
pdbl = PDB.PDBList()
pdbl.retrieve_pdb_file(pdb_id, pdir=".", file_format="pdb")

# Step 2: Parse the downloaded PDB file
parser = PDB.PDBParser(QUIET=True)
structure = parser.get_structure("protein", f"pdb{pdb_id.lower()}.ent")  # Bio.PDB saves as 'pdbXXXX.ent'

# Step 3: Access model and chain
model = structure[0]          # First model
chain = model['A']            # Select chain A

# Step 4: Print info about the selected chain
print(f"\nResidues in Chain {chain.id}:")
for residue in chain:
    print(residue)

# Step 5: Save to a new PDB file for visualization in PyMOL, Chimera, etc.
io = PDB.PDBIO()
io.set_structure(chain)       # You can save full structure or just a chain
io.save("selected_chain_A.pdb")

print("\nSaved chain A to 'selected_chain_A.pdb' for 3D visualization.")


from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio import SeqIO

# Step 1: Create a DNA sequence
dna_sequence = Seq("ATGCGTACGTAGCTAGCTAG")

# Step 2: Create a SeqRecord object with metadata and annotations
record = SeqRecord(
    dna_sequence,
    id="SEQ001",                        # Must be <= 10 characters for GenBank
    name="ExampleGene",                # Gene name
    description="Example gene sequence",
    annotations={
        "molecule_type": "DNA"         # Required for GenBank format
    }
)

# Optional: add features or custom annotations as comments
record.annotations["comment"] = "Function: Hypothetical protein"

# Step 3: Write the record to a GenBank file
output_file_path = "C:/Users/Admin/Downloads/q4_genbank.gb"
with open(output_file_path, "w") as output_file:
    SeqIO.write(record, output_file, "genbank")
print("GenBank file written successfully.")

# Step 4: Read and print the contents of the GenBank file
with open(output_file_path, "r") as input_file:
    record_read = SeqIO.read(input_file, "genbank")
    print("\nContents of the GenBank file:")
    print(record_read)





#Output is a q4_genbank.gb file



from Bio import SeqIO
from Bio.SeqRecord import SeqRecord

# Function to convert a FASTA file to GenBank format
def convert_fasta_to_genbank(fasta_file, genbank_file):
    # List to hold GenBank records
    records = []

    # Parse the FASTA file
    for record in SeqIO.parse(fasta_file, "fasta"):
        # Create a new SeqRecord with GenBank-required annotations
        genbank_record = SeqRecord(
            record.seq,
            id=record.id[:10],  # GenBank requires ID to be ≤10 characters
            name="ExampleGene",
            description=record.description,
            annotations={
                "molecule_type": "DNA"  # Required field
            }
        )
        # Optional: add a comment field for gene/function info
        genbank_record.annotations["comment"] = "Gene: ExampleGene | Function: Hypothetical protein"
        
        # Append to the list of records
        records.append(genbank_record)

    # Write all records to GenBank format
    with open(genbank_file, "w") as output_handle:
        SeqIO.write(records, output_handle, "genbank")

    print(f"All FASTA sequences converted to GenBank format and saved as '{genbank_file}'")

# File paths (replace with actual ones if needed)
fasta_file = "C:/Users/Admin/Downloads/fasta_1.fasta"
genbank_file = "C:/Users/Admin/Downloads/example_output.gb"

# Call the function
convert_fasta_to_genbank(fasta_file, genbank_file)



from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.SeqFeature import SeqFeature, FeatureLocation

# Step 1: Create a DNA sequence
dna_sequence = Seq("ATGCGTACGTAGCTAGCTAG")

# Step 2: Create a SeqRecord object with basic info
record = SeqRecord(
    dna_sequence,
    id="seq1",
    name="Example_Gene",
    description="An example DNA sequence for gene annotation.",
)

# Step 3: Add annotations
record.annotations["gene"] = "ExampleGene"
record.annotations["function"] = "Hypothetical protein"
record.annotations["organism"] = "Synthetic organism"

# Step 4: Add a feature for the gene (with start and end positions)
gene_feature = SeqFeature(
    FeatureLocation(0, len(dna_sequence)),  # 0-based indexing, end is exclusive
    type="gene",
    qualifiers={"gene": "ExampleGene", "note": "Example gene feature"}
)
record.features.append(gene_feature)

# Step 5: Modify one of the annotations
record.annotations["function"] = "Hypothetical protein with modified function"

# Step 6: Print the updated SeqRecord
print(f"ID: {record.id}")
print(f"Name: {record.name}")
print(f"Description: {record.description}")
print("\nAnnotations:")
for key, value in record.annotations.items():
    print(f"  {key}: {value}")

print("\nFeatures:")
for feature in record.features:
    print(f"  Type: {feature.type}")
    print(f"  Location: {feature.location}")
    print(f"  Qualifiers: {feature.qualifiers}")


from Bio import Entrez, SeqIO

# Step 1: Provide your email (required by NCBI)
Entrez.email = "your_email@example.com"  # Replace with your actual email

# Step 2: Accession number of the sequence
accession_number = "NM_001301717"  # Example: Human gene

# Step 3: Fetch GenBank record using Entrez
with Entrez.efetch(db="nucleotide", id=accession_number, rettype="gb", retmode="text") as handle:
    seq_record = SeqIO.read(handle, "genbank")

# Step 4: Print sequence and metadata
print(f"Accession Number: {seq_record.id}")
print(f"Description: {seq_record.description}")
print(f"Organism: {seq_record.annotations.get('organism', 'Not available')}")
print(f"Sequence (first 100 bases): {seq_record.seq[:100]}...")  # Print only first 100 bases
print(f"Length of Sequence: {len(seq_record.seq)}")
print(f"Number of Features: {len(seq_record.features)}")

# Optional: Print top-level features (like CDS, gene, etc.)
print("\nTop Features:")
for feature in seq_record.features[:5]:  # Show only first 5 features
    print(f"  Type: {feature.type}, Location: {feature.location}")


from Bio import pairwise2
from Bio.pairwise2 import format_alignment

# Define two DNA sequences
seq1 = "AGTACACTGGT"
seq2 = "AGTACGCTGGT"

# Perform global alignment
alignments = pairwise2.align.globalxx(seq1, seq2)  # 'xx' = match = 1, mismatch = 0

# Print the best alignment and score
print("Aligned Sequences:")
print(format_alignment(*alignments[0]))


# ✅ Steps to Perform MSA with MUSCLE in Biopython

#     Install MUSCLE separately:
#     Download from: https://www.drive5.com/muscle/
#     Add it to your system PATH or provide the full path in the script.

#     Save input sequences to a FASTA file.

#     Call MUSCLE using MuscleCommandline from Biopython.

#     Read the aligned output using AlignIO.

from Bio import AlignIO
from Bio.Align.Applications import MuscleCommandline

# Step 1: Define three DNA sequences in FASTA format
seq1 = """>seq1
ATGCGTACGTA
"""
seq2 = """>seq2
ATGCGTACGTC
"""
seq3 = """>seq3
ATGCGTACGAG
"""

# Step 2: Write sequences to input FASTA file
with open("input_sequences.fasta", "w") as f:
    f.write(seq1)
    f.write(seq2)
    f.write(seq3)

# Step 3: Set path to MUSCLE executable
# If MUSCLE is in PATH, just use "muscle"
# Otherwise, provide full path e.g. "C:/Users/Anurag/muscle.exe"
muscle_exe = "muscle"

# Step 4: Set up MUSCLE command line
muscle_cline = MuscleCommandline(
    cmd=muscle_exe,
    input="input_sequences.fasta",
    out="aligned_sequences.fasta"
)

# Step 5: Run MUSCLE
stdout, stderr = muscle_cline()

# Step 6: Read and print the alignment
alignment = AlignIO.read("aligned_sequences.fasta", "fasta")
print("\nAligned Sequences:")
print(alignment)


from Bio import AlignIO, Phylo
from Bio.Phylo.TreeConstruction import DistanceCalculator, DistanceTreeConstructor

# Step 1: Load the aligned sequences (in CLUSTAL or FASTA format)
alignment = AlignIO.read("aligned_sequences.fasta", "fasta")  # or "clustal" if using .aln

# Step 2: Calculate the distance matrix
calculator = DistanceCalculator("identity")  # You can also use "blastn", "trans", etc.
distance_matrix = calculator.get_distance(alignment)

# Step 3: Construct the phylogenetic tree using UPGMA or NJ
constructor = DistanceTreeConstructor()
tree = constructor.upgma(distance_matrix)
# tree = constructor.nj(distance_matrix)  # Alternatively use neighbor-joining

# Step 4: Visualize the tree
Phylo.draw(tree)



from Bio import PDB
import os

# Step 1: Define PDB ID and fetch the structure from RCSB PDB
pdb_id = "1TUP"  # Example: Human p53 DNA-binding domain
pdb_filename = f"{pdb_id}.pdb"

# Use PDBList to download the structure if not already present
pdbl = PDB.PDBList()
pdbl.retrieve_pdb_file(pdb_id, pdir=".", file_format="pdb")

# Step 2: Parse the downloaded PDB file
parser = PDB.PDBParser(QUIET=True)
structure = parser.get_structure("protein", f"pdb{pdb_id.lower()}.ent")  # Bio.PDB saves as 'pdbXXXX.ent'

# Step 3: Access model and chain
model = structure[0]          # First model
chain = model['A']            # Select chain A

# Step 4: Print info about the selected chain
print(f"\nResidues in Chain {chain.id}:")
for residue in chain:
    print(residue)

# Step 5: Save to a new PDB file for visualization in PyMOL, Chimera, etc.
io = PDB.PDBIO()
io.set_structure(chain)       # You can save full structure or just a chain
io.save("selected_chain_A.pdb")

print("\nSaved chain A to 'selected_chain_A.pdb' for 3D visualization.")
