from typing import List, Dict, Optional

import streamlit as st
import pandas as pd
import numpy as np

import os

from rnadvisor.rnadvisor_cli import RNAdvisorCLI

from rnadvisor2_webserver.enums.enums import DESC_METRICS, DESC_ENERGY, SUB_SCORING, SUB_METRICS
from rnadvisor2_webserver.tb_helper.tb_mcq import TBMCQ
from rnadvisor2_webserver.utils.utils import convert_cif_to_pdb

os.environ["TOKENIZERS_PARALLELISM"] = "false"

rnadvisor_args = {
    "pred_dir": None,
    "native_path": None,
    "out_path": None,
    "scores": None,
    "out_time_path": None,
}


def compute_metrics(native_path: Optional[str], pred_dir: str,
                    out_path: str, out_time_path: str, tmp_dir: str, params: str,
                    scores: List[str]):
    rnadvisor_cli = RNAdvisorCLI(native_path=native_path, pred_dir=pred_dir, out_path=out_path,
                                 scores=scores, params=params, out_time_path=out_time_path,
                                 sort_by=None, tmp_dir=tmp_dir,
                                 normalise=False)
    rnadvisor_cli.predict()



# @st.cache_data
def run_rnadvisor(
    native_path,
    pred_path,
    out_path,
    metrics,
    scoring_functions,
    time_path,
    log_path,
    hp_params,
    tmp_dir,
    z_sum,
    n_sum
):
    if metrics is None:
        metrics = []
    str_metrics = ",".join(metrics) if len(metrics) > 0 else ""
    to_compute_tb = (
        "TB-MCQ" in scoring_functions if scoring_functions is not None else False
    )
    if scoring_functions is not None:
        scoring_functions = [
            score_fn for score_fn in scoring_functions if score_fn not in metrics
        ]
        str_metrics += "," + ",".join(scoring_functions)
        str_metrics = str_metrics.replace("TB-MCQ", "")  # TB-MCQ is computed separately
    if native_path is None and pred_path is not None:
        native_path = os.path.join(pred_path, os.listdir(pred_path)[0])
    str_metrics = str_metrics.lower().split(",")
    str_metrics = [metric.replace("lcs-ta", "lcs").replace("barnaba", "escore").replace("rsrnasp", "rs-rnasp") for metric in str_metrics]
    rnadvisor_args["pred_dir"] = pred_path
    rnadvisor_args["native_path"] = native_path
    rnadvisor_args["out_path"] = out_path
    rnadvisor_args["scores"] = str_metrics
    rnadvisor_args["out_time_path"] = time_path
    rnadvisor_args["params"] = hp_params
    rnadvisor_args["tmp_dir"] = tmp_dir
    compute_metrics(**rnadvisor_args)
    if to_compute_tb:
        out_path_mcq = out_path.replace(".csv", "_tb_mcq.csv")
        compute_tb_mcq_per_sequence(pred_path, out_path_mcq, time_path)
    clean_df(out_path, scoring_functions)
    add_sum(out_path, z_sum, n_sum, scoring_functions is not None)
    with open(os.path.join(tmp_dir, "done.flag"), "w") as f:
        f.write("done")


def normalize_metrics(df: pd.DataFrame, is_sf: bool) -> pd.DataFrame:
    df_n = pd.DataFrame(index=df.index)
    desc_metrics = DESC_METRICS + DESC_ENERGY
    for col in df.columns:
        min_val = df[col].min(skipna=True)
        max_val = df[col].max(skipna=True)
        df_n[f"N-{col}"] = (df[col] - min_val) / (max_val - min_val)
        if col in desc_metrics:
            df_n[f"N-{col}"] = 1 - df_n[f"N-{col}"]
    cols = [f"N-{col}" for col in df.columns if col in SUB_SCORING + SUB_METRICS]
    if not is_sf:
        cols = [metric for metric in cols if "N-BARNABA-eSCORE" not in metric]
    df_n["N-SUM"] = df_n[cols].sum(axis=1, skipna=True)
    return df_n

def zscore_metrics(df: pd.DataFrame, is_sf: bool) -> pd.DataFrame:
    df_z = pd.DataFrame(index=df.index)
    desc_metrics = DESC_METRICS + DESC_ENERGY
    for col in df.columns:
        if col != "Z-SUM" and pd.api.types.is_numeric_dtype(df[col]):
            mean = df[col].mean(skipna=True)
            std = df[col].std(skipna=True)
            if std == 0 or np.isnan(std):
                df_z[f"Z-{col}"] = np.nan
            else:
                df_z[f"Z-{col}"] = (df[col] - mean) / std
            if col in desc_metrics:
                df_z[f"Z-{col}"] = -df_z[f"Z-{col}"]
    cols = [f"Z-{col}" for col in df.columns if col in SUB_SCORING + SUB_METRICS]
    if not is_sf:
        cols = [metric for metric in cols if "Z-BARNABA-eSCORE" not in metric]
    df_z["Z-SUM"] = df_z[cols].sum(axis=1, skipna=True)
    return df_z


def add_sum(in_df: str, z_sum: bool, n_sum: bool, is_sf):
    df = pd.read_csv(in_df, index_col=0)
    dfs_to_concat = [df]
    if z_sum:
        dfs_to_concat.append(zscore_metrics(df, is_sf))
    if n_sum:
        dfs_to_concat.append(normalize_metrics(df, is_sf))
    df_combined = pd.concat(dfs_to_concat, axis=1)
    df_combined.to_csv(in_df)


def clean_df(in_df: str, scoring_functions: List):
    """
    Clean the dataframe by removing unwanted names and columns
    """
    df = pd.read_csv(in_df, index_col=0)
    df.index = df.index.map(lambda x: x.replace("normalized_", ""))
    if scoring_functions is not None:
        try:
            df = df.drop(["BARNABA-RMSD", "BARNABA-eRMSD"], axis=1)
        except KeyError:
            pass
    df.to_csv(in_df)


def convert_preds_cif_to_pdb(pred_paths: List[str]) -> List[str]:
    """
    Convert .cif to .pdb
    :param pred_paths:
    :return:
    """
    new_preds = []
    for pred in pred_paths:
        if pred.endswith(".cif"):
            new_path = pred.replace(".cif", "pdb")
            convert_cif_to_pdb(pred, new_path)
        else:
            new_path = pred
        new_preds.append(new_path)
    return new_preds


def add_tb_mcq_to_df(tb_mcq: Dict, in_path: str):
    """
    Add the TB-MCQ to the dataframe
    """
    df = pd.read_csv(in_path, index_col=0)
    df_tb = pd.DataFrame({"TB-MCQ": tb_mcq.values()}, index=tb_mcq.keys())
    # Clean names
    if "normalized_" in df.index[0]:
        df_tb.index = df_tb.index.map(lambda x: f"normalized_{x}")
    new_df = pd.concat([df, df_tb], axis=1)
    new_df.to_csv(in_path)


def compute_tb_mcq_per_sequence(pred_path: str, out_path: str, time_path):
    """
    Compute the TB-MCQ per sequence
    :param pred_path: path to a predicted structure
    :param out_path: path where to save the predicted error
    :param time_path: path where to save the time
    """
    if os.path.isdir(pred_path):
        pred_files = [
            os.path.join(pred_path, name)
            for name in os.listdir(pred_path)
            if name.endswith(".pdb") or name.endswith(".cif")
        ]
    elif os.path.isfile(pred_path):
        pred_files = pred_path
    pred_files = convert_preds_cif_to_pdb(pred_files)
    df, df_angle, tb_mcq, c_time = TBMCQ.get_tb_mcq_all(pred_files)
    df.to_csv(out_path, index=False)
    df_angle.to_csv(out_path.replace(".csv", "_per_angle.csv"))
    add_tb_mcq_to_df(tb_mcq, out_path.replace("_tb_mcq", ""))
    add_tb_mcq_to_df(c_time, time_path)
