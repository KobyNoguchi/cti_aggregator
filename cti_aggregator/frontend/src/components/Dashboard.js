import React, { useState } from 'react';
import VulnerabilityPanel from './VulnerabilityPanel';
import './Dashboard.css';

const Dashboard = () => {
  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>CTI Dashboard</h1>
      </div>
      
      <div className="dashboard-grid">
        <div className="dashboard-panel top-left">
          <div className="panel-header">
            <h2>Intelligence Feed</h2>
          </div>
          <div className="panel-content">
            <p>Feedly RSS Feed will be displayed here</p>
          </div>
        </div>
        
        <div className="dashboard-panel top-right">
          <div className="panel-header">
            <h2>CISA KEV</h2>
          </div>
          <div className="panel-content">
            <VulnerabilityPanel dataSource="cisa" />
          </div>
        </div>
        
        <div className="dashboard-panel bottom-left">
          <div className="panel-header">
            <h2>NVD Vulnerabilities</h2>
          </div>
          <div className="panel-content">
            <p>NVD data will be displayed here</p>
          </div>
        </div>
        
        <div className="dashboard-panel bottom-right">
          <div className="panel-header">
            <h2>Greynoise Intel</h2>
          </div>
          <div className="panel-content">
            <p>Greynoise data will be displayed here</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
