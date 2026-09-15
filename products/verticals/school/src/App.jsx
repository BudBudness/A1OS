import React,{useMemo,useState} from "react";
import {HashRouter,Routes,Route,Link,useLocation} from "react-router-dom";
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

const roles={
  Owner:{
    description:"Full school governance and oversight",
    sections:["Dashboard","Students","Parents","Admissions","Attendance","Fees","Finance","Transport","Users","Roles","Organizations","Audit","Site Content"]
  },
  Leticia:{
    description:"School operations and administration",
    sections:["Dashboard","Students","Parents","Admissions","Attendance","Fees","Finance","Transport","Notifications"]
  },
  Headmistress:{
    description:"Academic and staff operations",
    sections:["Dashboard","Students","Parents","Admissions","Attendance","Fees","Notifications"]
  },
  Staff:{
    description:"Assigned teaching and operational duties",
    sections:["Dashboard","Students","Attendance","Notifications"]
  },
  Driver:{
    description:"Transport and assigned routes",
    sections:["Dashboard","Transport","Students","Notifications"]
  }
};

const routes={
  Dashboard:"/",
  Students:"/students",
  Parents:"/parents",
  Admissions:"/admissions",
  Attendance:"/attendance",
  Fees:"/fees",
  Users:"/users",
  Roles:"/roles",
  Organizations:"/organizations",
  Audit:"/audit",
  "Site Content":"/site-content",
  Notifications:"/notifications"
};

function Dashboard({role}){
  return <section className="dashboard">
    <div className="dashboard-title">
      <div><span className="eyebrow">LITTLE OAKS</span><h2>{role} Dashboard</h2><p>{roles[role].description}</p></div>
      <span className="role-badge">{role}</span>
    </div>
    <div className="stat-grid">
      <article><strong>Students</strong><b>—</b><small>School records</small></article>
      <article><strong>Attendance</strong><b>—</b><small>Today</small></article>
      <article><strong>Fees</strong><b>—</b><small>Current period</small></article>
      <article><strong>Admissions</strong><b>—</b><small>Pending</small></article>
    </div>
    <div className="dashboard-grid">
      <article className="panel"><h3>Today</h3><p>Operational activity will appear here as school records are connected.</p></article>
      <article className="panel"><h3>Quick actions</h3><div className="quick-actions">
        {roles[role].sections.filter(x=>routes[x]&&x!=="Dashboard").slice(0,5).map(x=><Link key={x} to={routes[x]}>{x}</Link>)}
      </div></article>
    </div>
  </section>
}

function Shell(){
  const location=useLocation();
  const [role,setRole]=useState("Owner");
  const allowed=roles[role].sections;
  const nav=useMemo(()=>allowed.map(label=>({label,path:routes[label]})).filter(x=>x.path),[allowed]);
  return <main className="app">
    <header className="brand-header">
      <div className="brand-mark">LO</div>
      <div className="brand-copy">
        <h1>Little Oaks</h1>
        <p>Montessori Kindergarten &amp; Daycare</p>
        <small>Nurture. Explore. Grow.</small>
      </div>
      <div className="role-control">
        <label htmlFor="role">Role</label>
        <select id="role" value={role} onChange={e=>setRole(e.target.value)}>
          {Object.keys(roles).map(r=><option key={r}>{r}</option>)}
        </select>
      </div>
    </header>
    <nav className="main-nav" aria-label="School navigation">
      {nav.map(({label,path})=><Link className={location.pathname===path?"active":""} key={label} to={path}>{label}</Link>)}
    </nav>
    <Routes>
      <Route path="/" element={<Dashboard role={role}/>}/>
      <Route path="/organizations" element={<Organizations/>}/>
      <Route path="/users" element={<Users/>}/>
      <Route path="/roles" element={<Roles/>}/>
      <Route path="/parties" element={<Parties/>}/>
      <Route path="/students" element={<Students/>}/>
      <Route path="/parents" element={<Parents/>}/>
      <Route path="/admissions" element={<Admissions/>}/>
      <Route path="/attendance" element={<Attendance/>}/>
      <Route path="/fees" element={<Fees/>}/>
      <Route path="/notifications" element={<Notifications/>}/>
      <Route path="/audit" element={<Audit/>}/>
      <Route path="/site-content" element={<SiteContent/>}/>
    </Routes>
  </main>
}

export default function App(){return <HashRouter><Shell/></HashRouter>}
