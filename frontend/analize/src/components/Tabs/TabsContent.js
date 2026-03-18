import React, { useEffect, useState } from "react";
import PredictionForm from "../PredictionForm";

const TabsContent = ({ activeTab }) => {
  const [summaryData, setSummaryData] = useState(null);

  useEffect(() => {
    if (activeTab === "analiza1") {
      fetch("http://127.0.0.1:8000/data/summary")
        .then((res) => res.json())
        .then((data) => setSummaryData(data))
        .catch((err) => console.error("Greška pri dohvatu podataka:", err));
    }
  }, [activeTab]);

  if (activeTab === "analiza1") {
    return (
      <div>
        <h2>Brojčana/Tablična analiza</h2>

        {summaryData ? (
          <>
            {/* STATISTIKE */}
            <div className="stats">
              <p>
                <strong>Ukupno učenika:</strong> {summaryData.ukupno_ucenika}
              </p>
              <p>
                <strong>Prosječna ocjena (G3):</strong>{" "}
                {summaryData.prosjek_ocjena}
              </p>
              <p>
                <strong>Najčešća adresa:</strong> {summaryData.najcesca_adresa}
              </p>
            </div>

            {/* TABELA */}
            <h3>Primjer podataka:</h3>

            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    {Object.keys(summaryData.sample_podaci[0]).map((key) => (
                      <th key={key}>{key}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {summaryData.sample_podaci.map((row, i) => (
                    <tr key={i}>
                      {Object.values(row).map((val, j) => (
                        <td key={j}>{val}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        ) : (
          <p>Učitavanje podataka...</p>
        )}
      </div>
    );
  }

  if (activeTab === "analiza2") {
    return (
      <div>
        <h2>Grafički prikaz (Analiza 2)</h2>
        <p>Usporedba stvarnih i predviđenih ocjena (G3) modelima:</p>

        <div className="charts">
          <div className="chart-card">
            <h4>Machine Learning (ML)</h4>
            <img src="http://localhost:8000/plot/ml" alt="ML graf" />
          </div>

          <div className="chart-card">
            <h4>Deep Learning (DL)</h4>
            <img src="http://localhost:8000/plot/dl" alt="DL graf" />
          </div>
        </div>
      </div>
    );
  }

  if (activeTab === "predikcija") {
    return (
      <div>
        <h2>Prediktivna analiza</h2>
        <PredictionForm />
      </div>
    );
  }

  return null;
};

export default TabsContent;
