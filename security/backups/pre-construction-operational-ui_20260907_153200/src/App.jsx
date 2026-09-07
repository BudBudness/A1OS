import React, { useEffect, useState } from "react";
import { api } from "./api/client.js";

const modules = [
  ["Dashboard","dashboard"],["Projects","projects"],["Clients","clients"],
  ["Estimates","estimates"],["Invoices","invoices"],["Payments","payments"],
  ["Tasks","tasks"],["Documents","documents"],["Reports","reports"]
];

function Dashboard() {
  const [data,setData]=useState({});
  useEffect(()=>Promise.all([
    api.get("/v1/professional-services/projects").catch(()=>({count:0})),
    api.get("/v1/professional-services/clients").catch(()=>({count:0})),
    api.get("/v1/professional-services/invoices").catch(()=>({count:0})),
    api.get("/v1/professional-services/payments").catch(()=>({count:0}))
  ]).then(([projects,clients,invoices,payments])=>setData({
    projects:projects.count??projects.projects?.length??0,
    clients:clients.count??clients.clients?.length??0,
    invoices:invoices.count??invoices.invoices?.length??0,
    payments:payments.count??payments.payments?.length??0
  })),[]);
  return <><h2>Construction Dashboard</h2><div className="grid">{Object.entries(data).map(([k,v])=><article key={k}><small>{k.toUpperCase()}</small><strong>{v}</strong></article>)}</div><section><h3>Construction Operations</h3><p>Projects, clients, estimates, invoicing, payments, tasks and documents are managed through the A1OS platform.</p></section></>;
}

function Resource({type,label,path}) {
  const [rows,setRows]=useState([]);
  const [loading,setLoading]=useState(true);
  const load=()=>{setLoading(true);api.get(path).then(x=>setRows(x[type]||[])).catch(()=>setRows([])).finally(()=>setLoading(false));};
  useEffect(load,[]);
  return <><h2>{label}</h2><section><button onClick={load}>Refresh</button>{loading?<p>Loading...</p>:rows.length?<div className="list">{rows.map((r,i)=><article key={r.id||i}><strong>{r.name||r.title||r.description||`${label} ${i+1}`}</strong><small>{r.status||r.amount||r.created_at||""}</small></article>)}</div>:<p>No {label.toLowerCase()} recorded yet.</p>}</section></>;
}

export function App() {
  const [active,setActive]=useState("dashboard");
  const content={
    dashboard:<Dashboard/>,
    projects:<Resource type="projects" label="Construction Projects" path="/v1/professional-services/projects"/>,
    clients:<Resource type="clients" label="Clients" path="/v1/professional-services/clients"/>,
    estimates:<Resource type="quotes" label="Estimates & Quotes" path="/v1/professional-services/quotes"/>,
    invoices:<Resource type="invoices" label="Invoices" path="/v1/professional-services/invoices"/>,
    payments:<Resource type="payments" label="Payments" path="/v1/professional-services/payments"/>,
    tasks:<Resource type="tasks" label="Tasks" path="/v1/professional-services/tasks"/>,
    documents:<Resource type="documents" label="Documents" path="/v1/professional-services/documents"/>,
    reports:<Resource type="reports" label="Reports" path="/v1/professional-services/reports/financial"/>
  };
  return <div className="app"><header><div><h1>Construction OS</h1><p>A1OS Project & Construction Management</p></div><span>UGX</span></header><div className="body"><nav>{modules.map(([name,key])=><button className={active===key?"active":""} onClick={()=>setActive(key)} key={key}>{name}</button>)}</nav><main>{content[active]}</main></div></div>;
}
