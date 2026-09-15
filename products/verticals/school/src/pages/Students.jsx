import React,{useEffect,useState} from "react";
import {schoolResources} from "../data.js";

export default function Students(){
  const [rows,setRows]=useState([]),[loading,setLoading]=useState(true),[error,setError]=useState("");
  useEffect(()=>{schoolResources.students.list().then(r=>setRows(r.students||r||[])).catch(e=>setError(e.message)).finally(()=>setLoading(false))},[]);
  return <section><h2>Students</h2>{loading&&<p>Loading…</p>}{error&&<p role="alert">{error}</p>} {!loading&&!error&&<div className="panel"><table><thead><tr><th>ID</th><th>Name</th><th>Status</th></tr></thead><tbody>{rows.map(s=><tr key={s.id}><td>{s.id}</td><td>{s.name||[s.first_name,s.last_name].filter(Boolean).join(" ")||"—"}</td><td>{s.status||"—"}</td></tr>)}</tbody></table></div>}</section>;
}
