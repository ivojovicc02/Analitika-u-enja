import React, { useState } from "react";
import TabButton from "./TabButton";
import TabsContent from "./TabsContent";

const Tabs = () => {
  const [activeTab, setActiveTab] = useState("analiza1");

  return (
    <div>
      <div style={{ display: "flex", gap: "10px", marginBottom: "20px" }}>
        <TabButton
          label="Analiza 1"
          onClick={() => setActiveTab("analiza1")}
          isActive={activeTab === "analiza1"}
        />
        <TabButton
          label="Analiza 2"
          onClick={() => setActiveTab("analiza2")}
          isActive={activeTab === "analiza2"}
        />
        <TabButton
          label="Prediktivna"
          onClick={() => setActiveTab("predikcija")}
          isActive={activeTab === "predikcija"}
        />
      </div>
      <TabsContent activeTab={activeTab} />
    </div>
  );
};

export default Tabs;
