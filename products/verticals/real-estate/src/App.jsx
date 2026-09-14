import React from "react";
import {HashRouter,Routes,Route,Link} from "react-router-dom";
import Properties from "./pages/Properties.jsx";
import Listings from "./pages/Listings.jsx";
import Clients from "./pages/Clients.jsx";
import Leases from "./pages/Leases.jsx";
import Payments from "./pages/Payments.jsx";
import Maintenance from "./pages/Maintenance.jsx";
import Reports from "./pages/Reports.jsx";
import Notifications from "./pages/Notifications.jsx";

export default function App() {
  return <HashRouter><main className="app">
    <header><h1>Real Estate</h1><p>A1OS frontend vertical</p></header>
    <nav><Link to="/">Dashboard</Link><Link to="/properties">Properties</Link>
<Link to="/listings">Listings</Link>
<Link to="/clients">Clients</Link>
<Link to="/leases">Leases</Link>
<Link to="/payments">Payments</Link>
<Link to="/maintenance">Maintenance</Link>
<Link to="/reports">Reports</Link>
<Link to="/notifications">Notifications</Link></nav>
    <Routes><Route path="/" element={<section><h2>Dashboard</h2><p>Real Estate platform dashboard.</p></section>} />
      <Route path="/properties" element={<Properties />} />
<Route path="/listings" element={<Listings />} />
<Route path="/clients" element={<Clients />} />
<Route path="/leases" element={<Leases />} />
<Route path="/payments" element={<Payments />} />
<Route path="/maintenance" element={<Maintenance />} />
<Route path="/reports" element={<Reports />} />
<Route path="/notifications" element={<Notifications />} />
    </Routes>
  </main></HashRouter>;
}
