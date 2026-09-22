import React,{useEffect,useState} from "react";
import {api} from "../api/client.js";
export default function Notifications(){const[r,setR]=useState([]),[e,setE]=useState("");useEffect(()=>{api.get("/notifications").then(x=>setR(x.notifications||x||[])).catch(x=>setE(x.message))},[]);return <section><h2>Notifications</h2>{e&&<p role="alert">{e}</p>}<div className="panel"><table><thead><tr><th>ID</th><th>Title</th><th>Status</th></tr></thead><tbody>{r.map(x=><tr key={x.id}><td>{x.id}</td><td>{x.title||x.message||"—"}</td><td>{x.status||"—"}</td></tr>)}</tbody></table></div></section>}
