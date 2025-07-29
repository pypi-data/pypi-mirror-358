from typing import List, Tuple
import os
import pandas as pd
import time

from rnadvisor2_webserver.tb_helper.extractor.extractor_helper import ExtractorHelper
from rnadvisor2_webserver.tb_helper.metrics.mcq import MCQ
from rnadvisor2_webserver.tb_helper.rna_torsionbert_helper import RNATorsionBERTHelper


class TBMCQ:
    def compute_tb_mcq(self, in_pdb: str) -> float:
        """
        Compute the TB-MCQ scoring function from a .pdb file
        It computes the angles with a custom Python script, and compute the MAE with the angles
            predictions from RNA-Torsion-BERT
        :param in_pdb: path to a .pdb file
        :return: the TB-MCQ score
        """
        experimental_angles = ExtractorHelper().extract_all(in_pdb)
        sequence = "".join(experimental_angles["sequence"].values)
        torsionBERT_helper = RNATorsionBERTHelper()
        torsionBERT_output = torsionBERT_helper.predict(sequence)
        mcq = MCQ().compute_mcq(experimental_angles, torsionBERT_output)
        return mcq

    @staticmethod
    def compute_tb_mcq_per_sequence(in_pdb: str) -> Tuple[str, List[float]]:
        """
        Compute the TB-MCQ scoring function from a .pdb file per sequence
        :param in_pdb: path to a .pdb file
        :return: the sequence and the TB-MCQ score per sequence
        """
        experimental_angles = ExtractorHelper().extract_all(in_pdb)
        sequence = "".join(experimental_angles["sequence"].values)
        torsionBERT_helper = RNATorsionBERTHelper()
        torsionBERT_output = torsionBERT_helper.predict(sequence)
        mcq_per_seq = MCQ().compute_mcq_per_sequence(
            experimental_angles, torsionBERT_output
        )
        return sequence, mcq_per_seq

    @staticmethod
    def compute_tb_mcq_per_sequences(list_pdbs: List[str]):
        """
        Compute the TB-MCQ per sequence for the list of PDB files.
        """
        out_seq, out_mcq = [], []
        for in_pdb in list_pdbs:
            seq, mcq_per_seq = TBMCQ.compute_tb_mcq_per_sequence(in_pdb)
            out_seq.append(seq)
            out_mcq.append(mcq_per_seq)
        return out_seq, out_mcq

    @staticmethod
    def extract_angles_sequences(all_pdbs: List[str]) -> Tuple[List, List]:
        """
        Extract the angles and sequences from a list of PDBs
        """
        all_angles, all_sequences = [], []
        for in_pdb in all_pdbs:
            experimental_angles = ExtractorHelper().extract_all(in_pdb)
            sequence = "".join(experimental_angles["sequence"].values)
            all_angles.append(experimental_angles)
            all_sequences.append(sequence)
        return all_angles, all_sequences

    @staticmethod
    def get_tb_mcq_all(list_pdbs: List[str]):
        """
        Return the TB MCQ per position and per angle
        :return:
        """
        start_time = time.time()
        out_seq, out_mcq_per_pos, out_mcq_per_angle = [], [], {}
        out_mcq_per_pos_pt = []
        all_tb_mcqs, all_tb_times = {}, {}
        torsionBERT_helper = RNATorsionBERTHelper()
        mcq_helper = MCQ()
        all_angles, all_sequences = TBMCQ.extract_angles_sequences(list_pdbs)
        pred_angles = torsionBERT_helper.predict_batch(all_sequences)
        pred_time = (time.time() - start_time) / len(list_pdbs)
        for in_pdb, exp_angle, seq, pred_angle in zip(
            list_pdbs, all_angles, all_sequences, pred_angles
        ):
            start_time = time.time()
            mcq_per_seq = mcq_helper.compute_mcq_per_sequence(exp_angle, pred_angle)
            mcq_per_seq_pt = mcq_helper.compute_mcq_per_sequence(
                exp_angle, pred_angle, torsion="PSEUDO"
            )
            mcq_per_angle = mcq_helper.compute_mcq_per_angle(exp_angle, pred_angle)
            mcq_per_angle_pt = mcq_helper.compute_mcq_per_angle(
                exp_angle, pred_angle, torsion="PSEUDO"
            )
            all_mcq = mcq_helper.compute_mcq(exp_angle, pred_angle)
            c_time = time.time() - start_time + pred_time
            all_tb_times[os.path.basename(in_pdb)] = c_time
            all_tb_mcqs[os.path.basename(in_pdb)] = all_mcq
            out_seq.append(seq)
            out_mcq_per_pos.append(mcq_per_seq)
            out_mcq_per_pos_pt.append(mcq_per_seq_pt)
            for angle, value in {**mcq_per_angle, **mcq_per_angle_pt}.items():
                out_mcq_per_angle[angle] = out_mcq_per_angle.get(angle, []) + [value]
        names = [os.path.basename(name) for name in list_pdbs]
        seq = list(seq[:-2])
        out = {name: mcq[: len(seq)] for name, mcq in zip(names, out_mcq_per_pos)}
        df = pd.DataFrame({"Sequence": seq, **out})
        df_angle = pd.DataFrame(out_mcq_per_angle, index=names)
        return df, df_angle, all_tb_mcqs, all_tb_times