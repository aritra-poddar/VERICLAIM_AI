import React, { useState } from "react";
import { Link } from "react-router-dom";
import "./Navbar.css";

const Navbar: React.FC = () => {
  const [menuOpen, setMenuOpen] = useState(false);

  const toggleMenu = () => setMenuOpen(!menuOpen);

  return (
    <nav className="navbar">
      <div className="navbar-logo">VeriClaim AI</div>

      <div className={`nav-links ${menuOpen ? "active" : ""}`}>
        <Link to="/" className="nav-link">Home</Link>
        <Link to="/about" className="nav-link">About</Link>
        <Link to="/dashboard" className="nav-link">Dashboard</Link>
        <Link to="/login" className="nav-link">Login</Link>
        <li><Link to="/claimSubmission">Submit Claim</Link></li>
      </div>

      <div className="menu-icon" onClick={toggleMenu}>
        ☰
      </div>
    </nav>
  );
};

export default Navbar;
