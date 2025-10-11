import React, { useState } from "react";
import API from "../api";
import { useNavigate } from "react-router-dom";

export default function Signup() {
  const [form, setForm] = useState({ username: "", email: "", password: "" });
  const [msg, setMsg] = useState("");
  const [ok, setOk] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMsg("");
    setOk(false);

    // quick client-side validation
    if (!form.username || !form.email || !form.password) {
      setMsg("Please fill all fields.");
      return;
    }

    try {
      // /signup expects JSON body
      await API.post("/signup", form);
      setOk(true);
      setMsg("User registered! Redirecting to login...");
      setTimeout(() => navigate("/login"), 1400);
    } catch (err) {
      console.error("Signup error:", err);
      // handle FastAPI validation or custom messages
      let detail = "Signup failed.";
      if (err.response?.data?.detail) {
        const d = err.response.data.detail;
        detail = Array.isArray(d) ? d.map(x => `${x.loc?.[1] || "field"}: ${x.msg}`).join(", ") : d;
      }
      setMsg(detail);
    }
  };

  return (
    <div>
      <h2>Sign Up</h2>
      <form onSubmit={handleSubmit}>
        <input
          placeholder="Username"
          value={form.username}
          onChange={(e) => setForm({ ...form, username: e.target.value })}
        />
        <input
          placeholder="Email"
          type="email"
          value={form.email}
          onChange={(e) => setForm({ ...form, email: e.target.value })}
        />
        <input
          placeholder="Password"
          type="password"
          value={form.password}
          onChange={(e) => setForm({ ...form, password: e.target.value })}
        />
        <button type="submit">Sign Up</button>
      </form>

      {msg && (
        <div className={`message ${ok ? "success" : "error"}`}>
          {msg}
        </div>
      )}
    </div>
  );
}
