import pandas as pd
import streamlit as st

st.set_page_config(page_title="Phenotype Response Copilot", layout="wide")
st.title("Phenotype Response Copilot")
st.caption("AI4S Open Innovation — reproducible cellular phenotype analysis")

st.markdown("""
This research prototype uses public microscopy data to recover biological context across
experiments. The current champion, **V7 Nested Blend**, combines RAW and OAS-whitened
prototype similarities with the blend weight selected only inside training folds.
""")

c1,c2,c3 = st.columns(3)
c1.metric("RxRx1 mean accuracy", "97.49%", "+0.21 pp vs V2")
c2.metric("RxRx1 median accuracy", "98.68%")
c3.metric("Experiments", "51")

st.subheader("RxRx1 validation")
summary = pd.DataFrame({
    "Metric": ["Mean accuracy", "Median accuracy", "Fold wins / ties / losses"],
    "V2": ["97.29%", "98.46%", "—"],
    "V7": ["97.49%", "98.68%", "35 / 11 / 5"],
})
st.dataframe(summary, use_container_width=True, hide_index=True)

st.subheader("External gut-on-chip transfer check")
ooc = pd.DataFrame({
    "Metric": ["Balanced accuracy", "Accuracy", "Held-out days"],
    "Baseline": ["69.57%", "68.35%", "5"],
    "V7-style": ["70.90%", "70.26%", "5"],
})
st.dataframe(ooc, use_container_width=True, hide_index=True)
st.caption("95 brightfield images; 1 day improved, 4 unchanged, 0 worse. Preliminary transfer evidence.")

st.subheader("Selected hard cases")
hard = pd.DataFrame({
    "Experiment": ["U2OS-04", "U2OS-05", "RPE-08"],
    "V2": [80.19, 92.38, 94.24],
    "V7": [82.06, 93.61, 94.97],
})
st.dataframe(hard, use_container_width=True, hide_index=True)

st.subheader("How V7 works")
st.markdown("""
1. Aggregate microscopy sites to the experimental unit.
2. Hold out one complete experiment or day.
3. Fit preprocessing only on training data.
4. Compute prototype similarities in RAW and OAS-whitened spaces.
5. Select the blend weight using nested validation **inside training only**.
6. Freeze the choice and score the held-out unit.
""")

st.subheader("Validation note")
st.markdown("""
The reported percentages are **internal validation metrics**, not official Kaggle
leaderboard scores. The external gut-on-chip result is a small proof-of-transfer,
not a broad organ-on-chip performance claim.
""")

st.subheader("Reproducibility")
st.code(
    "git clone https://github.com/hgreco85/HG.git\n"
    "cd HG/ai4s-open-innovation\n"
    "pip install -r requirements.txt\n"
    "python download_data.py\n"
    "python v2_celltype.py\n"
    "python v7_nested_blend.py\n"
    "python experiment_engine.py\n"
    "python external_ooc_validation.py",
    language="bash",
)

st.link_button(
    "Open public repository",
    "https://github.com/hgreco85/HG/tree/main/ai4s-open-innovation",
)

st.info("Research prototype only. Not a clinical or diagnostic system.")
