import React,{useEffect,useMemo,useState} from "react";
import {HashRouter,Routes,Route,Link,useLocation,Navigate} from "react-router-dom";
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
import Finance from "./pages/Finance.jsx";
import Transport from "./pages/Transport.jsx";
import SchoolIdentity from "./pages/SchoolIdentity.jsx";
import Login from "./pages/Login.jsx";
import {loadSession,logout,currentRole,isAuthenticated} from "./core/auth.js";

const roles={
  Owner:{
    description:"Full school governance and oversight",
    sections:["Dashboard","Students","Parents","Admissions","Attendance","Fees","Finance","Transport","Users","Roles","Organizations","Audit","Site Content","School Identity"]
  },
  Leticia:{
    description:"School operations and administration",
    sections:["Dashboard","Students","Parents","Admissions","Attendance","Fees","Finance","Transport","Notifications","School Identity"]
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
  Notifications:"/notifications",
  Finance:"/finance",
  Transport:"/transport",
  "School Identity":"/school-identity"
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
  const [ready,setReady]=useState(false);
  const [authenticated,setAuthenticated]=useState(isAuthenticated());

  useEffect(()=>{
    loadSession().finally(()=>setReady(true));
  },[]);

  if(!ready) return <main className="app"><section className="panel"><h2>Little Oaks</h2><p>Loading secure session…</p></section></main>;
  if(!authenticated) return <Login onAuthenticated={()=>setAuthenticated(true)}/>;

  const role=currentRole() || "Owner";
  const allowed=roles[role]?.sections || ["Dashboard"];
  const nav=useMemo(
    ()=>allowed.map(label=>({label,path:routes[label]})).filter(x=>x.path),
    [allowed]
  );

  return <main className="app">
    <header className="brand-header">
      <div className="brand-mark">LO</div>
      <div className="brand-copy">
        <h1>Little Oaks</h1>
        <p>Montessori Kindergarten &amp; Daycare</p>
        <small>Nurture. Explore. Grow.</small>
      </div>
      <div className="role-control">
        <span className="role-badge">{role}</span>
        <button type="button" onClick={async()=>{await logout();setAuthenticated(false)}}>Sign out</button>
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
      <Route path="/finance" element={<Finance/>}/>
      <Route path="/transport" element={<Transport/>}/>
      <Route path="/school-identity" element={<SchoolIdentity/>}/>
      <Route path="/site-content" element={<SiteContent/>}/>
      <Route path="*" element={<Navigate to="/" replace/>}/>
    </Routes>
  </main>
}

export default function App(){return <HashRouter><Shell/></HashRouter>}
