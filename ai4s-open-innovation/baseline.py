from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler

DATA = Path('data')
ART = Path('artifacts')
ART.mkdir(exist_ok=True)

def first_csv(folder):
    files = list(folder.rglob('*.csv'))
    if not files:
        raise FileNotFoundError(f'No CSV found under {folder}')
    return files[0]

meta = pd.read_csv(first_csv(DATA / 'metadata'))
emb = pd.read_csv(first_csv(DATA / 'embeddings'))

candidate_keys = [['experiment','plate','well','site'], ['id_code']]
join_keys = next((k for k in candidate_keys if all(c in meta.columns and c in emb.columns for c in k)), None)
if join_keys is None:
    shared = [c for c in meta.columns if c in emb.columns]
    if not shared:
        raise RuntimeError('Could not infer join keys')
    join_keys = shared[:1]

df = meta.merge(emb, on=join_keys, how='inner')
label_col = next((c for c in ['sirna','siRNA','perturbation','target'] if c in df.columns), None)
exp_col = next((c for c in ['experiment','experiment_id'] if c in df.columns), None)
if label_col is None or exp_col is None:
    raise RuntimeError(f'Expected perturbation and experiment columns. Got: {list(df.columns)[:40]}')

meta_cols = set(meta.columns) | set(join_keys)
features = [c for c in emb.columns if c not in meta_cols and c in df.columns and pd.api.types.is_numeric_dtype(df[c])]
if not features:
    features = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c]) and c not in set(meta.columns)]

df = df.dropna(subset=[label_col, exp_col]).reset_index(drop=True)
experiments = sorted(df[exp_col].astype(str).unique())
test_exp = experiments[-1]
train = df[df[exp_col].astype(str) != test_exp].copy()
test = df[df[exp_col].astype(str) == test_exp].copy()

scaler = StandardScaler()
Xtr = scaler.fit_transform(train[features].astype(float))
Xte = scaler.transform(test[features].astype(float))
train_labels = train[label_col].astype(str).to_numpy()
test_labels = test[label_col].astype(str).to_numpy()
classes = np.unique(train_labels)
prototypes = np.vstack([Xtr[train_labels == c].mean(axis=0) for c in classes])
prototypes /= np.linalg.norm(prototypes, axis=1, keepdims=True) + 1e-12
Xte /= np.linalg.norm(Xte, axis=1, keepdims=True) + 1e-12
scores = Xte @ prototypes.T
top = np.argmax(scores, axis=1)
pred = classes[top]
acc = float(accuracy_score(test_labels, pred))
part = np.partition(scores, -2, axis=1)
margin = part[:, -1] - part[:, -2]
metrics = {'dataset':'RxRx1','task':'cross-experiment perturbation prototype classification','held_out_experiment':test_exp,'n_train':int(len(train)),'n_test':int(len(test)),'n_features':int(len(features)),'n_classes_train':int(len(classes)),'accuracy':acc,'note':'V0 research baseline'}
(ART / 'metrics.json').write_text(json.dumps(metrics, indent=2))
out = test[join_keys + [exp_col, label_col]].copy()
out['prediction'] = pred
out['confidence_margin'] = margin
out.to_csv(ART / 'predictions.csv', index=False)
np.savez_compressed(ART / 'prototypes.npz', classes=classes, prototypes=prototypes)
print(json.dumps(metrics, indent=2))
