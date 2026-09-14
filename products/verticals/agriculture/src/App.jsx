import React from "react";
import {HashRouter,Routes,Route,Link} from "react-router-dom";
import Farms from "./pages/Farms.jsx";
import Crops from "./pages/Crops.jsx";
import Livestock from "./pages/Livestock.jsx";
import Inputs from "./pages/Inputs.jsx";
import Production from "./pages/Production.jsx";
import Inventory from "./pages/Inventory.jsx";
import Sales from "./pages/Sales.jsx";
import Reports from "./pages/Reports.jsx";

export default function App() {
  return <HashRouter><main className="app">
    <header><h1>Agriculture</h1><p>A1OS frontend vertical</p></header>
    <nav><Link to="/">Dashboard</Link><Link to="/farms">Farms</Link>
<Link to="/crops">Crops</Link>
<Link to="/livestock">Livestock</Link>
<Link to="/inputs">Inputs</Link>
<Link to="/production">Production</Link>
<Link to="/inventory">Inventory</Link>
<Link to="/sales">Sales</Link>
<Link to="/reports">Reports</Link></nav>
    <Routes><Route path="/" element={<section><h2>Dashboard</h2><p>Agriculture platform dashboard.</p></section>} />
      <Route path="/farms" element={<Farms />} />
<Route path="/crops" element={<Crops />} />
<Route path="/livestock" element={<Livestock />} />
<Route path="/inputs" element={<Inputs />} />
<Route path="/production" element={<Production />} />
<Route path="/inventory" element={<Inventory />} />
<Route path="/sales" element={<Sales />} />
<Route path="/reports" element={<Reports />} />
    </Routes>
  </main></HashRouter>;
}
