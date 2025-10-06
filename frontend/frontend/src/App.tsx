import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/navbar.tsx";
import Footer from "./components/footer.tsx";
import Home from "./pages/home.tsx"; 
import Login from "./pages/login.tsx";
import Dashboard from "./pages/dashboard.tsx";
import About from "./pages/about.tsx";
import ClaimSubmission from './pages/claimSubmission.tsx';
import "./App.css";



const App: React.FC = () => {
  return (
    <Router>
      <div className="app-container">
        <Navbar />
        <main className="content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/about" element={<About />} /> 
            <Route path="/claimSubmission" element={<ClaimSubmission/>} />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
};

export default App;
