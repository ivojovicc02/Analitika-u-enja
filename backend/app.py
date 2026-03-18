from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, create_model
import numpy as np
import pickle
from keras.models import load_model
from utils.preprocessing import preprocess_input_ml, preprocess_input_dl
import io
import matplotlib.pyplot as plt
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from fastapi.responses import JSONResponse
import traceback


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # ili ["*"] za sve izvore
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Učitavanje modela
ml_model = pickle.load(open("models/model_strojno.pkl", "rb"))
dl_model = load_model("models/model_duboko.h5")

print("Značajke koje model očekuje:")
print(ml_model.feature_names_in_)


# Automatski ispis i kreiranje InputData klase
try:
    feature_names = ml_model.feature_names_in_
    print(f"\n✅ Model očekuje {len(feature_names)} značajki:\n")
    for i, f in enumerate(feature_names, 1):
        print(f"{i:2d}. {f}")
    print()

    # Dinamičko kreiranje Pydantic klase
    fields = {name: (float, ...) for name in feature_names}
    InputData = create_model('InputData', **fields)

except AttributeError:
    raise RuntimeError("❌ Model nije treniran na pandas DataFrame pa nema feature_names_in_. Dodaj značajke ručno.")
except Exception as e:
    raise RuntimeError(f"❌ Greška prilikom učitavanja značajki: {e}")


@app.post("/predict/ml")
def predict_ml(data: InputData):
    try:
        X = preprocess_input_ml(data)
        y_pred = ml_model.predict([X])
        return {"prediction": int(y_pred[0])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/dl")
def predict_dl(data: InputData):
    try:
        X = preprocess_input_dl(data)
        y_pred = dl_model.predict(np.array([X]))[0]
        return {"prediction": y_pred.tolist()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Dodane rute za grafove ---

def create_scatter_plot(y_true, y_pred, title, color):
    plt.figure(figsize=(8, 6))
    plt.scatter(y_true, y_pred, alpha=0.7, color=color, edgecolors='k')
    plt.plot([0, 20], [0, 20], color='red', linestyle='--')  # idealna linija
    plt.xlabel('Stvarne ocjene (G3)')
    plt.ylabel('Predviđene ocjene (G3)')
    plt.title(title)
    plt.grid(True)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return buf

@app.get("/plot/ml")
def plot_ml():
    try:
        y_true = np.load("data/y_test.npy")
        y_pred = np.load("data/y_pred_ml.npy")
        img_buf = create_scatter_plot(y_true, y_pred, "Stvarne vs. Predviđene ocjene – ML", "royalblue")
        return StreamingResponse(img_buf, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/plot/dl")
def plot_dl():
    try:
        y_true = np.load("data/y_test.npy")
        y_pred = np.load("data/y_pred_dl.npy")
        img_buf = create_scatter_plot(y_true, y_pred, "Stvarne vs. Predviđene ocjene – DL", "darkorange")
        return StreamingResponse(img_buf, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/data/summary")
def get_summary():
    try:
        df = pd.read_csv("data/student-por.csv", sep=";")
        ukupno_ucenika = len(df)
        prosjek_ocjena = round(df["G3"].mean(), 2)
        najcesca_adresa = df["address"].mode()[0]
        sample = df.head(5).to_dict(orient="records")

        return JSONResponse({
            "ukupno_ucenika": ukupno_ucenika,
            "prosjek_ocjena": prosjek_ocjena,
            "najcesca_adresa": najcesca_adresa,
            "sample_podaci": sample
        })
    except Exception as e:
        print("❌ Greska u /data/summary:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

