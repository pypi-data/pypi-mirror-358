import os

import pandas as pd
import plotly.express as px

from rnadvisor2_webserver.enums.enums import OLD_TO_NEW


class PolarHelper:
    def __init__(self, in_path: str):
        """

        :param in_path: path to the .csv files with the given results
        """
        self.df = self.read_df(in_path)

    @staticmethod
    def read_df(in_path: str):
        """
        Read the dataset results
        """
        df = pd.read_csv(in_path, index_col=0)
        df = df.rename(columns=OLD_TO_NEW)
        df_reset = df.reset_index()
        if "rna" in df_reset.columns:
            df_out = pd.melt(df_reset, id_vars="rna", var_name="Metric", value_name="Value")
        else:
            df_out = pd.melt(df_reset, id_vars="index", var_name="Metric", value_name="Value")
        df_out = df_out.rename(columns={"rna": "Model", "index": "Model"})
        return df_out

    def viz(self):
        df = (
            self.df[["Metric", "Model", "Value"]]
            .groupby(["Model", "Metric"])
            .mean()
            .reset_index()
        )
        metric_order = ["INF-WC", "INF-NWC", "INF-STACK"]
        df["Metric"] = df["Metric"].astype(
            pd.CategoricalDtype(categories=metric_order, ordered=True)
        )
        df = df.sort_values(by="Metric").reset_index(drop=True)
        colors = ["#83b8d6", "#621038", "#ef8927"]
        fig = px.bar_polar(
            df,
            r="Value",
            theta="Model",
            color="Metric",
            template="plotly_white",
            color_discrete_sequence=colors,
            range_r=[0, 3],
        )
        fig = self._clean_polar_viz(fig)
        fig.update_layout(legend_title_text="Metric:")
        return fig

    def _clean_polar_viz(self, fig):
        new_polars = {
            "polar": dict(
                radialaxis=dict(
                    showline=False,
                    showgrid=True,
                    linewidth=1,
                    linecolor="black",
                    gridcolor="black",
                    gridwidth=1,
                    showticklabels=True,
                    dtick=1,
                ),
                angularaxis=dict(
                    linewidth=1,
                    visible=True,
                    linecolor="black",
                    showline=True,
                    gridcolor="black",
                ),
                radialaxis_tickfont_size=14,
                bgcolor="white",
            )
        }
        fig.update_layout(
            legend=dict(
                orientation="h",
                bgcolor="#f3f3f3",
                bordercolor="Black",
                borderwidth=1,
                font=dict(size=20),
                x=0.25,
                y=-0.1,
            ),
        )
        fig.update_layout(margin=dict(l=0, r=0, b=50, t=50))
        fig.update_layout(font_size=22)
        fig.update_layout(
            **new_polars,
            showlegend=True,
        )
        return fig

    @staticmethod
    def get_viz(in_path: str):
        polar_helper = PolarHelper(in_path)
        return polar_helper.viz()
