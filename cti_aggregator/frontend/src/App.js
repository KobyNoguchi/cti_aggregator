import React from "react";
import VulnerabilityTable from "./components/VulnerabilityTable";
import "./App.css"; 

function App() {
  return (
    <div className="app-container">
      {/* Banner */}
      <header className="banner">
        <h1>CTI Aggregator</h1>
      </header>


      {/* Main Content */}
      <div className="content-container">
        <VulnerabilityTable />
      </div>
    </div>
  );
}

export default App;

