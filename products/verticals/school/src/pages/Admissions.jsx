import React,{useEffect,useState} from "react";
import {schoolResources} from "../data.js";
export default function Admissions(){const[r,setR]=useState([]),[e,setE]=useState("");useEffect(()=>{schoolResources.admissions.list().then(x=>setR(x.admissions||x||[])).catch(x=>setE(x.message))},[]);return <section><h2>Admissions</h2>{e&&<p role="alert">{e}</p>}<div className="panel"><table><thead><tr><th>ID</th><th>Student</th><th>Status</th></tr></thead><tbody>{r.map(x=><tr key={x.id}><td>{x.id}</td><td>{x.student_id||"—"}</td><td>{x.status||"—"}</td></tr>)}</tbody></table></div></section>}
