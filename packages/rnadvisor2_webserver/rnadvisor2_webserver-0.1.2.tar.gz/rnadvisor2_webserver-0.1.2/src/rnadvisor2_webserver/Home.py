import streamlit as st
from importlib.resources import files
import base64

PREFIX_IMG = files("rnadvisor2_webserver.img.home")


def get_base64_gif(path: str, width: int):
    with open(path, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data).decode()
    return f'<img src="data:image/gif;base64,{encoded}" style="width:{width}px;display: block; margin-left: auto; margin-right: auto;" />'

def home_page():
    st.set_page_config(
        page_title="RNAdvisor 2",
        layout="wide",
    )
    st.write("# RNAdvisor 2")
    left_col, right_col = st.columns(2)
    left_col.image(PREFIX_IMG.joinpath("rnadvisor2.png"))

    right_col.markdown("### A tool to compute RNA 3D structure quality metrics")
    right_col.markdown(
        "**RNAdvisor 2** is a wrapper tool that gathers available metrics and scoring "
        "functions to assess RNA 3D structures quality."
    )
    right_col.markdown(
        "It is designed with Docker to ensure reproducibility and ease of use. "
    )
    right_col.markdown(
        "Any user can submit RNA 3D structures in .pdb format to get access to "
        "quality assessment metrics and scoring functions depending on what they want to evaluate."
    )
    right_col.markdown(
        "**This website is free and open to all users and there is no login requirement.**"
    )
    st.markdown("---")
    st.markdown(
        """
        ## Metrics
        Metrics assess structural quality of an RNA 3D structure given a reference native structure.
        The assessment can be made considering different aspects of the structure.
        """
    )
    left_col, right_col = st.columns(2)
    left_col.markdown(
        """
        ### General metrics
        General metrics will consider the differences in terms of general structural features.
        """
    )
    left_col.markdown(
        """
        #### RMSD
          RMSD stands for the Root Mean Square Deviation of two molecules. 
         It computes the mean Euclidean distances of the aligned atoms after superimposition. 
        """
    )
    with left_col.expander("More details"):
        st.markdown(
            r"""
                The alignment centers and rotates the two molecules using the Kabsch algorithm.
                $$
                RMSD(X, Y) = \min{(\sqrt{\frac{\sum_{i=1}^{N} (X_i - R Y_{i})}{N}})}
                $$
                with $R$ a rotation matrix.
                """
        )
        col1, col2, col3 = st.columns([1, 1, 1])
        col2.link_button("Code link", "https://github.com/RNA-Puzzles/RNA_assessment")
    left_col.markdown(
        r"""
        #### εRMSD
        εRMSD is an improved RMSD that tries to solve one of the main issues of RMSD: 
        the lack of reliable information about the differences in the base interaction network. """
    )
    with left_col.expander("More details"):
        st.markdown(
            r"""
    It uses a specific molecular representation of the bases, with the local 
    coordinate system in the center of six-membered rings. 
    The relative orientation and positions between nucleobases can thus be defined by a vector $r$, 
    in cylindrical coordinates $\rho$, $\theta$ and $z$. 
    This coordinate system defines almost all base-stacking and base-pairing interactions 
    in a well-defined ellipsoidal shell. 
    The anisotropic position vector is then defined as: 
$$
\tilde{r} = (\frac{r_x}{a},\frac{r_y}{a}, \frac{r_z}{b}) = (\frac{\rho}{a} \cos{\theta}, \frac{\rho}{a} \sin{\theta}, \frac{z}{b})
$$

This provides information about the relative base arrangement, enabling the definition of a RMSD-like metrics: 

$$
\epsilon \text{RMSD}(X,Y) = \sqrt{\frac{1}{N} \sum_{i,j} | G(\tilde{r}^X_{ij}) - G(\tilde{r}^Y_{ij})   |^2}
$$

with $\tilde{r}^X_{ij}$ is the $i$th base of structure X paired with the $j$th pair of reference structure Y. 
$G$ is a function that tries to avoid the significant deviation in distant pairs. 

Using a $\tilde{r}_{cutoff}$ value for the distance would bring discontinuity in the metric function, 
that is why they ended up with the $G$ function defined by: 
$$
G(\tilde{r}) = \begin{pmatrix}
sin(\gamma \tilde{r}) \frac{\tilde{r}_x}{\tilde{r}} \\
sin(\gamma \tilde{r}) \frac{\tilde{r}_y}{\tilde{r}} \\
sin(\gamma \tilde{r}) \frac{\tilde{r}_z}{\tilde{r}} \\
1+cos(\gamma \tilde{r}) 
\end{pmatrix} \times \frac{\Theta(\tilde{r}_{cutoff} - \tilde{r})}{\gamma}
$$ 
with $\gamma = \frac{\pi}{\tilde{r}_{cutoff}}$ and $r_{cutoff}$ a constant equal to 2.4 after analysis. $\Theta$ is the Heaviside function. 

This metric considers nucleobases' relative distance and orientation because of the $\tilde{r}$ distance coordinate. 
It is close to the INF score discussed above while being a continuous function of the atomic coordinates. 
"""
        )
        col1, col2, col3 = st.columns([1, 1, 1])
        col2.link_button("Code link", "https://github.com/srnas/barnaba")
    right_col.markdown(get_base64_gif( PREFIX_IMG.joinpath("skeleton_rp24.gif"), width=500), unsafe_allow_html=True)
    left_col, right_col = st.columns(2)
    left_col.markdown(
        """
        ### Protein-based metrics
        General metrics will consider the differences in terms of general structural features.
        """
    )
    left_col.markdown(get_base64_gif(PREFIX_IMG.joinpath("8VA9_PROTEIN.gif"), width=300), unsafe_allow_html=True)
    left_col.markdown(
        r"""
        #### TM-score
        TM-score stands for Template Modeling score and is a widely used metric in the CASP competition. 
        Instead of using the RMSD that doesn't consider the residual alignment, the TM-score 
        considers both residual alignment coverage and distance normalization. """
    )
    with left_col.expander("More details"):
        st.markdown(
            r"""
        As the normalisation parameters are specific to proteins, 
        an adaptation of the TM-score was introduced, with the following  formula: 
    $$
    \text{TM-score}_{RNA} = \frac{1}{L} \sum_{i=1}^{L_{ali}} \frac{1}{1+(\frac {d_i}{d_0})^2}
    $$
    with $L$ the length of the target RNA, $L_{ali}$ the number of aligned nucleotides, and $d_i$ the distance between the $i-th$ aligned pair of residues. The scaling factor $d_0$ prevents the score from being dependent on the length of the RNA. It is defined as :
    $$
    d_0 = 0.6 \sqrt{L-0.5} - 2.5
    $$
        """
        )
        col1, col2, col3 = st.columns([1, 1, 1])
        col2.link_button("Code link", "https://zhanggroup.org/US-align/")
    left_col.markdown(
        r"""
        #### GDT-TS
        GDT-TS stands for the Global Distance Test Total Score and is derived from a method of alignment 
        of longest continuous sequences, LGA(Local-Global Alignment). 
        The Global Distance Test (GDT) is a metric that estimates the percent of residues that can 
        fit under a distance cutoff using different superimpositions. 
        """
    )
    with left_col.expander("More details"):
        st.markdown(
            r"""
    The GDT-TS is computed as the average over the threshold of 1, 2, 4 and 8 Å: 
$$
\text{GDT-TS} = \frac{P_1 + P_2 + P_4 + P_8}{4}
$$
where $P_d$ is the percent of residues from a candidate that can be superimposed with 
corresponding residues in the target structure under a distance cutoff of $d$ Å. 
It ranges from 0 (bad prediction) to 1 (perfect prediction). 
Random predictions tend to give a GDT\_TS score of around 0.2, 
while getting the rough topology of the molecule usually give a score around 0.5.  
    """
        )
        col1, col2, col3 = st.columns([1, 1, 1])
        col2.link_button("Code link", "https://zhanggroup.org/TM-score/")
    left_col.markdown(
        r"""
        #### CAD-score
        The CAD-score stands for the Contact-area Difference score and measures the structural similarity in 
        a contact-area difference-based function. 
        This metric is based on a residue-residue 
        contact area score to compare a structure to a reference. 
        """
    )

    with left_col.expander("More details"):
        st.markdown(
            r"""
    The CAD-score is defined with the set of all pairs of residues $(i,j)$, denoting G, 
    that have non-contact area $T_{(i,j)}$ in the target structure. 
    The contact area of the residue pairs $(i,j) \in G$ is described as $M_{(i,j)}$ for the 
    candidate structure. 
    The contact area difference (CAD) is thus defined as the absolute difference of contact 
    areas between the residues $(i,j)$ in target T and candidate structure M: 
$$
CAD_{(i,j)} = |T_{(i,j)} - M_{(i,j)} |
$$
A bounded value is used to prevent over and under-prediction of contact areas: 
$$
CAD_{(i,j)}^{bonded} = \min{(CAD_{(i,j)}, T_{(i,j)})}
$$
Then, the final CAD-score is computed as: 
$$
\text{CAD-score} = 1 - \frac{ \sum_{(i,j) \in G} CAD^{bonded}_{(i,j)} } {\sum_{(i,j) \in G} T_{(i,j)}}
$$
The CAD-score ranges between 0 and 1, where 1 means the prediction and the target are identical. 
    """
        )
        col1, col2, col3 = st.columns([1, 1, 1])
        col2.link_button("Code link", "https://github.com/kliment-olechnovic/voronota")
    left_col.markdown(
        r"""
        #### LDDT
        LDDT stands for the local distance difference test and assesses the interatomic distance 
       differences between a reference structure and a predicted one. 
       It does not require any superposition. """
    )
    with left_col.expander("More details"):
        st.markdown(
            r"""
    The LDDT considers all the pairs of atoms in the reference structure within a $R_0$ distance, 
    where $R_0$ (the inclusion radius, default value of 15 Å) is a predefined threshold. 
    The atom pairs define a set of distances $L$, which is used for a predicted model. 
    A distance in the prediction is preserved if, given a threshold, it is the same as 
    its corresponding distance in $L$. 
    The LDDT is thus derived using four different thresholds: 0.5 Å, 1 Å, 2 Å, and 4 Å. 
    LDDT is the average of four fractions of conserved distances within the four thresholds. 
In the literature, no clear mathematical formula has been given. We define mathematically the LDDT in our own words. 
Given the set of distances in the reference model (with the inclusion radius $R_0$), the set of atom pairs can be defined as:
$$
L = \{ d^{REF}_{i,j}  \mid  d^{REF}_{i,j} < R_0 \} 
$$ 
where $(i,j)$ are pairs of atoms of the structures and $d^{REF}_{i,j}$ their distance in the reference structure. 
The number of conserved distances within a threshold $t$ (in Å) in the prediction can be specified as:
$$
P_t = \frac{|\{ d^{PRED}_{i,j} \text{ where } |d^{PRED}_{i,j} - d^{REF}_{i,j}| < t  \}|}{|L|}
$$
where $d^{PRED}_{i,j}$ is the distance for the atom pair $(i,j)$ in the prediction and $d^{REF}_{i,j} \in L$. 
Finally, the LDDT can be described as:
$$
LDDT = \frac{P_{0.5} + P_{1} + P_{2} + P_{4}}{4}
$$

LDDT ranges between 0 and 1, where 1 means a perfect reconstruction of interatomic distances. 
     """
        )
        col1, col2, col3 = st.columns([1, 1, 1])
        col2.link_button(
            "Code link", "https://git.scicore.unibas.ch/schwede/openstructure"
        )
    right_col.markdown(
        """
        ### RNA-oriented metrics
        General metrics will consider the differences in terms of general structural features.
        """
    )
    right_col.markdown(get_base64_gif(PREFIX_IMG.joinpath("torsional_angles.png"), width=400), unsafe_allow_html=True)
    right_col.markdown(
        r"""
        #### P-value
        P-value assesses the probability that a given structure is better than that 
        expected by chance. 
        It is based on an empirical law relationship between mean RMSD and chain length. 
        """
    )
    with right_col.expander("More details"):
        st.markdown(
            r"""
    The original paper finds its law by generating decoy structures using replica 
    exchange discrete molecular dynamics simulation. 
    They then used the mean and standard deviation distribution of each RMSD and 
    derived an expression that relates the RMSD to chain length. 
    The relation they found is the following:
$$
\langle RMSD \rangle = a N^{(0.41)} - b
$$ 
where $N$ is the length of the chain, $a$ and $b$ are constants that depend on the provided 
secondary structure as inputs to the molecular dynamic simulation. 
The P-value is then computed as the RNA prediction significance from the Z-score, 
given a predicted structure that differs from an accepted structure by an RMSD of m: 
$$
\text{P-value} = \frac{1+erf(\frac{Z}{\sqrt{2}})}{2}
$$
where 
$$
Z = \frac{m- \langle RMSD \rangle}{\sigma_m}
$$ 
with $\sigma_m \approx 1.8 Å$

P-value expresses the non-randomness of RNA structure prediction. 
A P-value below 0.01 represents a successful prediction for RNAs between 35 and 161 nucleotides.
    """
        )
        col1, col2, col3 = st.columns([1, 1, 1])
        col2.link_button("Code link", "https://github.com/RNA-Puzzles/RNA_assessment")

    right_col.markdown(
        r"""
        #### INF
       INF stands for Interaction Network Fidelity and is a metric that considers the specific RNA structural 
       features such as helices or hairpins. 
       It considers two main interactions for RNA molecules: base-stacking and base-pairing. 
       """
    )
    with right_col.expander("More details"):
        st.markdown(
            r"""
    Using Leontis and Westhof nomenclature, each base interacts with one of three edges: 
    Watson-Crick edge, Hoogsten edge, and sugar edge. 
    The INF metric integrates different types of interactions in the scoring process. 
If we denote $S_m$ the different interactions of the candidate structure, and $S_r$ those of the reference solved structure, we can define the interactions of both sets as $TP = S_r \cap S_m$. It defines the true positives, while the false positives are expressed as $FP = S_m \backslash S_r$. The interactions present in $S_r$ but not in $S_m$ are the false negatives: $FN = S_r \backslash S_m$. The INF score is then defined as: 
$$
INF(A,B) = MCC(A,B)
$$
with $MCC$ the Matthews Correlation Coefficient: 
$$
MCC = \sqrt{PPV \times STY}
$$
The PPV denotes the specificity: 
$$PPV = \frac{|TP|}{|TP| + |FP|}$$ and the STY defines the sensitivity: 
$$STY = \frac{|TP|}{|TP| + |FN|}$$ 

When the predicted model reproduces exactly the reference interactions, $|TP| > 1$ and $FP = FN = 0$. The $MCC$ value equals 1, such as the INF score. On the other hand, if none of the interactions of the reference is reproduced in the predicted model, $|TP| = 0$, and the INF score equals 0. The INF score can be specific to base-pairing interactions (INF$_{bp}$), the base stacking interactions (INF$_{stack}$), or consider both (INF$_{all}$).
     """
        )
        col1, col2, col3 = st.columns([1, 1, 1])
        col2.link_button("Code link", "https://github.com/RNA-Puzzles/RNA_assessment")
    right_col.markdown(
        r"""
        #### DI
        DI stands for the Deformation Index and combines both the INF and RMSD metrics. 
        """
    )
    with right_col.expander("More details"):
        st.markdown(
            r"""
        INF score alone is not enough to assess RNA 3D structure quality. 
        RMSD, on the other hand, can't consider the local dissimilarity as it averages 
        the error through the entire structure. 
        DI is defined as: 
$$
DI(A,B) = \frac{RMSD(A,B)}{INF(A,B)}
$$ 
        """
        )
        col1, col2, col3 = st.columns([1, 1, 1])
        col2.link_button("Code link", "https://github.com/RNA-Puzzles/RNA_assessment")
    right_col.markdown(
        r"""
        #### MCQ
        MCQ stands for the Mean of Circular Quantities and is a metric that uses algebraic 
        and trigonometric space for the dissimilarity measure. 
        It considers a molecule 3D structure as a set of torsional angles. 
        """
    )
    with right_col.expander("More details"):
        st.markdown(
            r"""
    Each RNA residue is described by eight torsion angles: 
    the seven classic RNA torsion angles 
    ($\alpha$, $\beta$, $\gamma$, $\delta$, $\epsilon$, $\xi$ and $\chi$) and the sugar pucker 
    pseudorotation phase called $P$. 
    The $P$ torsion angle is used to define the ribose ring. 
    To compute similarity between trigonometric structure $S_T$ and $S_{T'}$, 
    it considers $2\pi$-periodical circular quantities. 
    To compare two circular quantities $t$ and $t'$, the difference is defined as:
$$
\text{diff}(t, t') = |\text{mod}(t) - \text{mod}(t')|
$$ 
with: 
$$
\text{mod}(t) = (t+2\pi) \quad \text{modulo } 2\pi
$$
Therefore, the distance between two angles $t$ and $t'$ is described as:
$$
\Delta(t, t') =   \left\{
    \begin{array}{lll}
         0 && \text{if t, t' undefined}  \\
        \pi &&  \text{if t or t' undefined} \\
        \min{(\text{diff}(t, t'), 2\pi-\text{diff}(t,t'))} && \text{otherwise}
     \end{array}
\right.
$$

The sum of differences of angles, $D_{sin}$ and $D_{cos}$, defined by:

$$
D_{sin} = \frac{1}{r|T|} \sum_{i=1}^{r} \sum_{j=1}^{|T|} \sin \Delta(t_{i,j}, t'_{i,j}) 
$$

$$
D_{cos} = \frac{1}{r|T|} \sum_{i=1}^{r} \sum_{j=1}^{|T|}   \cos \Delta(t_{i,j}, t'_{i,j})
$$

Finally, the overall distance between structures $S_T$ and $S_{T'}$ is given by: 
$$
MCQ(S_T, S_{T'}) = \arctan(D_{sin}, D_{cos})
$$

with $r$ the number of residues in $S \cap S'$ and $T$ the set of torsion angles. 
This metric is computed using the MCQ4Structures algorithm.  
The MCQ gives a global dissimilarity measure. 
One of the advantages of the MCQ score is the possibility to consider inputs of different forms. 
Indeed, as it uses trigonometric space, it is possible to have different types of representation 
for a 3D structure and thus compute the score. 
The other benefit is that it complements other metrics, giving higher scores for 
structures with common shapes. It doesn't require superimposition, leading to less computation. 
    """
        )
        col1, col2, col3 = st.columns([1, 1, 1])
        col2.link_button("Code link", "https://github.com/tzok/mcq4structures")
    st.markdown("---")
    st.markdown(
        """
        ## Scoring functions
        Scoring functions are used to evaluate the quality of an RNA 3D structure without a reference structure.
        Indeed, having a reference structure is not always possible, and predicting models require to 
        evaluate the quality of structures without a reference.
        """
    )
    st.markdown(get_base64_gif(PREFIX_IMG.joinpath("scoring_evaluation_0.png"), width=1500), unsafe_allow_html=True)
    left_col, right_col = st.columns(2)
    left_col.markdown(
        """
        ### Knowledge-based scoring functions
        Knowledge-based scoring functions are derived from a set of native structures. 
        It considers structures to create a quality measurement score. These potentials are
        said to be derived from Boltzmann formulations. They rely on a
        comparison with non-native base pair interactions, known as a
        reference state. 
        """
    )
    left_col.markdown(
        """
        #### RASP
        Ribonucleic Acids Statistical Potential (RASP) is a scoring function that evaluates the quality of RNA 3D structures.
        It is an all-atom knowledge-based potential. It uses a pairwise distance-dependent energy score. 
        """
    )
    with left_col.expander("More details"):
        st.markdown(
            r"""
           The scoring function was computed using:
$$
\Delta E_k^{ij}(d) = RT \ln(1 + M_k^{ij} \sigma)-RT \ln(1+M_k^{ij} \sigma \frac{f_k^{ij}(d)}{f_k^{xx}(d)})
$$
where $R$ is the gas constant and $T$ is the absolute temperature and $\sigma$ was set to 0.02.

$M_k^{ij}$ is the total number of interactions observed between atom types $i$ and $j$ below the maximum distance range threshold (20 Å) at a given value of topological factor ($k$), defined as:
$$
M_k^{ij} = \sum_{d=1}^{N} F_k^{ij}(d)
$$
$F_k^{ij}(d)$ is the absolute frequency of observations between atom types $i$ and $j$ at the distance $d$, and $N$ is the total number of distance classes defined. 
The topological factor $k$ between nucleotides $n$ and $m$ is defined by $k = |m-n|- 1$, where $n$ and $m$ correspond to the observed residue indexes in the RNA chain. 

$f_k^{ij}(d)$ is the relative frequency of interactions between atom types $i$ and $j$ at the distance class $d$ and sequence separation $k$, and it was defined as follows: 
$$
f_k^{ij} = \frac{F_k^{ij}}{M_k^{ij}}
$$
$f_k^{xx}(d)$ is the reference system and corresponds to the relative frequency of observations between any two atom types in the distance class $d$ with sequence separation $k$.
$$
f_k^{xx}(d) = \frac{\sum_{i=1}^C \sum_{j=1}^C F_k^{ij}(d)} {\sum_{i=1}^C \sum_{j=1}^C \sum_{d=1}^{N} F_k^{ij}(d)}
$$
where $C$ is the number of different atom types and $N$ is the number of distance classes.
Parameters of the energy score have been optimized with the same set of native structures used to derive the potentials. The critical parameters of the energy score are the distance-dependent descriptors of atom pairs, the sequence separation to account for local or non-local interactions, and the atom types. 
                """
        )
        col1, col2, col3 = st.columns([1, 1, 1])
        col2.link_button("Code link", "http://melolab.org/webrasp/download.php")
    left_col.markdown(
        r"""
        #### εSCORE
        The εSCORE was introduced with the εRMSD metric. 
        """
    )
    with left_col.expander("More details"):
        st.markdown(
            r"""
            It is based on the six-membered rings coordinate system, where each relative orientation between two 
            nucleobases is described with the $r$ vector. 
            It is defined as:
            $$
            \epsilon \text{SCORE} = \sum_{j,k} p(r_{j,k})
            $$
            with $p(r)$ the empirical probability distribution of nucleobases in the crystal structure of H. 
            The sum is used instead of the product to reduce the effect of low-count regions.
                """
        )
        col1, col2, col3 = st.columns([1, 1, 1])
        col2.link_button("Code link", "https://github.com/srnas/barnaba")
    left_col.markdown(
        r"""
        #### DFIRE-RNA
        DFIRE-RNA is an all-atom, distance-dependent, knowledge-based energy function. 
        """
    )
    with left_col.expander("More details"):
        st.markdown(
            r"""
            The DFIRE-RNA energy score is defined as follows: 
$$
F(r_{ij}|a_i, a_j) = -RT \ln{ \frac{N_{obs}(r_{ij}| a_i, a_j)}{ (\frac{r_{ij}}{r_{cut}})^{\alpha} \frac{\Delta r}{\Delta r_{cut}} N_{obs}(r_{cut} | a_i, a_j) } } 
$$

with $N_{obs}(r_{ij} | a_i, a_j)$ is the observed number of atomic pairs ($a_i$, $a_j$) within a distance $r_{ij}$. 
They used all 85 atom types, where each atom in a nucleotide is considered different.  
The bin width $\Delta r$ is equal to 0.7Å. The distance cutoff is set to 19Å, and the $\alpha$ is set to 1.61. 
They used a dataset of 405 non-redundant RNA molecules derived from the PDB. 
                """
        )
        col1, col2, col3 = st.columns([1, 1, 1])
        col2.link_button("Code link", "https://github.com/tcgriffith/dfire_rna")

        left_col.markdown(
            r"""
            #### rsRNASP
            rsRNASP is an all-atom pairwise-dependent knowledge base score. 
            It states that no statistical potential considers the range of residue interactions. 
            Thus, it integrates a separation between short, medium and long-range interactions into the scoring function.
            """
        )
        with left_col.expander("More details"):
            st.markdown(
                r"""
     A separation threshold $k_0$ was used to classify an interaction as short- or long-range. 
     The energy for a conformation C is given by: 
$$
\Delta E(S) = \sum_{k>2}^{k \leq k_0} \Delta E_{short}(i,j,r) + w \sum_{k>k_0} \Delta E_{long}(i,j,r) 
$$
where 
$$
\Delta E_{short}(i,j,r) = -k_B T \ln{\frac{P^{OBS}_{2< k \leq k_0}(i,j,r)}{P^{REF}_{2< k \leq k_0}(i,j,r)}   }
$$
and 
$$
\Delta E_{long}(i,j,r) = -k_B T \ln{\frac{P^{OBS}_{ k> k_0}(i,j,r)}{P^{REF}_{k > k_0}(i,j,r)}   }
$$
with $w$ the weight to balance the contribution of the long-range interactions. 

They used two reference states: the random-walk-chain and averaging to build the long-ranged 
and short-ranged potentials. The distance bin width was set to 0.3Å, and the distance cutoffs were 
set to 13Å and 24Å for short- and long-range interactions, respectively. 
                    """
            )
            col1, col2, col3 = st.columns([1, 1, 1])
            col2.link_button("Code link", "https://github.com/Tan-group/rsRNASP")
        right_col.markdown(
            r"""
            ### Deep learning approaches
            Deep learning approaches have been developed to infer RNA structural quality from a set of input features.
            They input different characteristics like chemical type or atom position. 
            They use available native conformations to learn a score without explicitly using a reference state. 
            The objective is an RMSD-like metric, meaning that the network learns atom deviation properties to 
            assess structure predictive quality. 
            The architecture is based on a neural network with either convolutional layers or graph neural networks.
            """
        )
        right_col.markdown(
            r"""
            #### RNA3DCNN
            They assume that an RNA molecule can be seen as a 3D image, and thus convolutional neural networks could 
            help infer information. 
            The method relies on the fact that each RNA molecule has a different global shape and similar local conformation
            """
        )
        with right_col.expander("More details"):
            st.markdown(
                r"""
                The RNA3DCNN uses as inputs a cube of local atoms and outputs an RMSD-based residue unfitness score. 
                The convolutional model outputs an unfitness score for each local cube of atoms that are then 
                summed up to give a global score to the structure. 
                A Cartesian coordinate centered at the $C_1'$ atom is implemented, 
                where all the atoms of a distance below 16Å are considered. 
                They create a grid of 32x32x32 Å, each comprising voxels of three channels: 
                occupation number, mass and charge of the present atoms. 
                The channels are inspired by the RGB channels used in images. 
                The model uses four 3D convolutional layers, with filters of size 8, 16, 32 and 64. 
                The output layer returns a unique value named the unfitness score. 
                332 non-redundant RNA molecules were extracted from the PDB, while 82 RNAs were used as validation sets.
                We did not include this scoring function in our tool, but it is available on GitHub.
                Indeed, we did not succeed in reproducing the results of the paper, and thus we decided not to include it in our tool.
                    """
            )
            col1, col2, col3 = st.columns([1, 1, 1])
            col2.link_button("Code link", "https://github.com/lijunRNA/RNA3DCNN")
        right_col.markdown(
            r"""
            #### ARES
            The Atomic Rotationally Equivariant Scorer (ARES) is a scoring function incorporating 
            only atomic coordinates and chemical element type as inputs.
            """
        )
        with right_col.expander("More details"):
            st.markdown(
                r"""
               It is trained with 18 RNA structures, augmented by 1000 decoys for each structure with FARFAR 2. 
               They used the equivariance property of specific neural networks, where rotation or 
               translation in the 3D space (and network inputs) results in the same transformation in the output. 
               The first layer of the network collects information about local properties 
               (like position and orientation), while the latter layers infer global information. 
               The network’s output is the RMSD, while the inputs use coordinates and chemical properties. 
               We tried to include it in our tool, but the model was too large to be included in the Docker image.
                    """
            )
            col1, col2, col3 = st.columns([1, 1, 1])
            col2.link_button("Code link", "https://zenodo.org/records/6893040")
        right_col.markdown(
            r"""
            #### TB-MCQ
            TB-MCQ stands for TorsionBERT-MCQ. 
            It uses predicted torsional angles from a language-based model to compute the MCQ 
            score with the inferred angles from a given structure.
            """
        )
        with right_col.expander("More details"):
            st.markdown(
                r"""
                To discriminate near-native structures in the torsional space, 
                we have derived a scoring function from our RNA-TorsionBERT model. 
                First, we have replicated a quality assessment metric that uses torsional angles features: 
                the mean of circular quantities (MCQ). 
                Then, we replaced the true torsional angles with the predicted angles from our model 
                to compute the MCQ over the near-native structure. 
                Therefore, the MCQ computation compares the prediction of our model angles with the angles 
                from the predicted non-native structures. 
                This MCQ now becomes a scoring function, as it only takes as input a structure without 
                any known native structure. 
                We named this scoring function TB-MCQ for TorsionBERT-MCQ. 
                 """
            )
            col1, col2, col3 = st.columns([1, 1, 1])
            col2.link_button("Code link", "https://zenodo.org/records/6893040")
            right_col.markdown(
                r"""
                #### LociPARSE
                lociPARSE is a deep learning model  that predicts the LDDT score of RNA 3D structures.
                """
            )
            with right_col.expander("More details"):
                st.markdown(
                    r"""
    lociPARSE consists of multiple IPA (Invariant Point Attention, an attention mechanism that applies to 3D geometry) 
    layers that process the input RNA 3D structure to refine nucleotide and pair features. 
    Following the IPA layers, a linear layer and a two-layer fully connected network (MLP) are used to estimate nucleotide-wise 
    Local Distance Difference Test (LDDT) scores, which are then aggregated to predict the global structural accuracy. 
    The model was trained on a dataset derived from trRosettaRNA containing 1,399 RNA targets and 51,763 structural models 
    generated by various RNA 3D structure prediction methods. 
    lociPARSE uses several input features, including the one-hot encoding of the nucleotide, its relative position in the sequence, the 
    sequential separation of nucleotide pairs (discretized into bins representing different interaction ranges), and the interatomic distances 
    between all pairs of $P$, $C_4'$, and glycosidic $N$ atoms, encoded using Gaussian radial basis functions. 
                     """
                )
                col1, col2, col3 = st.columns([1, 1, 1])
                col2.link_button("Code link", "https://github.com/Bhattacharya-Lab/lociPARSE")
                right_col.markdown(
                    r"""
                    #### PAMNet
        The Physics-Aware Multiplex Graph Neural Network (PAMNet) is a graph neural network (GNN) framework designed for accurate and efficient representation learning of 3D molecules across different sizes and types.
                    """
                )
                with right_col.expander("More details"):
                    st.markdown(
                        r"""
    Is is not specifically designed for RNA but can be applied to any 3D molecule.
    PAMNet represents each molecule as a two-layer multiplex graph, 
    distinguishing between local and non-local interactions based on principles from molecular mechanics. 
    It uses global and local message passing modules to update node embeddings, 
    incorporating geometric information such as pairwise distances and angles. 
    A fusion module with a two-step attention pooling process combines the updated embeddings for downstream tasks. 
     The input features for PAMNet vary depending on the task, but it uses atomic numbers (Z) as initial node features and encodes 
     pairwise distances and angles using basis functions. 
                         """
                    )
                    col1, col2, col3 = st.columns([1, 1, 1])
                    col2.link_button("Code link", "https://github.com/XieResearchGroup/Physics-aware-Multiplex-GNN")
    st.markdown("---")
    left_info_col, right_info_col = st.columns(2)
    left_info_col.markdown(
        f"""
        ### Authors
        Please feel free to contact us with any issues, comments, or questions.

        ##### Clément Bernard 

        - Email:  clement.bernard@univ-evry.fr or clementbernardd@gmail.com
        - GitHub: https://github.com/clementbernardd

        ##### Guillaume Postic

        - Email: guillaume.postic@universite-paris-saclay.fr

        ##### Sahar Ghannay

        - Email: sahar.ghannay@universite-paris-saclay.fr

        ##### Fariza Tahi 

        - Email: fariza.tahi@univ-evry.fr
        """,
        unsafe_allow_html=True,
    )

    right_info_col.markdown(
        """
        ### Funding

        - UDOPIA-ANR-20-THIA-0013
        - Labex DigiCosme (project ANR11LABEX0045DIGICOSME)
        - GENCI/IDRIS (grant AD011014250)
        - "Investissement d'Avenir" Idex ParisSaclay (ANR11IDEX000302)
         """
    )

    right_info_col.markdown(
        """
        ### License
        Apache License 2.0
        """
    )

    # write_st_end()


home_page()
