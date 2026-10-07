import React, { useEffect, useMemo, useState } from "react";
import { supabase } from "./lib/supabase.js";

const nav = ["Command Center", "Matters", "Clients", "Diary", "Documents", "Billing", "Research", "Audit"];

export function App() {
  const [session, setSession] = useState(null);
  const [profile, setProfile] = useState(null);
  const [active, setActive] = useState("Command Center");
  const [query, setQuery] = useState("");
  const [data, setData] = useState({ matters: [], clients: [], tasks: [], deadlines: [], documents: [], invoices: [], research: [], audit: [] });
  const [showNew, setShowNew] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let mounted = true;
    supabase.auth.getSession().then(({ data: d }) => {
      if (!mounted) return;
      setSession(d.session);
      if (!d.session) setLoading(false);
    });
    const { data: listener } = supabase.auth.onAuthStateChange((_event, next) => {
      setSession(next);
      if (!next) { setProfile(null); setData({ matters: [], clients: [], tasks: [], deadlines: [], documents: [], invoices: [], research: [], audit: [] }); setLoading(false); }
    });
    return () => { mounted = false; listener.subscription.unsubscribe(); };
  }, []);

  useEffect(() => { if (session?.user) loadWorkspace(session.user.id); }, [session?.user?.id]);

  async function loadWorkspace(userId) {
    setLoading(true); setError("");
    const { data: p, error: pe } = await supabase.from("legal_profiles").select("user_id,full_name,role,active").eq("user_id", userId).maybeSingle();
    if (pe) { setError(pe.message); setLoading(false); return; }
    setProfile(p);
    if (!p || !p.active) { setLoading(false); return; }

    const queries = await Promise.all([
      supabase.from("legal_matters").select("id,matter_number,title,practice_area,status,confidentiality,created_at,legal_clients(legal_name)").order("created_at", { ascending: false }),
      supabase.from("legal_clients").select("id,client_number,client_type,legal_name,phone,email,status,created_at").order("created_at", { ascending: false }),
      supabase.from("legal_tasks").select("id,matter_id,title,status,priority,due_at").order("due_at", { ascending: true }),
      supabase.from("legal_deadlines").select("id,matter_id,title,deadline_at,status,source").order("deadline_at", { ascending: true }),
      supabase.from("legal_documents").select("id,matter_id,title,document_type,status,version,created_at").order("created_at", { ascending: false }),
      supabase.from("legal_invoices").select("id,matter_id,invoice_number,amount,currency,status,due_date").order("created_at", { ascending: false }),
      supabase.from("legal_research").select("id,matter_id,title,source,citation,url,created_at").order("created_at", { ascending: false }),
      supabase.from("legal_audit_events").select("id,matter_id,action,entity_type,entity_id,created_at").order("created_at", { ascending: false }).limit(100)
    ]);
    const firstError = queries.find(q => q.error)?.error;
    if (firstError) setError(firstError.message);
    setData({
      matters: queries[0].data || [], clients: queries[1].data || [], tasks: queries[2].data || [],
      deadlines: queries[3].data || [], documents: queries[4].data || [], invoices: queries[5].data || [],
      research: queries[6].data || [], audit: queries[7].data || []
    });
    setLoading(false);
  }

  const visible = useMemo(() => {
    const list = data[active === "Command Center" ? "matters" : active.toLowerCase()] || [];
    return list.filter(x => JSON.stringify(x).toLowerCase().includes(query.toLowerCase()));
  }, [data, active, query]);

  async function signOut() { await supabase.auth.signOut(); }

  async function addMatter(event) {
    event.preventDefault(); setError("");
    const form = new FormData(event.currentTarget);
    const clientName = String(form.get("client")).trim();
    const { data: existing, error: ce } = await supabase.from("legal_clients").select("id").eq("legal_name", clientName).maybeSingle();
    if (ce) { setError(ce.message); return; }
    let clientId = existing?.id;
    if (!clientId) {
      const { data: created, error: cte } = await supabase.from("legal_clients").insert({
        client_number: `CL-${Date.now()}`, client_type: "individual", legal_name: clientName, created_by: session.user.id
      }).select("id").single();
      if (cte) { setError(cte.message); return; }
      clientId = created.id;
    }
    const { data: matter, error: me } = await supabase.from("legal_matters").insert({
      matter_number: `MAT-${new Date().getFullYear()}-${String(data.matters.length + 1).padStart(4, "0")}`,
      title: form.get("title"), client_id: clientId, practice_area: form.get("type"),
      status: "intake", confidentiality: "restricted", created_by: session.user.id
    }).select("id").single();
    if (me) { setError(me.message); return; }
    const { error: ae } = await supabase.from("legal_matter_members").insert({ matter_id: matter.id, user_id: session.user.id, assignment_role: "lead_advocate" });
    if (ae) { setError(ae.message); return; }
    setShowNew(false); event.currentTarget.reset(); await loadWorkspace(session.user.id);
  }

  if (!session) return <Login />;
  if (loading) return <div className="center-screen">Loading governed workspace…</div>;
  if (!profile) return <AccessPending signOut={signOut} />;
  if (profile.role === "client") return <AccessPending signOut={signOut} title="Client access" text="The client portal is restricted to explicitly shared matter information." />;

  const metrics = [
    ["Visible matters", data.matters.length],
    ["Open tasks", data.tasks.filter(x => x.status !== "completed").length],
    ["Upcoming deadlines", data.deadlines.filter(x => x.status === "open").length],
    ["Outstanding fees", formatMoney(data.invoices.filter(x => x.status !== "paid").reduce((s,x) => s + Number(x.amount || 0), 0))]
  ];

  return <div className="shell">
    <aside className="sidebar">
      <div className="brand"><div className="mark">BB</div><div><strong>Barya, Byamugisha</strong><span>& Co. Advocates</span></div></div>
      <div className="workspace">INTERNAL PRACTICE PLATFORM</div>
      <nav>{nav.map(item => <button className={active === item ? "active" : ""} key={item} onClick={() => { setActive(item); setQuery(""); }}>{item}</button>)}</nav>
      <div className="security">🔒 Matter-level confidentiality<br/><small>A1OS governed · {profile.role}</small></div>
    </aside>
    <main className="main">
      <header className="topbar"><div><span className="eyebrow">BARYA, BYAMUGISHA & CO.</span><h1>{active}</h1></div><div className="top-actions"><span className="user">{profile.full_name} · {profile.role}</span><button className="secondary" onClick={signOut}>Sign out</button>{(profile.role === "partner" || profile.role === "administrator") && <button className="primary" onClick={() => setShowNew(true)}>+ New matter</button>}</div></header>
      {error && <div className="error-banner">{error}</div>}
      {active === "Command Center"
        ? <section><div className="hero"><div><span className="eyebrow">PRACTICE OVERVIEW</span><h2>Know what needs attention.</h2><p>One governed workspace for matters, deadlines, documents, billing and legal work.</p></div><div className="hero-status"><strong>Protected</strong><span>Role + matter access</span></div></div><div className="metrics">{metrics.map(([label,value]) => <Metric key={label} label={label} value={value}/>)}</div><DataTable title="Matter register" rows={data.matters} kind="matters" query={query} setQuery={setQuery}/></section>
        : <section><div className="panel page-panel"><div className="panel-head"><div><span className="eyebrow">GOVERNED WORKSPACE</span><h2>{active}</h2></div><input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search…"/></div><DataTable rows={visible} kind={active.toLowerCase()} /></div></section>}
      {showNew && <div className="modal-backdrop"><form className="modal" onSubmit={addMatter}><div className="panel-head"><div><span className="eyebrow">MATTER INTAKE</span><h3>Open a new matter</h3></div><button type="button" onClick={() => setShowNew(false)}>×</button></div><label>Matter title<input name="title" required placeholder="Matter title"/></label><label>Client<input name="client" required placeholder="Client legal name"/></label><label>Practice area<select name="type"><option value="litigation">Litigation</option><option value="commercial">Commercial</option><option value="labour">Labour</option><option value="conveyancing">Conveyancing</option><option value="advisory">Advisory</option><option value="corporate">Corporate</option></select></label><button className="primary full">Create intake record</button></form></div>}
    </main>
  </div>;
}

function DataTable({ rows, kind, title, query, setQuery }) {
  const headers = {
    matters:["Matter","Client","Area","Status"], clients:["Client","Type","Contact","Status"], diary:["Deadline / Task","Matter","Due","Status"],
    documents:["Document","Matter","Type","Version"], billing:["Invoice","Matter","Amount","Status"], research:["Research item","Source","Citation","Date"], audit:["Action","Entity","Matter","Date"]
  }[kind] || ["Record","Status"];
  return <div className="panel"><div className="panel-head"><div>{title && <><span className="eyebrow">MATTER REGISTER</span><h3>{title}</h3></>}</div>{setQuery && <input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search matters…"/>}</div><div className="table-wrap"><table><thead><tr>{headers.map(h=><th key={h}>{h}</th>)}</tr></thead><tbody>{rows.map((r,i)=><tr key={r.id || i}>{renderCells(r,kind)}</tr>)}{!rows.length&&<tr><td colSpan={headers.length}><div className="empty-state">No records are visible to this account.</div></td></tr>}</tbody></table></div></div>;
}
function renderCells(r,kind){
  if(kind==="matters") return <><td><strong>{r.title}</strong><small>{r.matter_number}</small></td><td>{r.legal_clients?.legal_name || "—"}</td><td>{r.practice_area}</td><td><span className={`pill ${r.status}`}>{r.status}</span></td></>;
  if(kind==="clients") return <><td><strong>{r.legal_name}</strong><small>{r.client_number}</small></td><td>{r.client_type}</td><td>{r.phone || r.email || "—"}</td><td>{r.status}</td></>;
  if(kind==="diary") return <><td><strong>{r.title}</strong><small>{r.priority || r.source || "—"}</small></td><td>{r.matter_id || "—"}</td><td>{formatDate(r.due_at || r.deadline_at)}</td><td>{r.status}</td></>;
  if(kind==="documents") return <><td><strong>{r.title}</strong></td><td>{r.matter_id}</td><td>{r.document_type}</td><td>v{r.version}</td></>;
  if(kind==="billing") return <><td><strong>{r.invoice_number}</strong></td><td>{r.matter_id}</td><td>{formatMoney(r.amount,r.currency)}</td><td>{r.status}</td></>;
  if(kind==="research") return <><td><strong>{r.title}</strong></td><td>{r.source}</td><td>{r.citation || r.url || "—"}</td><td>{formatDate(r.created_at)}</td></>;
  if(kind==="audit") return <><td><strong>{r.action}</strong></td><td>{r.entity_type} {r.entity_id || ""}</td><td>{r.matter_id || "—"}</td><td>{formatDate(r.created_at)}</td></>;
  return <><td>{r.title || "Record"}</td><td>{r.status || "—"}</td></>;
}
function formatDate(v){return v ? new Date(v).toLocaleDateString("en-GB") : "—";}
function formatMoney(v,c="UGX"){return `${c} ${Number(v||0).toLocaleString("en-UG")}`;}
function Metric({label,value}){return <div className="metric"><span>{label}</span><strong>{value}</strong></div>;}
function AccessPending({signOut,title="Access pending",text="Your authenticated account is not yet provisioned in the firm's legal workspace."}){return <div className="center-screen"><div className="access-card"><span className="eyebrow">ACCESS CONTROL</span><h1>{title}</h1><p>{text}</p><button className="primary" onClick={signOut}>Sign out</button></div></div>;}
function Login(){
  const [email,setEmail]=useState(""); const [password,setPassword]=useState(""); const [busy,setBusy]=useState(false); const [error,setError]=useState("");
  async function submit(e){e.preventDefault();setBusy(true);setError("");const {error:err}=await supabase.auth.signInWithPassword({email,password});if(err)setError(err.message);setBusy(false);}
  return <div className="login-screen"><form className="login-card" onSubmit={submit}><div className="brand login-brand"><div className="mark">BB</div><div><strong>Barya, Byamugisha</strong><span>& Co. Advocates</span></div></div><span className="eyebrow">INTERNAL PRACTICE PLATFORM</span><h1>Secure sign in</h1><p>Authentication and matter-level permissions are enforced by the platform.</p><label>Email<input type="email" required value={email} onChange={e=>setEmail(e.target.value)} autoComplete="username"/></label><label>Password<input type="password" required value={password} onChange={e=>setPassword(e.target.value)} autoComplete="current-password"/></label>{error&&<div className="error-banner">{error}</div>}<button className="primary full" disabled={busy}>{busy?"Signing in…":"Sign in"}</button></form></div>;
}
