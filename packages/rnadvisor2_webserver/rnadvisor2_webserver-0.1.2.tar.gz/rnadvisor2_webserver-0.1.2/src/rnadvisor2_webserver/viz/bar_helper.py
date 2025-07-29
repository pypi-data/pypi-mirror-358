from typing import List
import numpy as np

import plotly.express as px

from rnadvisor2_webserver.enums.enums import DESC_METRICS, SUB_METRICS, OLD_TO_NEW, COLORS_MAPPING
from rnadvisor2_webserver.utils.utils import update_bar_plot
from rnadvisor2_webserver.viz.polar_helper import PolarHelper


class BarHelper:
    def __init__(self, in_path: str):
        self.df = PolarHelper.read_df(in_path)

    def normalize_metrics(self, df):
        metrics = df["Metric"].unique()
        df["Value (normalised)"] = [np.nan] * df.shape[0]
        for metric in metrics:
            mask = df["Metric"] == metric
            if metric.startswith("N-"):
                df.loc[mask, "Value (normalised)"] = df["Metric"]
        return df

    def viz(self):
        """Plot the polar distribution for a dataset."""
        df = self.df[self.df["Metric"].str.startswith("N-")].copy()
        df["Metric"] = df["Metric"].str.replace(r"^N-", "", regex=True)
        n_df = self.df[~self.df["Metric"].str.startswith(("N-", "Z-"))].copy()
        df = df.merge( n_df[["Model", "Metric", "Value"]].rename(columns={"Value": "True value"}), how="left", on=["Model", "Metric"] )
        df = df[df["Metric"].isin(SUB_METRICS)]
        df = df.replace(OLD_TO_NEW)
        df = (
            df[["Metric", "Model", "Value", "True value"]]
            .groupby(["Model", "Metric"])
            .mean()
            .reset_index()
        )
        if len(df) == 0:
            return None
        fig = px.bar(
            df,
            y="Model",
            x="Value",
            color="Metric",
            color_discrete_map=COLORS_MAPPING,
            orientation="h",
            category_orders={
                "Metric": list(COLORS_MAPPING.keys()),
            },
            labels={"Metric": "Normalized metrics"},
            hover_data=["Value", "True value"],
        )
        fig = update_bar_plot(fig)
        return fig

    @staticmethod
    def get_viz(in_path):
        bar_helper = BarHelper(in_path)
        return bar_helper.viz()

