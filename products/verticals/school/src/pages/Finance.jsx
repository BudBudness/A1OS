import React,{useEffect,useState} from "react";
import {api} from "../api/client.js";
export default function Finance(){
 const [a,setA]=useState([]),[l,setL]=useState([]),[e,setE]=useState("");
 useEffect(()=>Promise.all([api.get("/accounts"),api.get("/ledger")]).then(([x,y])=>{
  setA(x.items||x.accounts||[]);setL(y.items||y.ledger||[])
 }).catch(x=>setE(x.message)),[]);
 return <section><h2>Finance</h2>{e&&<p>{e}</p>}
 <div className="stat-grid"><article><strong>Accounts</strong><b>{a.length}</b></article><article><strong>Ledger entries</strong><b>{l.length}</b></article></div>
 <div className="table-wrap"><table><thead><tr><th>Account</th><th>Type</th><th>Balance</th></tr></thead><tbody>
 {a.map(x=><tr key={x.id}><td>{x.name||x.account_name||x.id}</td><td>{x.type||x.account_type||"—"}</td><td>{x.balance??"—"}</td></tr>)}
 </tbody></table></div></section>
}