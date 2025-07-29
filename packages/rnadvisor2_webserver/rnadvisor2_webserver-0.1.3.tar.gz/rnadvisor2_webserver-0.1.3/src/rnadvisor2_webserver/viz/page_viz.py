import streamlit as st
from streamlit_molstar.auto import st_molstar_auto
import pandas as pd

from rnadvisor2_webserver.enums.enums import TEXT_BY_FIGURES
from rnadvisor2_webserver.viz.angles_helper import AnglesHelper
from rnadvisor2_webserver.viz.angles_per_model import AnglesPerModel
from rnadvisor2_webserver.viz.bar_helper import BarHelper
from rnadvisor2_webserver.viz.bar_helper_scoring import BarHelperScoring
from rnadvisor2_webserver.viz.polar_helper import PolarHelper
from rnadvisor2_webserver.viz.time_plot import TimePlot


def viz_structure(in_path: str, key="aligned_structure"):
    st.write("---")
    st.write("## Aligned structures")
    st.write("Aligned structures using US-Align.")
    st_molstar_auto([in_path], key=key)


def show_results(out_path: str, time_path: str, is_only_scoring: bool = False):
    df = pd.read_csv(out_path, index_col=0)
    df.index = df.index.map(lambda x: x.replace("normalized_", ""))
    st.write("## Results")
    st.write(TEXT_BY_FIGURES["Results"])
    st.dataframe(df)
    st.download_button("📥 Download Results", open(out_path, "rb"), file_name="results.csv")
    mapping_titles = {"TB-MCQ per position": "_tb_mcq.csv",
                      "TB-MCQ per angle": "_tb_mcq_per_angle.csv"}
    if is_only_scoring and len(df) > 1:
        fn_to_show = [BarHelperScoring]
        titles = ["Bar plot"]
        if "TB-MCQ" in df.columns:
            fn_to_show.extend([AnglesHelper, AnglesPerModel])
            titles.extend(["TB-MCQ per position", "TB-MCQ per angle"])
    else:
        fn_to_show, titles = [], []
        if len(df) > 1:
            fn_to_show.append(BarHelper)
            titles.append("Bar plot")
        if not is_only_scoring and len(df) > 1:
            fn_to_show.append(PolarHelper)
            titles.append("Polar plot")
    for index, fn in enumerate(fn_to_show):
        if titles[index] in mapping_titles:
            c_out_path = out_path.replace(".csv", mapping_titles[titles[index]])
        else:
            c_out_path = out_path
        fig = fn.get_viz(c_out_path)
        if fig is not None:
            st.write(f"## {titles[index]}")
            st.write(f"{TEXT_BY_FIGURES[titles[index]]}")
            st.plotly_chart(fig)
    fig_time = TimePlot.get_viz(time_path)
    st.write("## Time plot")
    st.write(f"{TEXT_BY_FIGURES['Time plot']}")
    st.plotly_chart(fig_time)
