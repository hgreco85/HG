import pandas as pd
import streamlit as st

st.set_page_config(page_title="Phenotype Response Copilot", layout="wide")
st.title("Phenotype Response Copilot")
st.caption("AI4S Open Innovation — reproducible cellular phenotype analysis")

st.markdown("""
This research prototype uses public **RxRx1** microscopy embeddings to recover
perturbation-specific cellular phenotypes across experiments. The current champion,
**V7 Nested Blend**, combines RAW and OAS-whitened prototype similarities with a
blend weight selected only inside the training folds.
""")

c1,c2,c3 = st.columns(3)
c1.metric("Mean accuracy", "97.49%", "+0.21 pp vs V2")
c2.metric("Median accuracy", "98.68%")
c3.metric("Experiments", "51")

st.subheader("Validated improvement")
summary = pd.DataFrame({
    "Metric": ["Mean accuracy", "Median accuracy", "Fold wins / ties / losses"],
    "V2": ["97.29%", "98.46%", "—"],
    "V7": ["97.49%", "98.68%", "35 / 11 / 5"],
})
st.dataframe(summary, use_container_width=True, hide_index=True)

st.subheader("Hard cases")
hard = pd.DataFrame({
    "Experiment": ["U2OS-04", "U2OS-05", "RPE-08"],
    "V2": [80.19, 92.38, 94.24],
    "V7": [82.06, 93.61, 94.97],
})
st.dataframe(hard, use_container_width=True, hide_index=True)

st.subheader("How V7 works")
st.markdown("""
1. Aggregate microscopy sites to the **well level**.
2. Hold out one complete experiment.
3. Train on the **same cell type** only.
4. Compute perturbation prototypes in RAW and OAS-whitened spaces.
5. Select the RAW/OAS blend weight using nested leave-one-experiment-out CV **inside training only**.
6. Freeze the weight and score the held-out experiment.
""")

st.subheader("Validation note")
st.markdown("""
The 97.49% result is an **internal RxRx1 validation metric**, not an official Kaggle
leaderboard score. AI4S Open Innovation is judged on impact, innovation, validation,
reproducibility and presentation.
""")

st.subheader("Organ-on-chip transfer path")
st.markdown("""
**Microscopy → embeddings → experimental-unit aggregation → context-aware phenotype comparison → treatment-response ranking → experiment report**

Current results are on RxRx1, so direct organ-on-chip validation remains future work.
""")

st.subheader("Reproducibility")
st.code(
    "git clone https://github.com/hgreco85/HG.git\n"
    "cd HG/ai4s-open-innovation\n"
    "pip install -r requirements.txt\n"
    "python download_data.py\n"
    "python v2_celltype.py\n"
    "python v7_nested_blend.py\n"
    "python experiment_engine.py",
    language="bash",
)

st.link_button(
    "Open public repository",
    "https://github.com/hgreco85/HG/tree/main/ai4s-open-innovation",
)

st.info("Research prototype only. Not a clinical or diagnostic system.")
