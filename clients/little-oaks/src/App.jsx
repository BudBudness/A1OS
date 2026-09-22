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
import ChangePassword from "./pages/ChangePassword.jsx";
import Login from "./pages/Login.jsx";
import {api} from "./api/client.js";
import {schoolResources} from "./data.js";
import {loadSession,logout,currentRole,isAuthenticated,displayRole} from "./core/auth.js";

const roles={
  Director:{
    description:"Full Little Oaks organization governance and oversight",
    sections:["Dashboard","Students","Staff","Classes","Parents","Admissions","Attendance","Fees","Finance","Transport","Users","Roles","Organizations","Audit","Site Content","School Identity","Change password"]
  },
  Headmistress:{
    description:"Academic and staff operations",
    sections:["Dashboard","Students","Staff","Classes","Parents","Admissions","Attendance","Fees","Notifications","Change password"]
  },
  Staff:{
    description:"Assigned teaching and operational duties",
    sections:["Dashboard","Students","Attendance","Notifications","Change password"]
  }
};

const routes={
  Dashboard:"/",
  Students:"/students",
  Staff:"/staff",
  Classes:"/classes",
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
  ,"Change password":"/change-password"
};

function Staff(){
  const [state,setState]=useState({items:[],error:""});
  useEffect(()=>{api.get("/users").then(data=>setState({items:data.users||[],error:""})).catch(error=>setState({items:[],error:error.message}));},[]);
  return <section><h2>Staff</h2>{state.error?<p>Staff records are not available for this role.</p>:<table><thead><tr><th>Name</th><th>Email</th><th>Role</th></tr></thead><tbody>{state.items.map(user=><tr key={user.id}><td>{user.full_name}</td><td>{user.email}</td><td>{user.role}</td></tr>)}</tbody></table>}</section>;
}

function Classes(){
  return <section><h2>Classes</h2><p>Class records are not configured in the current school data system.</p></section>;
}

function Dashboard({role}){
  const [stats,setStats]=useState(null);
  const [error,setError]=useState("");
  useEffect(()=>{
    Promise.all([
      schoolResources.students.list(),
      schoolResources.attendance.list(),
      schoolResources.fees.list(),
      schoolResources.admissions.list(),
    ]).then(([students,attendance,fees,admissions])=>{
      setStats({
        students: students.items?.length || 0,
        attendance: attendance.items?.length || 0,
        fees: fees.items?.length || 0,
        admissions: admissions.items?.length || 0,
      });
    }).catch(err=>setError(err.message));
  },[]);
  return <section className="dashboard">
    <div className="dashboard-title">
      <div><span className="eyebrow">LITTLE OAKS</span><h2>{role} Dashboard</h2><p>{roles[role].description}</p></div>
      <span className="role-badge">{role}</span>
    </div>
    <div className="stat-grid">
      <article><strong>Students</strong><b>{stats?.students ?? "—"}</b><small>School records</small></article>
      <article><strong>Attendance</strong><b>{stats?.attendance ?? "—"}</b><small>Records</small></article>
      <article><strong>Fees</strong><b>{stats?.fees ?? "—"}</b><small>Fee records</small></article>
      <article><strong>Admissions</strong><b>{stats?.admissions ?? "—"}</b><small>Applications</small></article>
    </div>
    <div className="dashboard-grid">
      <article className="panel"><h3>School data</h3><p>{error || "Live data is loaded from the school data system."}</p></article>
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
    loadSession()
      .then(principal=>setAuthenticated(Boolean(principal)))
      .finally(()=>setReady(true));
  },[]);

  const role=displayRole(currentRole() || "director");
  const allowed=roles[role]?.sections || ["Dashboard"];
  const nav=useMemo(
    ()=>allowed.map(label=>({label,path:routes[label]})).filter(x=>x.path),
    [allowed]
  );

  if(!ready) return <main className="app"><section className="panel"><h2>Little Oaks</h2><p>Loading secure session…</p></section></main>;
  if(!authenticated) return <Login onAuthenticated={()=>setAuthenticated(true)}/>;

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
      <Route path="/staff" element={<Staff/>}/>
      <Route path="/classes" element={<Classes/>}/>
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
      <Route path="/change-password" element={<ChangePassword/>}/>
      <Route path="*" element={<Navigate to="/" replace/>}/>
    </Routes>
  </main>
}

export default function App(){return <HashRouter><Shell/></HashRouter>}
