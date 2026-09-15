import React,{useEffect,useState} from "react";
import {api} from "../api/client.js";
export default function Transport(){
 const [s,setS]=useState([]),[e,setE]=useState("");
 useEffect(()=>api.get("/education/transport").then(x=>setS(x.items||[])).catch(x=>setE(x.message)),[]);
 return <section><h2>Transport</h2>{e&&<p>{e}</p>}
 <div className="table-wrap"><table><thead><tr><th>Student</th><th>Admission</th><th>Class</th><th>Status</th><th>Route</th></tr></thead><tbody>
 {s.map(x=><tr key={x.id}><td>{x.first_name} {x.last_name}</td><td>{x.admission_no||"—"}</td><td>{x.class_name||"—"}</td><td>{x.transport_status||"Not assigned"}</td><td>{x.route||"—"}</td></tr>)}
 </tbody></table></div></section>
}