import React, { useState } from "react";
import api from "../api/api";

const MachineLearningPredicts = () => {
  const [formData, setFormData] = useState({
    age: 18,
    Medu: 2,
    Fedu: 2,
    traveltime: 1,
    studytime: 2,
    failures: 0,
    famrel: 4,
    freetime: 3,
    goout: 3,
    Dalc: 1,
    Walc: 2,
    health: 4,
    absences: 0,
    G1: 10,
    G2: 11,
    school_MS: 1,
    sex_M: 1,
    address_U: 1,
    famsize_LE3: 0,
    Pstatus_T: 1,
    Mjob_health: 0,
    Mjob_other: 1,
    Mjob_services: 0,
    Mjob_teacher: 0,
    Fjob_health: 0,
    Fjob_other: 1,
    Fjob_services: 0,
    Fjob_teacher: 0,
    reason_home: 0,
    reason_other: 0,
    reason_reputation: 1,
    guardian_mother: 1,
    guardian_other: 0,
    schoolsup_yes: 0,
    famsup_yes: 1,
    paid_yes: 0,
    activities_yes: 1,
    nursery_yes: 1,
    higher_yes: 1,
    internet_yes: 1,
    romantic_yes: 0,
  });

  const [prediction, setPrediction] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await api.post("/predict/ml", formData);
      setPrediction(res.data.prediction);
    } catch (err) {
      console.error(err);
      alert("Greška prilikom slanja zahtjeva.");
    }
  };

  return (
    <div>
      <h2>🔍 Machine Learning Predikcija</h2>
      <button onClick={handleSubmit}>Pošalji podatke</button>
      {prediction !== null && (
        <p>
          <strong>Predikcija (G3):</strong> {prediction}
        </p>
      )}
    </div>
  );
};

export default MachineLearningPredicts;
