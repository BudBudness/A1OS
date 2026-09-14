import React from "react";
import {HashRouter,Routes,Route,Link} from "react-router-dom";
import Projects from "./pages/Projects.jsx";
import Sites from "./pages/Sites.jsx";
import Contractors from "./pages/Contractors.jsx";
import Materials from "./pages/Materials.jsx";
import Procurement from "./pages/Procurement.jsx";
import Inventory from "./pages/Inventory.jsx";
import Budgets from "./pages/Budgets.jsx";
import Ledger from "./pages/Ledger.jsx";
import Reports from "./pages/Reports.jsx";

export default function App() {
  return <HashRouter><main className="app">
    <header><h1>Construction</h1><p>A1OS frontend vertical</p></header>
    <nav><Link to="/">Dashboard</Link><Link to="/projects">Projects</Link>
<Link to="/sites">Sites</Link>
<Link to="/contractors">Contractors</Link>
<Link to="/materials">Materials</Link>
<Link to="/procurement">Procurement</Link>
<Link to="/inventory">Inventory</Link>
<Link to="/budgets">Budgets</Link>
<Link to="/ledger">Ledger</Link>
<Link to="/reports">Reports</Link></nav>
    <Routes><Route path="/" element={<section><h2>Dashboard</h2><p>Construction platform dashboard.</p></section>} />
      <Route path="/projects" element={<Projects />} />
<Route path="/sites" element={<Sites />} />
<Route path="/contractors" element={<Contractors />} />
<Route path="/materials" element={<Materials />} />
<Route path="/procurement" element={<Procurement />} />
<Route path="/inventory" element={<Inventory />} />
<Route path="/budgets" element={<Budgets />} />
<Route path="/ledger" element={<Ledger />} />
<Route path="/reports" element={<Reports />} />
    </Routes>
  </main></HashRouter>;
}
