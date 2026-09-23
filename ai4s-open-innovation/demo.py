import pandas as pd
import streamlit as st

st.set_page_config(page_title="Phenotype Response Copilot", layout="wide")

st.title("Phenotype Response Copilot")
st.caption("AI4S Open Innovation — reproducible cellular phenotype analysis")

st.markdown("""
This research prototype uses public **RxRx1** microscopy embeddings to recover
perturbation-specific cellular phenotypes across experiments. V2 combines
**well-level aggregation** with **same-cell-type prototype matching**.
""")

c1,c2,c3 = st.columns(3)
c1.metric("Mean accuracy", "97.29%", "+4.94 pp vs V0")
c2.metric("Median accuracy", "98.46%")
c3.metric("Experiments", "51")

st.subheader("Hard-case improvement")
hard = pd.DataFrame({
    "Experiment": ["U2OS-04", "U2OS-05"],
    "V0": [42.29, 59.71],
    "V2": [80.19, 92.38],
})
st.dataframe(hard, use_container_width=True, hide_index=True)

st.subheader("How the system works")
st.markdown("""
1. Convert microscopy data to embeddings.
2. Aggregate image sites to the **well level**.
3. Hold out one complete experiment.
4. Build perturbation prototypes only from the **same cell type**.
5. Classify held-out wells by cosine similarity.
6. Save auditable experiment-level results.

**Organ-on-chip transfer path:** microscopy → embeddings → experimental-unit aggregation →
context-aware phenotype comparison → treatment-response ranking → experiment report.
""")

st.subheader("Validation")
st.markdown("""
The reported V2 result uses **leave-one-experiment-out validation across 51 experiments**.
The benchmark is intentionally experiment-level rather than a random row split, making it
a stricter test of cross-experiment robustness.
""")

st.subheader("Reproducibility")
st.code(
    "git clone https://github.com/hgreco85/HG.git\n"
    "cd HG/ai4s-open-innovation\n"
    "pip install -r requirements.txt\n"
    "python download_data.py\n"
    "python v2_celltype.py",
    language="bash",
)

st.link_button(
    "Open public repository",
    "https://github.com/hgreco85/HG/tree/main/ai4s-open-innovation",
)

st.info(
    "Research prototype only. Current validation uses RxRx1 and is not a clinical "
    "or organ-on-chip performance claim."
)
