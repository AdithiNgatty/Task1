import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:8000", // FastAPI backend
  // For some setups, you might use "http://127.0.0.1:8000"
});

// attach token automatically to every request if present
API.interceptors.request.use((req) => {
  const token = localStorage.getItem("token");
  if (token) {
    req.headers = req.headers || {};
    req.headers.Authorization = `Bearer ${token}`;
  }
  return req;
});

export default API;
