import React,{useEffect,useState} from "react";
import {api} from "./api/client.js";
const API="/v1/professional-services";
const nav=[["Dashboard","dashboard"],["Projects","projects"],["Clients","clients"],["Estimates","quotes"],["Invoices","invoices"],["Payments","payments"],["Tasks","tasks"],["Documents","documents"],["Reports","reports"]];
const empty={projects:[],clients:[],quotes:[],invoices:[],payments:[],tasks:[],documents:[]};

function Form({type,onDone,onCancel}){
 const [v,setV]=useState({});
 const fields={
  clients:[["name","Client name"],["company","Company"],["email","Email"],["phone","Phone"]],
  projects:[["name","Project name"],["description","Description"],["status","Status"],["client_id","Client ID"]],
  quotes:[["title","Estimate title"],["description","Description"],["amount","Amount"],["client_id","Client ID"]],
  invoices:[["title","Invoice title"],["description","Description"],["amount","Amount"],["due_date","Due date"],["client_id","Client ID"]],
  payments:[["invoice_id","Invoice ID"],["amount","Amount"],["method","Payment method"]],
  tasks:[["title","Task title"],["description","Description"],["due_date","Due date"],["status","Status"]],
  documents:[["name","Document name"],["document_type","Document type"],["url","Document URL"]]
 }[type]||[];
 async function submit(e){e.preventDefault();const body={...v};for(const k of ["amount"])if(body[k]!==undefined)body[k]=Number(body[k]);await api.post(`${API}/${type}`,body);onDone();}
 return <form className="form" onSubmit={submit}>{fields.map(([k,l])=><label key={k}>{l}<input value={v[k]||""} onChange={e=>setV({...v,[k]:e.target.value})} required={["name","title","amount"].includes(k)}/></label>)}<div><button type="submit">Save</button><button type="button" onClick={onCancel}>Cancel</button></div></form>;
}

function Resource({type,label,keyName,fields}){
 const [rows,setRows]=useState([]),[form,setForm]=useState(false),[error,setError]=useState("");
 const load=()=>api.get(`${API}/${type}`).then(x=>setRows(x[keyName]||[])).catch(e=>setError(e.message));
 useEffect(load,[]);
 async function remove(id){if(!confirm("Delete this record?"))return;try{await api.delete(`${API}/${type}/${id}`);load()}catch(e){setError(e.message)}}
 return <><div className="titlebar"><div><h2>{label}</h2><p className="muted">{rows.length} record{rows.length===1?"":"s"}</p></div><div><button onClick={()=>setForm(!form)}>{form?"Close":"Add "+label.replace(/s$/,"")}</button> <button onClick={load}>Refresh</button></div></div>{form&&<Form type={type} onDone={()=>{setForm(false);load()}} onCancel={()=>setForm(false)}/>}<div className="panel">{error&&<p className="error">{error}</p>}{rows.length?<div className="table">{rows.map((x,i)=><div className="row" key={x.id||i}>{fields.map(f=><span key={f}><b>{f.replaceAll("_"," ")}</b>{String(x[f]??"—")}</span>)}{x.id&&<button onClick={()=>remove(x.id)}>Delete</button>}</div>)}</div>:!error&&<p>No records yet.</p>}</div></>;
}

function Dashboard(){
 const [s,setS]=useState({projects:0,clients:0,quotes:0,invoices:0,payments:0,tasks:0});
 useEffect(()=>Promise.all(Object.keys(s).map(k=>api.get(`${API}/${k}`).catch(()=>({})))).then(a=>setS(Object.fromEntries(Object.keys(s).map((k,i)=>[k,a[i].count??a[i][k]?.length??0])))),[]);
 return <><h2>Construction Dashboard</h2><p className="muted">Live operational overview.</p><div className="grid">{Object.entries(s).map(([k,v])=><article className="metric" key={k}><small>{k}</small><strong>{v}</strong></article>)}</div><div className="panel"><h3>Construction Operations</h3><p>Track projects from client engagement and estimating through invoicing, payments, tasks and documentation.</p></div></>;
}

export function App(){
 const [active,setActive]=useState("dashboard");
 const views={
  dashboard:<Dashboard/>,
  projects:<Resource type="projects" label="Projects" keyName="projects" fields={["name","status","client_id","created_at"]}/>,
  clients:<Resource type="clients" label="Clients" keyName="clients" fields={["name","company","phone","status"]}/>,
  quotes:<Resource type="quotes" label="Estimates & Quotes" keyName="quotes" fields={["title","amount","status","client_id"]}/>,
  invoices:<Resource type="invoices" label="Invoices" keyName="invoices" fields={["title","amount","paid_amount","status","due_date"]}/>,
  payments:<Resource type="payments" label="Payments" keyName="payments" fields={["invoice_id","amount","method","created_at"]}/>,
  tasks:<Resource type="tasks" label="Tasks" keyName="tasks" fields={["title","status","due_date"]}/>,
  documents:<Resource type="documents" label="Documents" keyName="documents" fields={["name","document_type","created_at"]}/>,
  reports:<Resource type="reports/financial" label="Financial Reports" keyName="reports" fields={["metric","value"]}/>
 };
 return <div className="app"><header><div><h1>Construction OS</h1><p>Project & Construction Management</p></div><strong>UGX</strong></header><div className="layout"><nav>{nav.map(([l,k])=><button className={active===k?"active":""} onClick={()=>setActive(k)} key={k}>{l}</button>)}</nav><main>{views[active]}</main></div></div>;
}
