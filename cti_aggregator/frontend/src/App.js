import React, { useEffect, useState } from "react";
import axios from "axios";

const API_URL = "http://127.0.0.1:8000/api/vulnerabilities/";

function App() {
  const [data, setData] = useState([]);

  useEffect(() => {
    axios.get(API_URL)
      .then(response => {
        setData(response.data);
      })
      .catch(error => {
        console.error("Error fetching data:", error);
      });
  }, []); // ✅ Closing bracket and semicolon properly placed

  return (
    <div>
      <h1>Vulnerability Dashboard</h1>
      <ul>
        {data.map((vuln) => (
          <li key={vuln.id}>
            <strong>{vuln.cve_id}</strong>: {vuln.vulnerability_name} - {vuln.severity}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;

