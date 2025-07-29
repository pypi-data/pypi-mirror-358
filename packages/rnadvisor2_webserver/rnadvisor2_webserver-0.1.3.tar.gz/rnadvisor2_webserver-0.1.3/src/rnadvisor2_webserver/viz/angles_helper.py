from typing import List, Any
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import numpy as np
import pandas as pd


class AnglesHelper:
    def __init__(self, in_path: str):
        self.df = pd.read_csv(in_path, index_col=0)

    def viz(self):
        sequence = list(self.df.index)
        mcq_per_seq = self.df.values
        names = self.df.columns
        return self.plot_mcq_per_position(sequence, mcq_per_seq, names)

    @staticmethod
    def update_plot(fig: Any):
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
        return fig

    @staticmethod
    def plot_mcq_per_position(sequence: List, mcq_per_seq: List, names: List):
        z = np.array(mcq_per_seq)
        sequence = [f"{seq}_{i}" for i, seq in enumerate(sequence)]
        y = names
        fig = go.Figure(data=go.Heatmap(z=z.T, x=sequence, y=y, colorscale="Viridis"))
        fig.update_layout(
            xaxis=dict(title="Sequence Position"),
        )
        fig = AnglesHelper.update_plot(fig)
        return fig

    @staticmethod
    def get_viz(in_path):
        angles_helper = AnglesHelper(in_path)
        return angles_helper.viz()
