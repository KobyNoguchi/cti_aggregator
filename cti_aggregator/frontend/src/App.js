import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Dashboard from "./components/Dashboard";
import VulnerabilityTable from "./components/VulnerabilityTable";
import "./App.css";

function App() {
  return (
    <Router>
      <div className="app-container">
        {/* Banner */}
        <header className="banner">
          <h1>CTI Aggregator</h1>
        </header>
        
        {/* Main Content */}
        <div className="content-container">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/legacy" element={<VulnerabilityTable />} />
            {/* Add other routes as needed */}
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
