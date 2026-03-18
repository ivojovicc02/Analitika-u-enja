import React, { useState } from "react";
import axios from "axios";

const PredictionForm = () => {
  const [formData, setFormData] = useState({
    age: 17,
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
    absences: 4,
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

  const [mlResult, setMlResult] = useState(null);
  const [dlResult, setDlResult] = useState(null);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: parseFloat(value) });
  };

  const handleSubmit = async () => {
    try {
      setError(null);

      const mlRes = await axios.post(
        "http://localhost:8000/predict/ml",
        formData
      );
      setMlResult(mlRes.data.prediction);

      const dlRes = await axios.post(
        "http://localhost:8000/predict/dl",
        formData
      );
      setDlResult(dlRes.data.prediction[0].toFixed(2)); // zaokruži na 2 decimale
    } catch (err) {
      setError("Greška pri predikciji: " + err.message);
    }
  };

  return (
    <div>
      <h3>Unesite podatke za predikciju</h3>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSubmit();
        }}
      >
        {Object.entries(formData).map(([key, value]) => (
          <div key={key} style={{ marginBottom: "10px" }}>
            <label>
              {key}:{" "}
              <input
                type="number"
                name={key}
                value={value}
                onChange={handleChange}
                step="any"
              />
            </label>
          </div>
        ))}
        <button type="submit">Predikcija</button>
      </form>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {mlResult !== null && (
        <p>
          <strong>ML predikcija:</strong> {mlResult}
        </p>
      )}
      {dlResult !== null && (
        <p>
          <strong>DL predikcija:</strong> {dlResult}
        </p>
      )}
    </div>
  );
};

export default PredictionForm;
