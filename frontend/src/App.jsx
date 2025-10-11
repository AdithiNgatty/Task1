import React from "react";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import Signup from "./Components/Signup";
import Login from "./Components/Login";
import Profile from "./Components/Profile";

export default function App() {
  return (
    <BrowserRouter>
      <div className="nav">
        <Link to="/signup">Sign Up</Link>
        <Link to="/login">Login</Link>
        <Link to="/profile">Profile</Link>
      </div>

      <main className="container">
        <Routes>
          <Route path="/" element={<Signup />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/login" element={<Login />} />
          <Route path="/profile" element={<Profile />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}
