import React from "react";
import {HashRouter,Routes,Route,Link} from "react-router-dom";
import Customers from "./pages/Customers.jsx";
import Staff from "./pages/Staff.jsx";
import Services from "./pages/Services.jsx";
import Appointments from "./pages/Appointments.jsx";
import Products from "./pages/Products.jsx";
import Payments from "./pages/Payments.jsx";
import Inventory from "./pages/Inventory.jsx";
import Reports from "./pages/Reports.jsx";

export default function App() {
  return <HashRouter><main className="app">
    <header><h1>Salon / Barber</h1><p>A1OS frontend vertical</p></header>
    <nav><Link to="/">Dashboard</Link><Link to="/customers">Customers</Link>
<Link to="/staff">Staff</Link>
<Link to="/services">Services</Link>
<Link to="/appointments">Appointments</Link>
<Link to="/products">Products</Link>
<Link to="/payments">Payments</Link>
<Link to="/inventory">Inventory</Link>
<Link to="/reports">Reports</Link></nav>
    <Routes><Route path="/" element={<section><h2>Dashboard</h2><p>Salon / Barber platform dashboard.</p></section>} />
      <Route path="/customers" element={<Customers />} />
<Route path="/staff" element={<Staff />} />
<Route path="/services" element={<Services />} />
<Route path="/appointments" element={<Appointments />} />
<Route path="/products" element={<Products />} />
<Route path="/payments" element={<Payments />} />
<Route path="/inventory" element={<Inventory />} />
<Route path="/reports" element={<Reports />} />
    </Routes>
  </main></HashRouter>;
}
