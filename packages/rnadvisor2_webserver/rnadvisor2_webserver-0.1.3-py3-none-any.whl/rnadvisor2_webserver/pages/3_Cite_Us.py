
import streamlit as st

def cite_us():
    st.markdown(
        """
        ### Cite Us
        If you use *RNAdvisor* in your research, please cite the following paper:
        - [Bernard C, Postic G, Ghannay S, Tahi F. 
        RNAdvisor: a comprehensive benchmarking tool for the measure and prediction of RNA 
        structural model quality. Brief Bioinform. 2024 Jan 22;25(2):bbae064. 
        doi: 10.1093/bib/bbae064. PMID: 38436560; PMCID: PMC10939302](https://academic.oup.com/bib/article/25/2/bbae064/7618078)
        """
    )
    st.markdown("---")
    st.markdown(
        """
        ### Contact Us
        Please feel free to contact us with any issues, comments, or questions.
        - **Email**: [fariza.tahi@univ-evry.fr](fariza.tahi@univ-evry.fr)
        """
    )
    st.markdown("---")
    st.markdown(
        """
        ### Authors
        - **Clément Bernard**: [Clément Bernard](clement.bernard@univ-evry.fr)
        - **Guillaume Postic**: [Guillaume Postic](guillaume.postic@universite-paris-saclay.fr)
        - **Sahar Ghannay**: [Sahar Ghannay](sahar.ghannay@universite-paris-saclay.fr)
        - **Fariza Tahi**: [Fariza Tahi](fariza.tahi@univ-evry.fr)
        """)
    st.markdown(
        """
        ### Local running
        If you want to run the application locally, you can clone the repository and run the following command: 
        """
    )
    st.link_button("Code link", "https://github.com/EvryRNA/rnadvisor")
    st.markdown("---")
cite_us()