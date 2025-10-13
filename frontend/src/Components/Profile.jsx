import React, { useEffect, useState } from "react";
import API from "../api";
import { useNavigate } from "react-router-dom";

export default function Profile() {
  const [user, setUser] = useState(null);
  const [bio, setBio] = useState("");
  const [editing, setEditing] = useState(false);
  const [msg, setMsg] = useState("Loading...");
  const navigate = useNavigate();

  // -------------------- Fetch user profile --------------------
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await API.get("/me"); // /me returns username, email, bio
        setUser(res.data);
        setBio(res.data.bio || "");
        setMsg("");
      } catch (err) {
        console.error("Profile error:", err);
        let detail = "Please log in to access profile.";
        if (err.response?.status === 401) {
          detail = err.response?.data?.detail || "Unauthorized. Please login.";
        } else if (err.response?.data?.detail) {
          detail = err.response.data.detail;
        }
        setMsg(detail);
        setTimeout(() => navigate("/login"), 1000);
      }
    };
    fetchProfile();
  }, [navigate]);

  // -------------------- Logout --------------------
  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  // -------------------- Save or Update Bio --------------------
  const handleSaveBio = async () => {
    try {
      if (!bio.trim()) {
        alert("Bio cannot be empty!");
        return;
      }

      const endpoint = user?.bio ? "/me/bio" : "/me/bio"; // same endpoint for create/update
      const method = user?.bio ? "put" : "post";
      const res = await API[method](endpoint, { bio });
      setUser(res.data);
      setEditing(false);
      setMsg("Bio saved successfully!");
      setTimeout(() => setMsg(""), 2000);
    } catch (err) {
      console.error("Error saving bio:", err);
      setMsg("Failed to save bio.");
    }
  };

  // -------------------- Delete Bio --------------------
  const handleDeleteBio = async () => {
    try {
      await API.delete("/me/bio");
      setBio("");
      setUser({ ...user, bio: "" });
      setMsg("Bio deleted.");
      setTimeout(() => setMsg(""), 2000);
    } catch (err) {
      console.error("Error deleting bio:", err);
      setMsg("Failed to delete bio.");
    }
  };

  // -------------------- UI --------------------
  return (
    <div style={{ maxWidth: "500px", margin: "2rem auto", textAlign: "left" }}>
      <h2>Profile</h2>

      {user ? (
        <>
          <p><strong>Username:</strong> {user.username}</p>
          <p><strong>Email:</strong> {user.email}</p>

          <div style={{ marginTop: "1rem" }}>
            <h3>Bio</h3>
            {!editing ? (
              <>
                <p>{user.bio ? user.bio : "No bio added yet."}</p>
                <button onClick={() => setEditing(true)}>Edit Bio</button>
                {user.bio && (
                  <button
                    onClick={handleDeleteBio}
                    style={{ marginLeft: "10px", color: "red" }}
                  >
                    Delete Bio
                  </button>
                )}
              </>
            ) : (
              <>
                <textarea
                  rows="5"
                  value={bio}
                  onChange={(e) => setBio(e.target.value)}
                  placeholder="Write something about yourself..."
                  style={{ width: "100%", padding: "10px", marginBottom: "10px" }}
                />
                <button onClick={handleSaveBio}>Save</button>
                <button
                  onClick={() => {
                    setEditing(false);
                    setBio(user.bio || "");
                  }}
                  style={{ marginLeft: "10px" }}
                >
                  Cancel
                </button>
              </>
            )}
          </div>

          <button
            onClick={handleLogout}
            style={{ marginTop: "2rem", background: "gray", color: "white" }}
          >
            Logout
          </button>
        </>
      ) : (
        <div className="message error">{msg}</div>
      )}

      {msg && <p style={{ color: "green", marginTop: "10px" }}>{msg}</p>}
    </div>
  );
}
