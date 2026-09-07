import React,{useEffect,useState} from "react";
import {api} from "./api/client.js";

const API="/v1/professional-services";
const nav=[["Dashboard","dashboard"],["Projects","projects"],["Clients","clients"],["Estimates","quotes"],["Invoices","invoices"],["Payments","payments"],["Tasks","tasks"],["Documents","documents"],["Reports","reports"]];

function useResource(path,key){
 const [data,setData]=useState([]),[busy,setBusy]=useState(true),[error,setError]=useState("");
 const load=()=>{setBusy(true);setError("");api.get(`${API}${path}`).then(x=>setData(x[key]||[])).catch(e=>setError(e.message)).finally(()=>setBusy(false))};
 useEffect(load,[]);
 return {data,busy,error,load};
}

function Dashboard(){
 const [s,setS]=useState({projects:0,clients:0,invoices:0,payments:0});
 useEffect(()=>Promise.all([
  api.get(`${API}/projects`).catch(()=>({})),
  api.get(`${API}/clients`).catch(()=>({})),
  api.get(`${API}/invoices`).catch(()=>({})),
  api.get(`${API}/payments`).catch(()=>({}))
 ]).then(([p,c,i,pm])=>setS({
  projects:p.count??p.projects?.length??0,
  clients:c.count??c.clients?.length??0,
  invoices:i.count??i.invoices?.length??0,
  payments:pm.count??pm.payments?.length??0
 })),[]);
 return <><h2>Dashboard</h2><p className="muted">Construction operations at a glance.</p><div className="grid">{Object.entries(s).map(([k,v])=><article className="metric" key={k}><small>{k}</small><strong>{v}</strong></article>)}</div><div className="panel"><h3>Construction OS</h3><p>Manage projects, clients, estimates, invoices, payments, tasks and project documents from one A1OS workspace.</p></div></>;
}

function Resource({label,path,keyName,fields}){
 const r=useResource(path,keyName);
 return <><div className="titlebar"><div><h2>{label}</h2><p className="muted">A1OS Platform API</p></div><button onClick={r.load}>Refresh</button></div><div className="panel">{r.busy?<p>Loading...</p>:r.error?<p className="error">{r.error}</p>:r.data.length?<div className="table">{r.data.map((x,i)=><div className="row" key={x.id||i}>{fields.map(f=><span key={f}><b>{f.replaceAll("_"," ")}</b>{String(x[f]??"—")}</span>)}</div>)}</div>:<p>No records yet.</p>}</div></>;
}

function App(){
 const [active,setActive]=useState("dashboard");
 const views={
  dashboard:<Dashboard/>,
  projects:<Resource label="Projects" path="/projects" keyName="projects" fields={["name","status","client_id","created_at"]}/>,
  clients:<Resource label="Clients" path="/clients" keyName="clients" fields={["name","company","phone","status"]}/>,
  quotes:<Resource label="Estimates & Quotes" path="/quotes" keyName="quotes" fields={["title","amount","status","client_id"]}/>,
  invoices:<Resource label="Invoices" path="/invoices" keyName="invoices" fields={["title","amount","paid_amount","status","due_date"]}/>,
  payments:<Resource label="Payments" path="/payments" keyName="payments" fields={["invoice_id","amount","method","created_at"]}/>,
  tasks:<Resource label="Tasks" path="/tasks" keyName="tasks" fields={["title","status","due_date"]}/>,
  documents:<Resource label="Documents" path="/documents" keyName="documents" fields={["name","document_type","created_at"]}/>,
  reports:<Resource label="Financial Reports" path="/reports/financial" keyName="reports" fields={["metric","value"]}/>
 };
 return <div className="app"><header><div><h1>Construction OS</h1><p>Project & Construction Management</p></div><strong>UGX</strong></header><div className="layout"><nav>{nav.map(([label,key])=><button className={active===key?"active":""} onClick={()=>setActive(key)} key={key}>{label}</button>)}</nav><main>{views[active]}</main></div></div>;
}
export {App};
