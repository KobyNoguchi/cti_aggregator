export async function fetchVulnerabilities() {
  try {
    const response = await fetch("http://localhost:8000/api/vulnerabilities/");
    if (!response.ok) {
      throw new Error("Failed to fetch vulnerabilities");
    }
    return await response.json();
  } catch (error) {
    console.error("Error fetching vulnerabilities:", error);
    return [];
  }
}

