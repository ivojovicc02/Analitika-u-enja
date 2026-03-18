import React from "react";

const TabButton = ({ label, onClick, isActive }) => {
  return (
    <button
      onClick={onClick}
      style={{
        padding: "10px 20px",
        backgroundColor: isActive ? "#1976d2" : "#e0e0e0",
        color: isActive ? "white" : "black",
        border: "none",
        borderRadius: "5px",
        cursor: "pointer",
      }}
    >
      {label}
    </button>
  );
};

export default TabButton;
