import React,{useEffect,useState} from "react";
import {api} from "../api/client.js";
export default function SchoolIdentity(){
 const [x,setX]=useState([]),[e,setE]=useState("");
 useEffect(()=>api.get("/education/site-content").then(r=>setX(r.items||[])).catch(r=>setE(r.message)),[]);
 return <section><h2>School Identity</h2><p>System-managed identity and authorized school configuration.</p>{e&&<p>{e}</p>}
 <div className="table-wrap"><table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>
 {x.map(v=><tr key={v.id}><td>{v.key||v.title||v.content_key||v.id}</td><td>{v.value||v.content||v.body||"—"}</td></tr>)}
 </tbody></table></div></section>
}