import streamlit as st
from importlib.resources import files
PREFIX_IMG = files("rnadvisor2_webserver.img.help")

def help_page():
    st.set_page_config(
        layout="wide",
    )
    st.markdown(
        """
        ### Help
        If you have any questions or need help with the *RNAdvisor* tool, please contact us at [fariza.tahi@univ-evry.fr](fariza.tahi@univ-evry.fr).
        """
    )
    st.markdown("---")
    st.markdown("""
    
        ## How to use RNAdvisor 2
        
        RNAdvisor 2 is an updated version of the [RNAdvisor](https://github.com/EvryRNA/rnadvisor) tool with an interface available.
        The tool is designed to compute the quality of RNA 3D structures. It computes a variety of metrics and scoring functions.
        
        There are two main modes available: the **metric** mode and the **scoring function** mode:
        
        - The **metric** mode computes a variety of metrics for the input structures compared to a true reference structure.
        - The **scoring function** mode computes the RNA structural quality without the need for a reference structure.
        
        ### Inputs
        
        The user can choose to select one reference structure and multiple predicted structures. 
        The reference structure is the native structure of the RNA molecule. 
        The predicted structures are the molecules to evaluate the quality of.
        The user can input either a `.pdb` file or a `.cif` file. """)
    st.image(PREFIX_IMG.joinpath("main_website_0.png"))
    st.markdown("""
        Then, the user has to select the mode to use: **metric** or **scoring function**.
        """)
    st.image(PREFIX_IMG.joinpath("metrics_selection.png"))
    st.markdown("""
        It can then submit the input to the tool, and the results will be displayed. """)
    st.image(PREFIX_IMG.joinpath("submission.png"))
    st.markdown("""---""")
    st.markdown("""
        ## Metrics computation
        In the **metric** mode, the user can select around ten metrics. 
        Default metrics are selected for their quick computation and efficiency.""")
    # st.image("img/help/quick_metrics.png")
    st.markdown("""
      The user can select among other available metrics. 
    """)
    st.image(PREFIX_IMG.joinpath("all_metrics.png"))
    st.markdown("""
        The user can then select the hyperparameters for different metrics. 
        - **Meta-metrics**: whether to compute the meta-metrics (using either Z-score for Z-SUM or Min-max normalisation for N-SUM).
        - **LCS-TA**: the threshold to use for the Longest Common Subsequence (LCS) algorithm. Choice is between 10, 15, 20 and 25° for the MCQ threshold. 
        - **MCQ**: the mode to use for the computation of the MCQ. Choice is between 
        `Strict` (no computation if any violation is found), `Relaxed` (computation only on non violation parts) and `All` 
        (computation regardless any violation).""")
    st.image(PREFIX_IMG.joinpath("hp.png"))
    st.markdown("""
        ### Outputs and visualisation
        Once the user has selected the metrics and hyperparameters, the tool will compute the metrics for each predicted structure.
        Different visualisations are available. A link is available to retrieve the results later.
        - **Align structures**: we aligned the first 5 structures using [US-Align](https://zhanggroup.org/US-align/) tool.""")
    st.image(PREFIX_IMG.joinpath("aligned.png"))
    st.markdown("""
        - **Output dataframe**: the user can download the dataframe with the computed metrics for each predicted structure. A button is available to download the dataframe on the upper right.""")
    st.image(PREFIX_IMG.joinpath("df.png"))
    st.markdown("""
        - **Bar plot**: normalised scores for each metric considered. 
            The higher the score, the better the model. The scores are normalised to be between 0 and 1, where 1 is the best 
            and 0 the worst. The decreasing scores are reversed to be increasing. 
            The goal is to give a quick overview of which method seems the best in terms of the selected metrics.""")
    st.image(PREFIX_IMG.joinpath("bar_plot_metrics.png"))
    st.markdown("""
        - **Polar plot**: INF metrics for three types of interactions: Watson-Crick, Non-Watson-Crick and Stacking interactions.
      """)
    st.image(PREFIX_IMG.joinpath("polar_plot_metrics.png"))
    st.markdown("""
        - **Time plot**: time taken to compute the score for all the models.""")
    st.image(PREFIX_IMG.joinpath("time_plot_metrics.png"))
    st.markdown("""---""")
    st.markdown("""
        ## Scoring functions computation
        In the **scoring function** mode, the user can select among six existing scoring functions. 
    """)
    st.image(PREFIX_IMG.joinpath("scoring_functions.png"))
    st.markdown("""
        Once the scoring functions are selected, the user can submit the input to the tool.
        
        ### Outputs and visualisation
        Once the user has selected the metrics and hyperparameters, the tool will compute the different scoring functions.
        Different visualisations are available. 
        - **Output dataframe**: the user can download the dataframe with the computed scoring functions for each predicted structure.""")
    st.image(PREFIX_IMG.joinpath("df_sf.png"))
    st.markdown("""
        - **Bar plot**: normalised scores for each metric considered. 
            The higher the score, the better the model. The scores are normalised to be between 0 and 1, where 1 is the best 
            and 0 the worst. The decreasing scores are reversed to be increasing. 
            The goal is to give a quick overview of which method seems the best in terms of the selected scoring functions.
            The scoring functions used for the normalisation are among 3dRNAScore, eSCORE, DFIRE, PAMNet, RASP, TB-MCQ, cgRNASP and rsRNASP. 
            The user can freely choose which meta-scoring functions it can used by downloaded the dataframe and compute by himself the meta-scores. 
            """)
    st.image(PREFIX_IMG.joinpath("bar_plot_sf.png"))
    st.markdown("""
        - **TB-MCQ per position**: this plot shows the TB-MCQ (scoring function that reproduces the MCQ metric) value for each 
        position of the sequence for each model. It reproduces MCQ visualisations (inspired by [RNAtango](https://rnatango.cs.put.poznan.pl/)),
        with an estimation of the MCQ but without any reference structure.""")
    st.image(PREFIX_IMG.joinpath("tb_mcq_position.png"))
    st.markdown("""
        - **TB-MCQ per angle**: this plot shows the TB-MCQ value for each angle for each model. The lower the MCQ value, the better the model.
        """)
    st.image(PREFIX_IMG.joinpath("tb_mcq_angle.png"))
    st.markdown("""
        - **Time plot**: time taken to compute the score for all the models.""")
    st.image(PREFIX_IMG.joinpath("time_plot_sf.png"))
    st.markdown("""---""")
    st.markdown("""
        ## Loaded examples
        
        Different examples are available for the user: **metrics**, **scoring functions** and specific examples from 
        [RNA-Puzzles](https://www.rnapuzzles.org/) and [CASP-RNA](https://predictioncenter.org/index.cgi). 
        Predicted structures are from our [work](https://www.biorxiv.org/content/10.1101/2024.06.13.598780v2), where a dozens of 
        predictive models are available for each RNA structure of either RNA-Puzzles or CASP-RNA. We set four examples per each RNA structure for the examples.""")
    st.image(PREFIX_IMG.joinpath("examples.png"))
    st.markdown("""
        - **Metrics**: the user can select the **Metrics** example where one reference structure and multiple predicted structures are available.
        - **Scoring functions**: the user can select the **Scoring functions** example where one reference structure and multiple predicted structures are available.
        - **RNA-Puzzles**: the user can select the **RNA-Puzzles** example where one reference structure and multiple predicted structures are available. 
        - **CASP-RNA**: the user can select the **CASP-RNA** example where one reference structure and multiple predicted structures are available.
        """)
    st.markdown("""---""")
    st.markdown("""
    
    ## Local installation
    
    The tool is available on [GitHub](https://github.com/EvryRNA/rnadvisor2) and can be installed locally. 
    A docker image is also available to build locally the webserver.
    
    You can also directly use the [RNAdvisor](https://github.com/EvryRNA/rnadvisor) tool with command line.""")

help_page()