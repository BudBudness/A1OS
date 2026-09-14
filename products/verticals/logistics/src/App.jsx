import React from "react";
import {HashRouter,Routes,Route,Link} from "react-router-dom";
import Customers from "./pages/Customers.jsx";
import Shipments from "./pages/Shipments.jsx";
import Vehicles from "./pages/Vehicles.jsx";
import Drivers from "./pages/Drivers.jsx";
import Tracking from "./pages/Tracking.jsx";
import Billing from "./pages/Billing.jsx";
import Inventory from "./pages/Inventory.jsx";
import Reports from "./pages/Reports.jsx";

export default function App() {
  return <HashRouter><main className="app">
    <header><h1>Logistics</h1><p>A1OS frontend vertical</p></header>
    <nav><Link to="/">Dashboard</Link><Link to="/customers">Customers</Link>
<Link to="/shipments">Shipments</Link>
<Link to="/vehicles">Vehicles</Link>
<Link to="/drivers">Drivers</Link>
<Link to="/tracking">Tracking</Link>
<Link to="/billing">Billing</Link>
<Link to="/inventory">Inventory</Link>
<Link to="/reports">Reports</Link></nav>
    <Routes><Route path="/" element={<section><h2>Dashboard</h2><p>Logistics platform dashboard.</p></section>} />
      <Route path="/customers" element={<Customers />} />
<Route path="/shipments" element={<Shipments />} />
<Route path="/vehicles" element={<Vehicles />} />
<Route path="/drivers" element={<Drivers />} />
<Route path="/tracking" element={<Tracking />} />
<Route path="/billing" element={<Billing />} />
<Route path="/inventory" element={<Inventory />} />
<Route path="/reports" element={<Reports />} />
    </Routes>
  </main></HashRouter>;
}
