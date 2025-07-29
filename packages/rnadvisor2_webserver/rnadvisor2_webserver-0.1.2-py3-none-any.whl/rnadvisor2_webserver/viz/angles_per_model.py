import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px


class AnglesPerModel:
    def __init__(self, in_path: str):
        self.df = pd.read_csv(in_path, index_col=0)

    @staticmethod
    def get_viz(in_path):
        angles_helper = AnglesPerModel(in_path)
        return angles_helper.plot_mcq_per_angle_all()

    def plot_mcq_per_angle_all(self):
        df_long = self.df.reset_index().melt(
            id_vars="index", var_name="MCQ", value_name="Angle"
        )
        df_long.rename(columns={"index": "Name"}, inplace=True)
        models = df_long["Name"].unique()
        colors = px.colors.qualitative.D3
        # Plot all the models in a single plot
        fig = px.line_polar(
            df_long,
            r="Angle",
            theta="MCQ",
            line_group="Name",
            color="Name",
            line_close=True,
            color_discrete_sequence=colors,
        )
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, df_long["Angle"].max()],
                ),
                angularaxis=dict(
                    showticklabels=True,
                ),
            ),
            showlegend=True,
            height=500,
        )
        fig.update_layout(font=dict(size=25))
        fig.update_annotations(font_size=30)
        return fig

    def plot_mcq_per_angle(self):
        df_long = self.df.reset_index().melt(
            id_vars="index", var_name="MCQ", value_name="Angle"
        )
        df_long.rename(columns={"index": "Name"}, inplace=True)
        models = df_long["Name"].unique()
        num_models = len(models)
        cols = 3
        num_rows = (num_models + cols - 1) // cols
        fig = make_subplots(
            rows=num_rows,
            cols=cols,
            subplot_titles=models,
            specs=[[{"type": "polar"} for _ in range(cols)] for _ in range(num_rows)],
            vertical_spacing=0.01,
            horizontal_spacing=0.1,
        )
        for i, model in enumerate(models):
            row = (i // cols) + 1
            col = (i % cols) + 1
            model_data = df_long[df_long["Name"] == model]
            fig.add_trace(
                go.Scatterpolar(
                    r=model_data["Angle"],
                    theta=model_data["MCQ"],
                    mode="lines+markers",
                    name=model,
                    line=dict(color="blue"),
                ),
                row=row,
                col=col,
            )
        layout_updates = {
            f"polar{i + 1}": dict(
                bgcolor="white",
                radialaxis=dict(
                    range=[0, df_long["Angle"].max()],
                    showticklabels=True,
                    color="black",
                    gridcolor="black",
                ),
                angularaxis=dict(showticklabels=True, color="black", gridcolor="black"),
            )
            for i in range(len(models))
        }
        fig.update_layout(
            height=3000,
            showlegend=False,
            **layout_updates,
        )
        fig.update_layout(font=dict(size=25))
        fig.update_annotations(font_size=30)
        return fig

    @staticmethod
    def clean_fig(fig):
        fig.update_annotations(font_size=20)
        params_axes = dict(
            showgrid=True,
            gridcolor="grey",
            linecolor="black",
            zeroline=False,
            linewidth=1,
            showline=True,
            mirror=True,
            gridwidth=1,
            griddash="dot",
            tickson="boundaries",
        )
        fig.update_yaxes(**params_axes)
        fig.update_xaxes(**params_axes)
        fig.update_layout(
            dict(plot_bgcolor="white"), margin=dict(l=10, r=5, b=10, t=20)
        )
        param_marker = dict(
            opacity=1, line=dict(width=0.5, color="DarkSlateGrey"), size=6
        )
        fig.update_traces(marker=param_marker, selector=dict(mode="markers"))
        fig.update_layout(
            font=dict(
                family="Computer Modern",
                size=10,
            )
        )
        fig.update_yaxes(matches=None)
        return fig
