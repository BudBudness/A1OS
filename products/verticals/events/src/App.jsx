import React from "react";
import {HashRouter,Routes,Route,Link} from "react-router-dom";
import Events from "./pages/Events.jsx";
import Venues from "./pages/Venues.jsx";
import Tickets from "./pages/Tickets.jsx";
import Attendees from "./pages/Attendees.jsx";
import Vendors from "./pages/Vendors.jsx";
import Payments from "./pages/Payments.jsx";
import Notifications from "./pages/Notifications.jsx";
import Reports from "./pages/Reports.jsx";

export default function App() {
  return <HashRouter><main className="app">
    <header><h1>Events</h1><p>A1OS frontend vertical</p></header>
    <nav><Link to="/">Dashboard</Link><Link to="/events">Events</Link>
<Link to="/venues">Venues</Link>
<Link to="/tickets">Tickets</Link>
<Link to="/attendees">Attendees</Link>
<Link to="/vendors">Vendors</Link>
<Link to="/payments">Payments</Link>
<Link to="/notifications">Notifications</Link>
<Link to="/reports">Reports</Link></nav>
    <Routes><Route path="/" element={<section><h2>Dashboard</h2><p>Events platform dashboard.</p></section>} />
      <Route path="/events" element={<Events />} />
<Route path="/venues" element={<Venues />} />
<Route path="/tickets" element={<Tickets />} />
<Route path="/attendees" element={<Attendees />} />
<Route path="/vendors" element={<Vendors />} />
<Route path="/payments" element={<Payments />} />
<Route path="/notifications" element={<Notifications />} />
<Route path="/reports" element={<Reports />} />
    </Routes>
  </main></HashRouter>;
}
