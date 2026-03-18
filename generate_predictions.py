import pandas as pd
import numpy as np
import pickle
from keras.models import load_model

# === 1. Učitaj CSV s ispravnim delimiterom ===
df = pd.read_csv("data/student-por.csv", sep=';')
df.columns = df.columns.str.strip()  # ukloni višak razmaka

# === 2. Razdvoji X i y ===
y = df["G3"]
X = df.drop("G3", axis=1)

# === 3. One-hot encoding ===
X = pd.get_dummies(X)

# === 4. Učitaj modele ===
ml_model = pickle.load(open("backend/models/model_strojno.pkl", "rb"))
dl_model = load_model("backend/models/model_duboko.h5")

# === 5. Poravnaj stupce tako da odgovaraju modelu ===
X = X.reindex(columns=ml_model.feature_names_in_, fill_value=0)

# === 6. Napravi predikcije ===
y_pred_ml = ml_model.predict(X)

# Deep learning model traži float32 format
X_dl = X.astype(np.float32)
y_pred_dl = dl_model.predict(X_dl)

# === 7. Spremi predikcije i stvarne vrijednosti ===
np.save("data/y_test.npy", y)
np.save("data/y_pred_ml.npy", y_pred_ml)
np.save("data/y_pred_dl.npy", y_pred_dl)

print("✅ Uspješno spremljeno: y_test.npy, y_pred_ml.npy, y_pred_dl.npy")


