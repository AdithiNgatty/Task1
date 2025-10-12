import React, { useState } from "react";
import API from "../api";
import { useNavigate } from "react-router-dom";

export default function Signup() {
  const [form, setForm] = useState({ username: "", email: "", password: "" });
  const [otp, setOtp] = useState(""); // stores the entered OTP
  const [step, setStep] = useState(1); // 1 = signup form, 2 = otp verification
  const [msg, setMsg] = useState("");
  const [ok, setOk] = useState(false);
  const navigate = useNavigate();

  // -----------------------------------------------------
  // STEP 1: Signup Request → backend sends OTP to email
  // -----------------------------------------------------
  const handleSignupRequest = async (e) => {
    e.preventDefault();
    setMsg("");
    setOk(false);

    // simple validation
    if (!form.username || !form.email || !form.password) {
      setMsg("Please fill all fields.");
      return;
    }

    try {
      // send signup data to backend
      const res = await API.post("/signup-request", form);

      setOk(true);
      setMsg(res.data?.message || "OTP sent to your email. Please verify.");
      setStep(2); // move to next step: OTP verification
    } catch (err) {
      console.error("Signup request error:", err);
      let detail = "Signup failed.";
      if (err.response?.data?.detail) {
        detail = err.response.data.detail;
      }
      setMsg(detail);
    }
  };

  // -----------------------------------------------------
  // STEP 2: Verify OTP → backend creates user account
  // -----------------------------------------------------
  const handleOtpVerify = async (e) => {
    e.preventDefault();
    setMsg("");
    setOk(false);

    if (!otp) {
      setMsg("Please enter the OTP sent to your email.");
      return;
    }

    try {
      const res = await API.post("/signup-verify", {
        email: form.email,
        otp: otp,
      });

      setOk(true);
      setMsg(res.data?.message || "Account verified! Redirecting to login...");
      setTimeout(() => navigate("/login"), 1500);
    } catch (err) {
      console.error("OTP verification error:", err);
      let detail = "OTP verification failed.";
      if (err.response?.data?.detail) {
        detail = err.response.data.detail;
      }
      setMsg(detail);
    }
  };

  // -----------------------------------------------------
  // UI Rendering
  // -----------------------------------------------------
  return (
    <div style={{ maxWidth: "400px", margin: "0 auto", padding: "1rem" }}>
      <h2>Sign Up</h2>

      {/* Step 1: Signup Form */}
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
          <button type="submit">Send OTP</button>
        </form>
      )}

      {/* Step 2: OTP Verification */}
      {step === 2 && (
        <form onSubmit={handleOtpVerify}>
          <p>Enter the OTP sent to your email:</p>
          <input
            placeholder="Enter OTP"
            value={otp}
            onChange={(e) => setOtp(e.target.value)}
          />
          <button type="submit">Verify OTP</button>
          <button
            type="button"
            onClick={() => {
              setStep(1);
              setMsg("");
              setOk(false);
            }}
            style={{ marginLeft: "10px" }}
          >
            Edit Info
          </button>
        </form>
      )}

      {/* Message box */}
      {msg && (
        <div
          className={`message ${ok ? "success" : "error"}`}
          style={{
            marginTop: "1rem",
            color: ok ? "green" : "red",
            fontWeight: 500,
          }}
        >
          {msg}
        </div>
      )}
    </div>
  );
}
