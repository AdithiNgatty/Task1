import React, { useState } from "react";
import API from "../api";
import { useNavigate } from "react-router-dom";

export default function Signup() {
  const [form, setForm] = useState({ username: "", email: "", password: "" });
  const [otp, setOtp] = useState(""); // new field for OTP
  const [step, setStep] = useState(1); // step 1 = signup request, step 2 = verify
  const [msg, setMsg] = useState("");
  const [ok, setOk] = useState(false);
  const navigate = useNavigate();

  // ------------------------------------------
  // Step 1: Send signup request → OTP emailed
  // ------------------------------------------
  const handleSignupRequest = async (e) => {
    e.preventDefault();
    setMsg("");
    setOk(false);

    if (!form.username || !form.email || !form.password) {
      setMsg("Please fill all fields.");
      return;
    }

    try {
      const fd = new FormData();
      fd.append("username", form.username);
      fd.append("email", form.email);
      fd.append("password", form.password);

      await API.post("/signup-request", fd);
      setOk(true);
      setMsg("OTP sent to your email. Please verify.");
      setStep(2); // move to OTP verification step
    } catch (err) {
      console.error("Signup request error:", err);
      let detail = "Signup failed.";
      if (err.response?.data?.detail) {
        detail = err.response.data.detail;
      }
      setMsg(detail);
    }
  };

  // ------------------------------------------
  // Step 2: Verify OTP → Create account
  // ------------------------------------------
  const handleOtpVerify = async (e) => {
    e.preventDefault();
    setMsg("");
    setOk(false);

    if (!otp) {
      setMsg("Please enter the OTP sent to your email.");
      return;
    }

    try {
      const fd = new FormData();
      fd.append("email", form.email);
      fd.append("otp", otp);

      await API.post("/signup-verify", fd);
      setOk(true);
      setMsg("Account verified! Redirecting to login...");
      setTimeout(() => navigate("/login"), 1400);
    } catch (err) {
      console.error("OTP verification error:", err);
      let detail = "OTP verification failed.";
      if (err.response?.data?.detail) {
        detail = err.response.data.detail;
      }
      setMsg(detail);
    }
  };

  // ------------------------------------------
  // UI Rendering
  // ------------------------------------------
  return (
    <div>
      <h2>Sign Up</h2>

      {step === 1 && (
        <form onSubmit={handleSignupRequest}>
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
      )}

      {step === 2 && (
        <form onSubmit={handleOtpVerify}>
          <p>Enter the OTP sent to your email:</p>
          <input
            placeholder="Enter OTP"
            value={otp}
            onChange={(e) => setOtp(e.target.value)}
          />
          <button type="submit">Verify OTP</button>
        </form>
      )}

      {msg && (
        <div className={`message ${ok ? "success" : "error"}`}>
          {msg}
        </div>
      )}
    </div>
  );
}
