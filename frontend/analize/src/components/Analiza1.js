import React, { useEffect, useState } from "react";
import axios from "axios";

const Analiza1 = () => {
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    axios.get("http://localhost:8000/data/summary")
      .then(res => setSummary(res.data))
      .catch(err => console.error("Greška:", err));
  }, []);

  if (!summary) return <p>Učitavanje...</p>;

  return (
    <div>
      <h2>📊 Brojčani podaci</h2>
      <ul>
        <li>Ukupno učenika: {summary.ukupno_ucenika}</li>
        <li>Prosječna ocjena (G3): {summary.prosjek_ocjena}</li>
        <li>Najčešća adresa: {summary.najcesca_adresa === "U" ? "Urban" : "Rural"}</li>
      </ul>

      <h3>📋 Primjer podataka (prvih 10):</h3>
      <table border="1" cellPadding="5">
        <thead>
          <tr>
            {Object.keys(summary.sample_podaci[0]).map((key) => (
              <th key={key}>{key}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {summary.sample_podaci.map((row, i) => (
            <tr key={i}>
              {Object.values(row).map((val, j) => (
                <td key={j}>{val}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Analiza1;
