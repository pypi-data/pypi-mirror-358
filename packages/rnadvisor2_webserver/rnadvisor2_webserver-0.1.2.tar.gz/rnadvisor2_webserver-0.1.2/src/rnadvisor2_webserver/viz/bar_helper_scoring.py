import plotly.express as px

from rnadvisor2_webserver.enums.enums import SUB_SCORING, COLORS_MAPPING_SCORING
from rnadvisor2_webserver.utils.utils import update_bar_plot
from rnadvisor2_webserver.viz.bar_helper import BarHelper


class BarHelperScoring(BarHelper):
    def __init__(self, *args, **kwargs):
        super(BarHelperScoring, self).__init__(*args, **kwargs)

    def viz(self):
        """Plot the polar distribution for a dataset."""
        df = self.df[self.df["Metric"].str.startswith("N-")].copy()
        df["Metric"] = df["Metric"].str.replace(r"^N-", "", regex=True)
        n_df = self.df[~self.df["Metric"].str.startswith(("N-", "Z-"))].copy()
        df = df.merge( n_df[["Model", "Metric", "Value"]].rename(columns={"Value": "True value"}), how="left", on=["Model", "Metric"] )
        df = df.rename(columns={"Metric": "Scoring function"})
        df = df[df["Scoring function"].isin(SUB_SCORING)]
        df = (
            df[["Scoring function", "Model", "Value", "True value"]]
            .groupby(["Model", "Scoring function"])
            .mean()
            .reset_index()
        )
        fig = px.bar(
            df,
            y="Model",
            x="Value",
            color="Scoring function",
            color_discrete_map=COLORS_MAPPING_SCORING,
            orientation="h",
            category_orders={
                "Metric": list(COLORS_MAPPING_SCORING.keys()),
            },
            labels={"Metric": "Normalized scoring function"},
            hover_data=["Value", "True value"],
            custom_data=["True value"],
        )
        fig = update_bar_plot(fig)
        return fig

    @staticmethod
    def get_viz(in_path):
        bar_helper = BarHelperScoring(in_path)
        return bar_helper.viz()
