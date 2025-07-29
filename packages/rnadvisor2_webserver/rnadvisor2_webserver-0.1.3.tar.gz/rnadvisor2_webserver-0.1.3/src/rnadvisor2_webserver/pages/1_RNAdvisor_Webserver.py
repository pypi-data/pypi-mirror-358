from streamlit_molstar.auto import st_molstar_auto
from importlib.resources import files
import time
import json
import streamlit as st
import uuid
import os
import shutil
from streamlit_javascript import st_javascript

# Constants
from rnadvisor2_webserver.enums.enums import CASP_CHALLENGES, RNA_PUZZLES_CHALLENGES, ALL_METRICS, \
    QUICK_METRICS, ALL_SCORING_FUNCTIONS, QUICK_SCORING_FUNCTIONS
from rnadvisor2_webserver.utils.align_helper import align_structures
from rnadvisor2_webserver.utils.rnadvisor_helper import run_rnadvisor
from rnadvisor2_webserver.utils.utils import convert_cif_to_pdb, viz_structure
from rnadvisor2_webserver.viz.page_viz import show_results

PREFIX_IMG = files("rnadvisor2_webserver.img.webserver")
PREFIX_DATA = files("rnadvisor2_webserver.data")
TMP_ROOT = "tmp"
os.makedirs(TMP_ROOT, exist_ok=True)

# Session State Initialization
for key, default in {
    "job_status": {}, "run_clicked": False, "method": "Metrics",
    "returning_from_other_page": False, "current_mode": None
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

st.set_page_config(layout="wide")
params = st.query_params
page = params.get("page", "main")
token = params.get("token", None)

def reconstruct_task_info(token):
    tmp_dir = os.path.join(TMP_ROOT, token)
    path = os.path.join(tmp_dir, "task_info.json")
    if not os.path.exists(path): return None
    try:
        with open(path) as f:
            info = json.load(f)
        info["tmp_dir"] = tmp_dir
        return info
    except Exception as e:
        print(f"Failed to load task_info: {e}")
        return None

def shared_structure_loader():
    st.header("Examples")
    _, col, _ = st.columns([2, 6, 2])
    challenge_type = col.segmented_control("Choose example set", ["CASP15", "RNA-Puzzles"], key="example_challenge")
    challenge = "casp_rna" if challenge_type == "CASP15" else "rna_puzzles"
    names = CASP_CHALLENGES if challenge_type == "CASP15" else RNA_PUZZLES_CHALLENGES
    name = st.selectbox("Select structure", names, key="shared_structure_select")
    if st.button("Load Example"):
        load_shared_example(challenge, name)

def load_shared_example(challenge, name):
    native = PREFIX_DATA.joinpath(os.path.join(challenge.upper(), "NATIVE", f"{name}.pdb"))
    pred_dir = PREFIX_DATA.joinpath(os.path.join(challenge.upper(), "PREDS", name))
    preds = [os.path.join(pred_dir, f) for f in os.listdir(pred_dir) if f.endswith(".pdb")][:8]
    token = str(uuid.uuid4())
    tmp = os.path.join(TMP_ROOT, token)
    os.makedirs(os.path.join(tmp, "preds"), exist_ok=True)
    shutil.copy(native, os.path.join(tmp, "native.pdb"))
    paths = []
    for p in preds:
        tgt = os.path.join(tmp, "preds", os.path.basename(p))
        shutil.copy(p, tgt)
        paths.append(tgt)
    st.session_state.update({
        "native_path": os.path.join(tmp, "native.pdb"),
        "pred_paths": paths, "pred_dir": os.path.join(tmp, "preds"),
        "tmp_dir": tmp, "unique_token": token, "molstar_key": str(uuid.uuid4()),
        "uploaded_file": None, "uploaded_native": None,
        "used_shared_structure": True, "show_structures": True
    })
    st.query_params.page = "main"
    st.rerun()

def offer_task_launch(metrics, scoring, z_sum, n_sum):
    if "unique_token" not in st.session_state:
        token = str(uuid.uuid4())
        tmp_dir = os.path.join(TMP_ROOT, token)
        os.makedirs(tmp_dir, exist_ok=True)
        st.session_state["unique_token"] = token
        st.session_state["tmp_dir"] = tmp_dir
    else:
        token = st.session_state["unique_token"]
        tmp_dir = st.session_state["tmp_dir"]

    if not st.session_state.get("pred_dir"):
        return
    if st.session_state.method == "Metrics" and not st.session_state.get("native_path"):
        st.warning("Please upload a native structure for metric-based evaluation.")
        return
    if st.button("Run Task", key="run_task_button"):
        task = {
            "pred_dir": st.session_state["pred_dir"],
            "tmp_dir": tmp_dir,
            "native_path": st.session_state.get("native_path"),
            "metrics": metrics if st.session_state.method == "Metrics" else None,
            "scoring_functions": scoring if st.session_state.method == "Scoring functions" else None,
            "z_sum": z_sum, "n_sum": n_sum,
            "analysis_mode": st.session_state.method
        }
        st.session_state[f"{token}_info"] = task
        st.session_state[f"{token}_task_run"] = "pending"
        with open(os.path.join(tmp_dir, "task_info.json"), "w") as f:
            json.dump(task, f)
        st.query_params["page"] = "result"
        st.query_params["token"] = token
        st.rerun()

def get_metrics_scoring():
    st.markdown("### Quality assessment method")
    _, col, _ = st.columns([5, 6, 5])
    col.segmented_control("Select evaluation mode", ["Metrics", "Scoring functions"], key="method")
    reset_analysis_state()
    _, col, _ = st.columns([3, 6, 3])
    metrics, scoring = [], None
    if st.session_state.method == "Metrics":
        metrics = col.multiselect("Select Metrics", ALL_METRICS, default=QUICK_METRICS)
    else:
        scoring = col.multiselect("Select Scoring functions", ALL_SCORING_FUNCTIONS, default=QUICK_SCORING_FUNCTIONS)
    with st.expander("Optional parameters"):
        z_sum = st.checkbox("Z-SUM", value=True, key="z_sum")
        n_sum = st.checkbox("N-SUM", value=True, key="z_num")
        threshold, mcq = 10, "All"
        if st.session_state.method == "Metrics":
            threshold = st.slider("LCS-TA threshold", 10, 25, 10, 5, key="threshold")
            mcq = st.selectbox("MCQ method", ["Strict", "Moderate", "All"], index=2, key="mcq_method")
    return metrics, scoring, z_sum, n_sum

def reset_analysis_state():
    if st.session_state.get("current_mode") != st.session_state.method:
        for key in ["results_data", "aligned_path", "task_run", "metrics", "scoring_functions"]:
            st.session_state.pop(key, None)
    st.session_state.current_mode = st.session_state.method

def cleanup_on_page_change():
    tmp_dir = st.session_state.get("tmp_dir")
    if tmp_dir and os.path.exists(tmp_dir):
        try:
            shutil.rmtree(tmp_dir)
        except Exception as e:
            st.warning(f"Cleanup failed: {e}")
    for key in ["native_path", "pred_paths", "pred_dir", "molstar_key",
                "uploaded_file", "uploaded_native", "used_shared_structure",
                "tmp_dir", "unique_token", "show_structures"]:
        st.session_state.pop(key, None)

def show_upload_section():
    col1, col2 = st.columns(2)

    if st.session_state.method == "Metrics":
        col1.write("### Native structure")
        uploaded_native = col1.file_uploader("Upload native (.pdb, .cif)", accept_multiple_files=False)
        if uploaded_native is not None:
            st.session_state["uploaded_native"] = uploaded_native

    col2.write("### Predicted structures")
    uploaded_file = col2.file_uploader("Upload predictions (.pdb, .cif)", accept_multiple_files=True)
    if uploaded_file is not None:
        st.session_state["uploaded_file"] = uploaded_file

def handle_file_upload():
    if st.session_state.get("used_shared_structure"): return
    pred_files = st.session_state.get("uploaded_file")
    native_file = st.session_state.get("uploaded_native")
    method = st.session_state.method
    if not pred_files and not native_file:
        st.session_state["pred_paths"] = None
        st.session_state["pred_dir"] = None
        return
    if "unique_token" not in st.session_state:
        token = str(uuid.uuid4())
        st.session_state["unique_token"] = token
        st.session_state["tmp_dir"] = os.path.join(TMP_ROOT, token)
        os.makedirs(st.session_state["tmp_dir"], exist_ok=True)
    tmp = st.session_state["tmp_dir"]
    if method == "Metrics" and native_file:
        tmp_native = os.path.join(tmp, native_file.name)
        with open(tmp_native, "wb") as f:
            f.write(native_file.read())
        final_native = os.path.join(tmp, "native.pdb")
        if tmp_native.endswith(".cif"):
            convert_cif_to_pdb(tmp_native, final_native)
            os.remove(tmp_native)
        else:
            shutil.move(tmp_native, final_native)
        st.session_state["native_path"] = final_native
        st.session_state["molstar_key"] = str(uuid.uuid4())
    if pred_files:
        pred_dir = os.path.join(tmp, "preds")
        os.makedirs(pred_dir, exist_ok=True)
        paths = []
        for file in pred_files[:20]:
            path = os.path.join(pred_dir, file.name)
            with open(path, "wb") as f:
                f.write(file.read())
            if path.endswith(".cif"):
                converted = path.replace(".cif", ".pdb")
                convert_cif_to_pdb(path, converted)
                os.remove(path)
                paths.append(converted)
            else:
                paths.append(path)
        st.session_state.update({"pred_paths": paths, "pred_dir": pred_dir, "molstar_key": str(uuid.uuid4())})

def display_structures():
    native = st.session_state.get("native_path")
    preds = st.session_state.get("pred_paths")
    token = st.session_state.get("molstar_key", "default")
    col1, col2 = st.columns(2)
    if native and st.session_state.method == "Metrics":
        with col1: st_molstar_auto([native], key=f"native_{token}")
    if preds:
        with col2: st_molstar_auto(preds[:5], key=f"preds_{token}")

def handle_result_page(token):
    if not token:
        st.error("❌ No token found in the URL.")
        return

    full_url = st_javascript("await fetch('').then(r => window.parent.location.href)")
    st.info(f"🔗 Save this URL to view your results later:\n\n`{full_url}`")

    task_info = st.session_state.get(f"{token}_info") or reconstruct_task_info(token)
    if not task_info:
        st.error("🛑 Could not find task data for token.")
        return

    st.session_state[f"{token}_info"] = task_info
    analysis_mode = task_info.get("analysis_mode", "Metrics")
    run_flag = f"{token}_task_run"
    run_once_key = f"{token}_already_ran"
    if run_once_key not in st.session_state:
        st.session_state[run_once_key] = False

    pred_path = task_info["pred_dir"]
    native_path = task_info.get("native_path")
    tmp_dir = task_info["tmp_dir"]
    out_path = os.path.join(tmp_dir, "results.csv")
    aligned_path = os.path.join(tmp_dir, "aligned.pdb")
    time_path = os.path.join(tmp_dir, "times.csv")
    log_path = os.path.join(tmp_dir, "log.txt")
    metrics = task_info.get("metrics", [])
    scoring_functions = task_info.get("scoring_functions")
    z_sum = task_info.get("z_sum", True)
    n_sum = task_info.get("n_sum", True)

    if analysis_mode == "Metrics" and os.path.exists(aligned_path):
        viz_structure(aligned_path, key=f"aligned_structure_{token}")
    elif analysis_mode == "Scoring functions":
        pred_paths = [os.path.join(pred_path, f) for f in os.listdir(pred_path) if f.endswith(".pdb")][:5]
        st_molstar_auto(pred_paths, key=f"structure_pred_aligned_{token}")

    if not os.path.exists(out_path) and not st.session_state[run_once_key]:
        st.session_state[run_flag] = "pending"
        st.session_state[run_once_key] = True

        mcq_method = st.session_state.get("mcq_method", "All")
        mcq_to_params = {"Strict": 0, "Moderate": 1, "All": 2}
        hp_params = {
            "mcq_threshold": st.session_state.get("threshold", 10),
            "mcq_mode": mcq_to_params.get(mcq_method, 2)
        }

        if os.path.isdir(pred_path):
            pred_paths = [os.path.join(pred_path, f) for f in os.listdir(pred_path) if f.endswith(".pdb")]
        else:
            pred_paths = [pred_path]

        with st.spinner("Running RNAdvisor... Please wait."):
            try:
                if analysis_mode == "Metrics":
                    align_structures(native_path, pred_paths, aligned_path)
                run_rnadvisor(
                    native_path=native_path if analysis_mode == "Metrics" else None,
                    pred_path=pred_path,
                    out_path=out_path,
                    metrics=metrics if analysis_mode == "Metrics" else None,
                    scoring_functions=scoring_functions if analysis_mode == "Scoring functions" else None,
                    time_path=time_path,
                    log_path=log_path,
                    hp_params=hp_params if analysis_mode == "Metrics" else None,
                    tmp_dir=tmp_dir,
                    z_sum=z_sum,
                    n_sum=n_sum,
                )
                st.session_state[run_flag] = True
                if analysis_mode == "Metrics":
                    st.session_state["aligned_path"] = aligned_path
                st.success("✅ RNAdvisor completed!")
                st.experimental_rerun()
            except Exception as e:
                st.session_state[run_flag] = False
                st.session_state[run_once_key] = False
                st.error(f"❌ Failed to run RNAdvisor: {e}")
                return

    done_flag = os.path.join(tmp_dir, "done.flag")
    if not os.path.exists(done_flag):
        with st.spinner("⏳ RNAdvisor is running... waiting for full results."):
            placeholder = st.empty()
            for i in range(120):
                if os.path.exists(done_flag):
                    st.rerun()
                placeholder.info(f"⌛ Waiting... {i * 2} seconds elapsed.")
                time.sleep(2)
            st.error("⏰ Timeout: RNAdvisor results not fully ready.")
            if st.button("🔄 Check Again"):
                st.rerun()
    else:
        show_results(out_path, time_path, is_only_scoring=(analysis_mode == "Scoring functions"))


def handle_main_page():
    st.title("RNAdvisor Webserver")
    return_gif_native_figures()
    show_upload_section()
    handle_file_upload()
    display_structures()
    metrics, scoring, z_sum, n_sum = get_metrics_scoring()
    offer_task_launch(metrics, scoring, z_sum, n_sum)


def return_gif_native_figures():
    col1, col2 = st.columns(2)
    native_path = PREFIX_IMG.joinpath("native_rp14b.gif")
    pred_path = PREFIX_IMG.joinpath("pred_rp14b.gif")
    col1.image(native_path)
    col2.image(pred_path)


if page == "main":
    if st.session_state.get("returning_from_other_page"):
        cleanup_on_page_change()
        st.session_state["returning_from_other_page"] = False
    with st.sidebar:
        shared_structure_loader()
    handle_main_page()
elif page == "result":
    st.session_state["returning_from_other_page"] = True
    handle_result_page(token)
