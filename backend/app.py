"""
FastAPI backend za predviđanje završne ocjene učenika (G3).

API prima SIROVE podatke o učeniku (spol, škola, ...), a one-hot kodiranje
i skaliranje radi spremljeni preprocesor. Ako se pošalju G1 i G2, koristi se
scenarij "s_ocjenama", inače "bez_ocjena".

Pokretanje (iz mape backend/, nakon `python train.py`):
    uvicorn app:app --reload
"""
import io
import json
import os
from pathlib import Path
from typing import Literal, Optional

import joblib
import matplotlib
matplotlib.use("Agg")  # crtanje bez GUI-ja (server)
import matplotlib.pyplot as plt
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

MODELS_DIR = Path(os.environ.get("MODELS_DIR", "models"))
DATA_PATH = Path(os.environ.get("DATA_PATH", "data/student-por.csv"))
FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "http://localhost:3000")
SCENARIJI = ("s_ocjenama", "bez_ocjena")

app = FastAPI(title="Analitika učenja API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ---------- Učitavanje modela pri startu ----------
def ucitaj_modele():
    from tensorflow import keras

    modeli = {}
    for s in SCENARIJI:
        mapa = MODELS_DIR / s
        modeli[s] = {
            "rf": joblib.load(mapa / "rf_pipeline.joblib"),
            "dl_prep": joblib.load(mapa / "dl_preprocessor.joblib"),
            "dl": keras.models.load_model(mapa / "dl_model.keras"),
        }
    return modeli


MODELI = ucitaj_modele()
METRIKE = json.loads((MODELS_DIR / "metrics.json").read_text(encoding="utf-8"))


# ---------- Ulazni podaci (sirovi stupci iz dataseta) ----------
DaNe = Literal["yes", "no"]
Posao = Literal["teacher", "health", "services", "at_home", "other"]


class StudentInput(BaseModel):
    school: Literal["GP", "MS"]
    sex: Literal["F", "M"]
    age: int = Field(ge=15, le=22)
    address: Literal["U", "R"]
    famsize: Literal["LE3", "GT3"]
    Pstatus: Literal["T", "A"]
    Medu: int = Field(ge=0, le=4)
    Fedu: int = Field(ge=0, le=4)
    Mjob: Posao
    Fjob: Posao
    reason: Literal["home", "reputation", "course", "other"]
    guardian: Literal["mother", "father", "other"]
    traveltime: int = Field(ge=1, le=4)
    studytime: int = Field(ge=1, le=4)
    failures: int = Field(ge=0, le=4)
    schoolsup: DaNe
    famsup: DaNe
    paid: DaNe
    activities: DaNe
    nursery: DaNe
    higher: DaNe
    internet: DaNe
    romantic: DaNe
    famrel: int = Field(ge=1, le=5)
    freetime: int = Field(ge=1, le=5)
    goout: int = Field(ge=1, le=5)
    Dalc: int = Field(ge=1, le=5)
    Walc: int = Field(ge=1, le=5)
    health: int = Field(ge=1, le=5)
    absences: int = Field(ge=0, le=93)
    G1: Optional[int] = Field(default=None, ge=0, le=20)
    G2: Optional[int] = Field(default=None, ge=0, le=20)


# ---------- Rute ----------
@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(student: StudentInput):
    podaci = student.model_dump()
    ima_ocjene = podaci["G1"] is not None and podaci["G2"] is not None
    scenarij = "s_ocjenama" if ima_ocjene else "bez_ocjena"

    stupci = METRIKE[scenarij]["features"]
    X = pd.DataFrame([podaci])[stupci]
    m = MODELI[scenarij]

    pred_rf = float(m["rf"].predict(X)[0])
    X_dl = m["dl_prep"].transform(X).astype("float32")
    pred_dl = float(m["dl"].predict(X_dl, verbose=0)[0][0])

    ogranici = lambda v: round(min(max(v, 0.0), 20.0), 2)  # ocjene su 0–20
    return {
        "scenarij": scenarij,
        "random_forest": ogranici(pred_rf),
        "neuronska_mreza": ogranici(pred_dl),
    }


@app.get("/metrics")
def metrics():
    """Metrike na testnom skupu za oba scenarija (uključujući baseline)."""
    return {s: {k: v for k, v in r.items() if k != "features"} for s, r in METRIKE.items()}


@app.get("/plot/{model}")
def plot(model: Literal["rf", "dl"], scenarij: Literal[SCENARIJI] = Query("bez_ocjena")):
    df = pd.read_csv(MODELS_DIR / scenarij / "test_predictions.csv")
    naziv = "Random Forest" if model == "rf" else "Neuronska mreža"
    boja = "royalblue" if model == "rf" else "darkorange"
    r2 = METRIKE[scenarij][model]["R2"]

    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(df["y_true"], df[model], alpha=0.7, color=boja, edgecolors="k")
    ax.plot([0, 20], [0, 20], "r--", label="Idealna predikcija")
    ax.set_xlabel("Stvarna ocjena (G3)")
    ax.set_ylabel("Predviđena ocjena (G3)")
    ax.set_title(f"{naziv} — {scenarij.replace('_', ' ')} (test skup, R² = {r2})")
    ax.legend()
    ax.grid(True)
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")


@app.get("/data/summary")
def summary():
    if not DATA_PATH.exists():
        raise HTTPException(404, f"Dataset nije pronađen: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH, sep=";")
    return {
        "ukupno_ucenika": len(df),
        "prosjek_ocjena": round(float(df["G3"].mean()), 2),
        "najcesca_adresa": df["address"].mode()[0],
        "sample_podaci": df.head(5).to_dict(orient="records"),
    }
