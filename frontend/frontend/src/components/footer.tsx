import React from "react";
import "./Footer.css";

const Footer: React.FC = () => {
  return (
    <footer className="footer">
      <p>© {new Date().getFullYear()} VeriClaim AI | All rights reserved.</p>
    </footer>
  );
};

export default Footer;
