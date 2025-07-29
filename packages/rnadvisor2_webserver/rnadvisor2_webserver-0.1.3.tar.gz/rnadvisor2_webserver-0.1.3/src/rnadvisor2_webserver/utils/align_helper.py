import os
from importlib.resources import files
import subprocess
from typing import List
from Bio import PDB
from Bio.PDB import PDBIO


PREFIX_IMG = files("rnadvisor2_webserver.bin").joinpath("USalign")
COMMAND = f"{PREFIX_IMG} -mol RNA $PRED $REF -o tmp/struct1"


def align_structures(reference_struct: str, prediction_structs: List[str], out_path: str):
    """
    Align multiple predicted structures to the reference structure, adding each prediction as a new chain.
    """
    if not all(struct.endswith(".pdb") for struct in [reference_struct] + prediction_structs):
        raise ValueError("All input files must be in .pdb format")

    os.makedirs("tmp", exist_ok=True)

    parser = PDB.PDBParser(QUIET=True)
    pdb1 = parser.get_structure("reference", reference_struct)

    reference_chains = list(pdb1.get_chains())
    if len(reference_chains) != 1:
        raise ValueError("Reference structure must contain exactly one chain.")
    reference_chains[0].id = "A"

    for prediction_struct in prediction_structs:
        command = COMMAND.replace("$REF", reference_struct).replace("$PRED", prediction_struct)
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            stdout = result.stdout
            # Check if alignment failed (e.g., RMSD not reported or RMSD == 0)
            if "RMSD=" not in stdout or "Aligned length=0" in stdout:
                print(f"⚠️ USalign failed or gave bad alignment for: {prediction_struct}")
                continue

        except subprocess.CalledProcessError as e:
            print(f"❌ Error running USalign for {prediction_struct}: {e}")
            continue
        try:
            add_aligned_chain(pdb1, "tmp/struct1.pdb")
        except Exception as e:
            print(f"❌ Error merging aligned structure {prediction_struct}: {e}")
            continue
        os.remove("tmp/struct1.pdb")

    io = PDBIO()
    io.set_structure(pdb1)
    io.save(out_path)

    for fname in os.listdir("tmp"):
        if fname.endswith(".pml"):
            os.remove(os.path.join("tmp", fname))



def get_next_chain_id(used_ids: List[str]) -> str:
    """
    Return the next available single-letter chain ID.
    """
    for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        if c not in used_ids:
            return c
    raise ValueError("Too many chains! Ran out of chain IDs.")


def add_aligned_chain(reference_structure, aligned_struct_path: str):
    """
    Add the aligned structure (from tmp/struct1.pdb) as a new chain in the reference_structure.
    """
    parser = PDB.PDBParser(QUIET=True)
    aligned_struct = parser.get_structure("aligned", aligned_struct_path)
    aligned_chains = list(aligned_struct.get_chains())

    if not aligned_chains:
        raise ValueError("No chains found in aligned structure.")

    used_ids = [chain.id for chain in reference_structure[0].get_chains()]
    new_id = get_next_chain_id(used_ids)

    # Assume single chain (or take first if multiple)
    new_chain = aligned_chains[0]
    new_chain.id = new_id
    new_chain.detach_parent()
    reference_structure[0].add(new_chain)