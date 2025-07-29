import streamlit as st
import pandas as pd
from streamlit_molstar.auto import st_molstar_auto
from typing import Any, List
from Bio.PDB import (
    PDBParser,
    MMCIFIO,
    MMCIFParser,
    PDBIO,
    FastMMCIFParser,
    Atom,
    Model,
    Chain,
    Residue,
    Structure,
    PDBParser,
)


def update_bar_plot(fig: Any) -> Any:
    params_axes = dict(
        showgrid=True,
        gridcolor="#d6d6d6",
        linecolor="black",
        zeroline=False,
        linewidth=1,
        showline=True,
        mirror=True,
        gridwidth=1,
        griddash="dot",
    )
    fig.update_xaxes(**params_axes)
    fig.update_yaxes(**params_axes)
    fig.update_layout(dict(plot_bgcolor="white"), margin=dict(l=0, r=5, b=0, t=20))
    fig.update_layout(
        font=dict(
            family="Computer Modern",
            size=26,
        )
    )
    fig.update_layout(
        legend=dict(
            orientation="h",
            bgcolor="#f3f3f3",
            bordercolor="black",
            borderwidth=1,
            x=-0.12,
            y=-0.25,
        ),
    )
    return fig


def save_to_file(bytes_data, out_path):
    with open(out_path, "wb") as f:
        f.write(bytes_data)


def viz_structure(in_path: str, key="aligned_structure"):
    st.write("---")
    st.write("## Aligned structures")
    st.write("Aligned structures using US-Align.")
    st_molstar_auto([in_path], key=key)


def read_file(file_path):
    with open(file_path, "r") as f:
        return f.read()


def convert_cif_to_pdb(in_cif: str, out_pdb: str):
    """
    Convert a .cif file to a .pdb file, handling multiple chains and chain ID limits.
    :param in_cif: Path to the input .cif file
    :param out_pdb: Path to save the output .pdb file
    """
    try:
        parser = MMCIFParser(QUIET=True)
        structure = parser.get_structure("my_structure", in_cif)
        used_chain_ids = set()
        remap_chain_ids = {}
        # Handle chain IDs
        for model in structure:
            for chain in model:
                original_id = chain.id
                if len(original_id) > 1 or original_id in used_chain_ids:
                    # Generate a new chain ID
                    for new_id in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789":
                        if new_id not in used_chain_ids:
                            remap_chain_ids[original_id] = new_id
                            chain.id = new_id
                            used_chain_ids.add(new_id)
                            break
                    else:
                        raise ValueError("Too many chains to fit in PDB format!")
                else:
                    used_chain_ids.add(original_id)
        io = PDBIO()
        io.set_structure(structure)
        io.save(out_pdb)
    except Exception as e:
        print(f"Error during conversion: {e}")


def save_mcq_per_seq(sequences: List, mcq_per_seq: List, names: List, out_path: str):
    """
    Save the MCQ per seq into a dataframe
    """
    out = {name: mcq for name, mcq in zip(names, mcq_per_seq)}
    df = pd.DataFrame({"Sequence": list(sequences[0][:-2]), **out})
    df.to_csv(out_path, index=False)
