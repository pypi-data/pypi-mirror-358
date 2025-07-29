import pandas as pd
import plotly.express as px

from rnadvisor2_webserver.enums.enums import COLORS_MAPPING, COLORS_MAPPING_SCORING


class TimePlot:
    def __init__(self, time_path: str):
        self.time_df = self.read_csv(time_path)

    def read_csv(self, time_path):
        df = pd.read_csv(time_path, index_col=[0])
        df = df.sum()
        df = df.reset_index()
        df = df.melt(id_vars="index", var_name="Model", value_name="Time (s)")
        df = df.rename(columns={"index": "Metric"})
        try:
            df = df[~df["Metric"].isin(["BARNABA-RMSD", "BARNABA-eRMSD"])]
        except KeyError:
            pass
        return df

    def update_fig(self, fig):
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
            title=None,
        )
        fig.update_xaxes(**params_axes)
        fig.update_yaxes(**params_axes)
        fig.update_layout(dict(plot_bgcolor="white"), margin=dict(l=0, r=5, b=0, t=20))
        param_marker = dict(
            opacity=1, line=dict(width=0.5, color="DarkSlateGrey"), size=6
        )
        fig.update_traces(marker=param_marker, selector=dict(mode="markers"))
        fig.update_xaxes(title_text="Metrics/Scoring functions")
        fig.update_yaxes(title_text="Time (s)")
        fig.update_layout(
            font=dict(
                family="Computer Modern",
                size=14,
            )
        )
        return fig

    def viz(self):
        fig = px.bar(
            self.time_df,
            x="Metric",
            y="Time (s)",
            color="Metric",
            color_discrete_map={**COLORS_MAPPING, **COLORS_MAPPING_SCORING},
        )
        fig = self.update_fig(fig)
        return fig

    @staticmethod
    def get_viz(in_path: str):
        time_plot = TimePlot(in_path)
        return time_plot.viz()

