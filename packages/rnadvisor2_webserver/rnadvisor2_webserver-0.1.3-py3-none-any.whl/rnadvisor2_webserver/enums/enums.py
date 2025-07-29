ALL_METRICS = [
    "RMSD",
    "P-VALUE",
    "INF",
    "DI",
    "MCQ",
    "BARNABA",
    "GDT-TS",
    "LDDT",
    "LCS-TA",
    "TM-SCORE",
    "CAD-score"
]
QUICK_METRICS = ["RMSD", "INF", "TM-SCORE",]
ALL_SCORING_FUNCTIONS = ["BARNABA", "DFIRE", "rsRNASP", "RASP", "TB-MCQ", "CGRNASP",
                         "3dRNAscore", "PAMNet", "LociPARSE", "ARES"]
QUICK_SCORING_FUNCTIONS = ["DFIRE", "3dRNAscore", "RASP", "TB-MCQ"]
SUB_METRICS = [
    "RMSD",
    "P-VALUE",
    "BARNABA-eRMSD",
    "TM-score",
    "GDT-TS",
    "INF-ALL",
    "lddt",
    "MCQ",
    "LCS-TA-COVERAGE-10",
    "LCS-TA-COVERAGE-15",
    "LCS-TA-COVERAGE-20",
    "LCS-TA-COVERAGE-25",
]

# Higher is better
ASC_METRICS = [
    "INF-ALL",
    "TM-SCORE",
    "GDT-TS",
    "LDDT",
    "INF-WC",
    "INF-NWC",
    "INF-STACK",
    "GDT-TS",
]
# Lower is better
DESC_METRICS = ["RMSD", "P-VALUE", "DI", "BARNABA-RMSD", "BARNABA-eRMSD", "MCQ"]
COLORS_MAPPING = {
    "RMSD": "#ba0505",
    "INF-ALL": "#58585a",
    # "CAD": "#ee7f00",
    "TM-score": "#8b1b57",
    "GDT-TS": "#5e6c49",
    "LDDT": "#2da3ba",
    "P-VALUE": "#b77352",
    "εRMSD": "#ffd23f",
    "MCQ": "#005794",
    "LCS-10": "#3dbc75",
    "LCS-15": "#3dbc75",
    "LCS-20": "#3dbc75",
    "LCS-25": "#3dbc75",
}
OLD_TO_NEW = {
    "BARNABA-eRMSD": "εRMSD",
    "BARNABA-eSCORE": "εSCORE",
    "lddt": "LDDT",
    "3drnascore": "3dRNAScore",
    "LCS-TA-COVERAGE-10": "LCS-10",
    "LCS-TA-COVERAGE-15": "LCS-15",
    "LCS-TA-COVERAGE-20": "LCS-20",
    "LCS-TA-COVERAGE-25": "LCS-25",
}
METRICS_TO_HIDE = [
    "INF-STACK",
    "INF-WC",
    "INF-NWC",
    "BARNABA-RMSD",
    "GDT-TS@2",
    "GDT-TS@4",
    "GDT-TS@8",
    "GDT-TS@1",
    "BARNABA-eSCORE",
    "DI",
    "CLASH",
    "RASP-NB-CONTACTS"
]
DESC_ENERGY = ["DFIRE", "RASP-ENERGY", "RASP-NORMALIZED-ENERGY", "rsRNASP", "εSCORE", "TB-MCQ", "cgRNASP","cgRNASP-C",
                "cgRNASP-PC", "3drnascore", "PAMNet", "LociPARSE"]
NEGATIVE_ENERGY = ["εSCORE", "LociPARSE", ]
SUB_SCORING = [
    "DFIRE",
    "RASP-ENERGY",
    "rsRNASP",
    "εSCORE",
    "TB-MCQ",
    "cgRNASP",
    "3drnascore",
    "BARNABA-eSCORE",
    "PAMNet",
    "LociPARSE"
]
COLORS_MAPPING_SCORING = {
    "RASP-ENERGY": "#febe6f",
    "εSCORE": "#ff7f00",
    "BARNABA-eSCORE": "#ff7f00",
    "DFIRE": "#cab2d5",
    "rsRNASP": "#b9de28",
    "RASP-NB-CONTACTS": "#A0E9FF",
    "RASP-NORMALIZED-ENERGY": "#17A5A5",
    "TB-MCQ": "#32a02d",
    "cgRNASP": "#b15928",
    "3dRNAScore": "#a6cee3",
    "3drnascore": "#a6cee3",
    "LociPARSE": "#6a3d9a",
    "lociparse": "#6a3d9a",
    "PAMNet": "#b2df8a",
}

import os

ALIGNED_PATH = os.path.join("data", "tmp", "aligned.pdb")
OUT_PATH = os.path.join("data", "output", "tmp_out.csv")
TIME_PATH, LOG_PATH = os.path.join("data", "output", "time.csv"), os.path.join(
    "data", "output", "log.csv"
)
PRED_DIR = os.path.join("data", "tmp", "preds")
NATIVE_PATH, PRED_PATHS = None, None
CASP_PATH, RNA_PUZZLES_PATH = os.path.join("data", "CASP_RNA", "NATIVE"), os.path.join(
    "data", "RNA_PUZZLES", "NATIVE"
)
CASP_CHALLENGES = [
    "R1107",
    "R1108",
    "R1116",
    "R1117",
    "R1126",
    "R1128",
    "R1149",
    "R1156",
    "R1189",
    "R1190",
]
RNA_PUZZLES_CHALLENGES = [
    "rp03",
    "rp04",
    "rp05",
    "rp06",
    "rp07",
    "rp08",
    "rp09",
    "rp11",
    "rp12",
    "rp13",
    "rp14_bound",
    "rp14_free",
    "rp16",
    "rp17",
    "rp18",
    "rp21",
    "rp23",
    "rp24",
    "rp25",
    "rp29",
    "rp32",
    "rp34",
]


TEXT_BY_FIGURES = {
    "Bar plot": "Bar plot with the normalised scores for each score considered. The higher the score, the better the model. The scores are normalised to be between 0 and 1, "
    "where 1 is the best and 0 the worst. The decreasing scores are reversed to be increasing.",
    "Polar plot": "Polar plot for the INF metric for each model. "
    "It considers the different type of interactions possible in the RNA structure: stacking, Watson-Crick, non-Watson-Crick.",
    "TB-MCQ per position": "TB-MCQ value for each position of the sequence for each model.",
    "TB-MCQ per angle": "Line polar plot with the TB-MCQ value for each angle for each model. The lower the MCQ value, the better the model.",
    "Time plot": "Time plot for the different metrics/scoring functions used. It shows the time taken to compute the score for all the models.",
    "Results": "Obtained dataframe with the different metrics/scoring functions for each model.",
}
