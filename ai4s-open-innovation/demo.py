from pathlib import Path
import json
import pandas as pd
import streamlit as st

st.set_page_config(page_title='Phenotype Response Copilot', layout='wide')
st.title('Phenotype Response Copilot')
st.caption('AI4S Open Innovation — research prototype')
st.markdown('A reproducible phenotype-analysis pipeline on public RxRx1 microscopy embeddings. It tests whether biological perturbation signal can generalize across experimental batches.')
metrics_path = Path('artifacts/metrics.json')
pred_path = Path('artifacts/predictions.csv')
if not metrics_path.exists() or not pred_path.exists():
    st.warning('Run download_data.py and baseline.py first.')
    st.stop()
m = json.loads(metrics_path.read_text())
c1,c2,c3,c4 = st.columns(4)
c1.metric('Held-out experiment', m['held_out_experiment'])
c2.metric('Test samples', f"{m['n_test']:,}")
c3.metric('Phenotype classes', f"{m['n_classes_train']:,}")
c4.metric('Top-1 accuracy', f"{100*m['accuracy']:.2f}%")
df = pd.read_csv(pred_path)
st.subheader('Prediction audit')
st.dataframe(df.head(200), use_container_width=True)
st.info('Research use only. Not for diagnosis or clinical decision-making.')
