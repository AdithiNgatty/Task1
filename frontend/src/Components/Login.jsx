import React, { useState } from "react";
import API from "../api";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const [form, setForm] = useState({ username: "", password: "" });
  const [msg, setMsg] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setMsg("");

    if (!form.username || !form.password) {
      setMsg("Please enter username and password.");
      return;
    }

    try {
      // FastAPI's OAuth2PasswordRequestForm expects form-encoded data,
      // sending FormData works fine.
      const fd = new FormData();
      fd.append("username", form.username);
      fd.append("password", form.password);

      // Important: do NOT set Content-Type header manually here; axios will set multipart/form-data when using FormData.
      const res = await API.post("/login", fd);
      const token = res.data?.access_token;
      if (!token) throw new Error("No token returned");

      localStorage.setItem("token", token);
      setMsg("Login successful. Redirecting to profile...");
      setTimeout(() => navigate("/profile"), 800);
    } catch (err) {
      console.error("Login error:", err);
      let detail = "Login failed.";
      if (err.response?.data?.detail) {
        const d = err.response.data.detail;
        detail = Array.isArray(d) ? d.map(x => `${x.loc?.[1] || "field"}: ${x.msg}`).join(", ") : d;
      } else if (err.response?.data) {
        detail = JSON.stringify(err.response.data);
      }
      setMsg(detail);
    }
  };

  return (
    <div>
      <h2>Login</h2>
      <form onSubmit={handleLogin}>
        <input
          placeholder="Username"
          value={form.username}
          onChange={(e) => setForm({ ...form, username: e.target.value })}
        />
        <input
          placeholder="Password"
          type="password"
          value={form.password}
          onChange={(e) => setForm({ ...form, password: e.target.value })}
        />
        <button type="submit">Login</button>
      </form>

      {msg && <div className="message error">{msg}</div>}
    </div>
  );
}
