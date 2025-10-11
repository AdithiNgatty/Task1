import React, { useEffect, useState } from "react";
import API from "../api";
import { useNavigate } from "react-router-dom";

export default function Profile() {
  const [user, setUser] = useState(null);
  const [msg, setMsg] = useState("Loading...");
  const navigate = useNavigate();

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await API.get("/me");
        // backend returns UserOut (username, email)
        setUser(res.data);
        setMsg("");
      } catch (err) {
        console.error("Profile error:", err);
        // token missing/invalid or other
        let detail = "Please log in to access profile.";
        if (err.response?.status === 401) {
          detail = err.response?.data?.detail || "Unauthorized. Please login.";
        } else if (err.response?.data?.detail) {
          detail = err.response.data.detail;
        }
        setMsg(detail);
        // optional: redirect to login after short delay
        setTimeout(() => navigate("/login"), 1000);
      }
    };
    fetchProfile();
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  return (
    <div>
      <h2>Profile</h2>

      {user ? (
        <>
          <p><strong>Username:</strong> {user.username}</p>
          <p><strong>Email:</strong> {user.email}</p>
          <button onClick={handleLogout}>Logout</button>
        </>
      ) : (
        <div className="message error">{msg}</div>
      )}
    </div>
  );
}
