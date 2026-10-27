"""
Treniranje modela za predviđanje završne ocjene (G3) — UCI Student Performance.

Ispravlja tri problema iz prve verzije:
  1. Predprocesiranje (one-hot + skaliranje) sprema se ZAJEDNO s modelom,
     pa API dobiva iste transformacije kao pri treniranju.
  2. Dva scenarija: s ocjenama G1/G2 i bez njih (G1/G2 su gotovo isto što i G3).
  3. Grafovi i metrike računaju se SAMO na testnom skupu.

Pokretanje (iz mape backend/):
    python train.py --data data/student-por.csv
"""
import argparse
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

TARGET = "G3"
SEED = 42

# Scenarij -> stupci koje izbacujemo iz značajki
SCENARIJI = {
    "s_ocjenama": [],            # koristi G1 i G2 (lakši zadatak)
    "bez_ocjena": ["G1", "G2"],  # rana predikcija, prije ikakvih ocjena
}


def napravi_preprocesor(X: pd.DataFrame) -> ColumnTransformer:
    numericke = X.select_dtypes(include="number").columns.tolist()
    kategorijske = [c for c in X.columns if c not in numericke]
    return ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), kategorijske),
        ("num", StandardScaler(), numericke),
    ])


def metrike(y_true, y_pred) -> dict:
    return {
        "MAE": round(float(mean_absolute_error(y_true, y_pred)), 3),
        "RMSE": round(float(np.sqrt(mean_squared_error(y_true, y_pred))), 3),
        "R2": round(float(r2_score(y_true, y_pred)), 3),
    }


def treniraj_dl(X_train, y_train):
    # Import ovdje da se train.py može koristiti i bez TensorFlowa za RF dio
    from tensorflow import keras

    keras.utils.set_random_seed(SEED)
    model = keras.Sequential([
        keras.Input(shape=(X_train.shape[1],)),
        keras.layers.Dense(64, activation="relu"),
        keras.layers.Dropout(0.2),
        keras.layers.Dense(32, activation="relu"),
        keras.layers.Dense(1),
    ])
    model.compile(optimizer="adam", loss="mse", metrics=["mae"])
    model.fit(
        X_train, y_train,
        epochs=300, batch_size=16, validation_split=0.2, verbose=0,
        callbacks=[keras.callbacks.EarlyStopping(patience=20, restore_best_weights=True)],
    )
    return model


def main(data_path: str, out_dir: str):
    df = pd.read_csv(data_path, sep=";")
    df.columns = df.columns.str.strip()
    out = Path(out_dir)
    svi_rezultati = {}

    for scenarij, izbaci in SCENARIJI.items():
        X = df.drop(columns=[TARGET] + izbaci)
        y = df[TARGET].astype(float)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=SEED
        )

        # --- Random Forest: preprocesor + model u jednom Pipelineu ---
        rf = Pipeline([
            ("prep", napravi_preprocesor(X_train)),
            ("model", RandomForestRegressor(n_estimators=300, random_state=SEED, n_jobs=-1)),
        ])
        rf.fit(X_train, y_train)
        pred_rf = rf.predict(X_test)

        # --- Neuronska mreža: preprocesor se sprema zasebno (Keras nije sklearn) ---
        prep_dl = napravi_preprocesor(X_train).fit(X_train)
        dl = treniraj_dl(prep_dl.transform(X_train).astype("float32"), y_train.values)
        pred_dl = dl.predict(prep_dl.transform(X_test).astype("float32"), verbose=0).ravel()

        # --- Baseline: uvijek predvidi prosjek train skupa ---
        pred_base = np.full(len(y_test), y_train.mean())

        # --- Spremanje ---
        mapa = out / scenarij
        mapa.mkdir(parents=True, exist_ok=True)
        joblib.dump(rf, mapa / "rf_pipeline.joblib")
        joblib.dump(prep_dl, mapa / "dl_preprocessor.joblib")
        dl.save(mapa / "dl_model.keras")

        pd.DataFrame({
            "y_true": y_test.values, "rf": pred_rf, "dl": pred_dl,
        }).to_csv(mapa / "test_predictions.csv", index=False)

        svi_rezultati[scenarij] = {
            "features": X.columns.tolist(),
            "n_train": len(X_train),
            "n_test": len(X_test),
            "baseline": metrike(y_test, pred_base),
            "rf": metrike(y_test, pred_rf),
            "dl": metrike(y_test, pred_dl),
        }
        print(f"[{scenarij}] baseline={svi_rezultati[scenarij]['baseline']}")
        print(f"[{scenarij}] RF={svi_rezultati[scenarij]['rf']}")
        print(f"[{scenarij}] DL={svi_rezultati[scenarij]['dl']}")

    with open(out / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(svi_rezultati, f, indent=2, ensure_ascii=False)
    print(f"\nModeli i metrike spremljeni u '{out}/'")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--data", default="data/student-por.csv")
    p.add_argument("--out", default="models")
    a = p.parse_args()
    main(a.data, a.out)
