import React from "react";
import {HashRouter,Routes,Route,Link} from "react-router-dom";
import Organizations from "./pages/Organizations.jsx";
import Users from "./pages/Users.jsx";
import Roles from "./pages/Roles.jsx";
import Parties from "./pages/Parties.jsx";
import Students from "./pages/Students.jsx";
import Parents from "./pages/Parents.jsx";
import Admissions from "./pages/Admissions.jsx";
import Attendance from "./pages/Attendance.jsx";
import Fees from "./pages/Fees.jsx";
import Notifications from "./pages/Notifications.jsx";
import Audit from "./pages/Audit.jsx";
import SiteContent from "./pages/SiteContent.jsx";

export default function App() {
  return <HashRouter><main className="app">
    <header className="brand-header">
      <div className="brand-mark" aria-hidden="true">LO</div>
      <div>
        <h1>Little Oaks</h1>
        <p>Montessori Kindergarten &amp; Daycare</p>
        <small>Nurture. Explore. Grow.</small>
      </div>
    </header>
    <nav><Link to="/">Dashboard</Link><Link to="/organizations">Organizations</Link>
<Link to="/users">Users</Link>
<Link to="/roles">Roles</Link>
<Link to="/parties">Parties</Link>
<Link to="/students">Students</Link>
<Link to="/parents">Parents</Link>
<Link to="/admissions">Admissions</Link>
<Link to="/attendance">Attendance</Link>
<Link to="/fees">Fees</Link>
<Link to="/notifications">Notifications</Link>
<Link to="/audit">Audit</Link>
<Link to="/site-content">Site Content</Link></nav>
    <Routes><Route path="/" element={<section><h2>Dashboard</h2><p>School Management platform dashboard.</p></section>} />
      <Route path="/organizations" element={<Organizations />} />
<Route path="/users" element={<Users />} />
<Route path="/roles" element={<Roles />} />
<Route path="/parties" element={<Parties />} />
<Route path="/students" element={<Students />} />
<Route path="/parents" element={<Parents />} />
<Route path="/admissions" element={<Admissions />} />
<Route path="/attendance" element={<Attendance />} />
<Route path="/fees" element={<Fees />} />
<Route path="/notifications" element={<Notifications />} />
<Route path="/audit" element={<Audit />} />
<Route path="/site-content" element={<SiteContent />} />
    </Routes>
  </main></HashRouter>;
}
