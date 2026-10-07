import React, { useEffect, useMemo, useState } from "react";
import { supabase } from "./lib/supabase.js";

const nav = ["Command Center", "Matters", "Clients", "Diary", "Documents", "Billing", "Research", "Audit"];

export function App() {
  const [session, setSession] = useState(null);
  const [profile, setProfile] = useState(null);
  const [active, setActive] = useState("Command Center");
  const [query, setQuery] = useState("");
  const [matters, setMatters] = useState([]);
  const [showNew, setShowNew] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let mounted = true;
    supabase.auth.getSession().then(({ data }) => {
      if (!mounted) return;
      setSession(data.session);
      if (!data.session) setLoading(false);
    });
    const { data: listener } = supabase.auth.onAuthStateChange((_event, next) => {
      setSession(next);
      if (!next) { setProfile(null); setMatters([]); setLoading(false); }
    });
    return () => { mounted = false; listener.subscription.unsubscribe(); };
  }, []);

  useEffect(() => {
    if (!session?.user) return;
    loadWorkspace(session.user.id);
  }, [session?.user?.id]);

  async function loadWorkspace(userId) {
    setLoading(true); setError("");
    const { data: p, error: pe } = await supabase.from("legal_profiles").select("user_id,full_name,role,active").eq("user_id", userId).maybeSingle();
    if (pe) { setError(pe.message); setLoading(false); return; }
    setProfile(p);
    if (!p || !p.active) { setLoading(false); return; }
    const { data, error: me } = await supabase.from("legal_matters").select("id,matter_number,title,practice_area,status,created_at,clients(legal_name),matter_members(assignment_role,profiles(full_name))").order("created_at", { ascending: false });
    if (me) setError(me.message); else setMatters(data || []);
    setLoading(false);
  }

  const filtered = useMemo(() => matters.filter(m => JSON.stringify(m).toLowerCase().includes(query.toLowerCase())), [matters, query]);

  async function signOut() { await supabase.auth.signOut(); }

  async function addMatter(event) {
    event.preventDefault(); setError("");
    const form = new FormData(event.currentTarget);
    const clientName = String(form.get("client")).trim();
    const { data: existing, error: ce } = await supabase.from("legal_clients").select("id").eq("legal_name", clientName).maybeSingle();
    if (ce) { setError(ce.message); return; }
    let clientId = existing?.id;
    if (!clientId) {
      const { data: created, error: cte } = await supabase.from("legal_clients").insert({ client_number: `CL-${Date.now()}`, client_type: "individual", legal_name: clientName, created_by: session.user.id }).select("id").single();
      if (cte) { setError(cte.message); return; }
      clientId = created.id;
    }
    const { data: matter, error: me } = await supabase.from("legal_matters").insert({
      matter_number: `MAT-${new Date().getFullYear()}-${String(matters.length + 1).padStart(4, "0")}`,
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
  if (!profile) return <div className="center-screen"><div className="access-card"><span className="eyebrow">ACCESS CONTROL</span><h1>Access pending</h1><p>Your authenticated account is not yet provisioned in the firm's legal workspace.</p><button className="primary" onClick={signOut}>Sign out</button></div></div>;
  if (profile.role === "client") return <div className="center-screen"><div className="access-card"><h1>Client access</h1><p>The client portal is restricted to explicitly shared matter information.</p><button className="primary" onClick={signOut}>Sign out</button></div></div>;

  return <div className="shell">
    <aside className="sidebar">
      <div className="brand"><div className="mark">BB</div><div><strong>Barya, Byamugisha</strong><span>& Co. Advocates</span></div></div>
      <div className="workspace">INTERNAL PRACTICE PLATFORM</div>
      <nav>{nav.map(item => <button className={active === item ? "active" : ""} key={item} onClick={() => setActive(item)}>{item}</button>)}</nav>
      <div className="security">🔒 Matter-level confidentiality<br/><small>A1OS governed · {profile.role}</small></div>
    </aside>
    <main className="main">
      <header className="topbar"><div><span className="eyebrow">BARYA, BYAMUGISHA & CO.</span><h1>{active}</h1></div><div className="top-actions"><span className="user">{profile.full_name} · {profile.role}</span><button className="secondary" onClick={signOut}>Sign out</button>{(profile.role === "partner" || profile.role === "administrator") && <button className="primary" onClick={() => setShowNew(true)}>+ New matter</button>}</div></header>
      {error && <div className="error-banner">{error}</div>}
      {active === "Command Center" && <section>
        <div className="hero"><div><span className="eyebrow">PRACTICE OVERVIEW</span><h2>Know what needs attention.</h2><p>One governed workspace for matters, deadlines, documents, billing and legal work.</p></div><div className="hero-status"><strong>Protected</strong><span>Role + matter access</span></div></div>
        <div className="metrics"><Metric label="Visible matters" value={matters.length}/><Metric label="Open tasks" value="—"/><Metric label="Upcoming deadlines" value="—"/><Metric label="Outstanding fees" value="—"/></div>
        <MatterPanel matters={filtered} query={query} setQuery={setQuery}/>
      </section>}
      {active !== "Command Center" && <section><div className="panel page-panel"><span className="eyebrow">GOVERNED WORKSPACE</span><h2>{active}</h2><p>Access is enforced by Supabase RLS and matter assignment. Connected records are loaded from the firm's production data layer.</p>{active === "Matters" && <MatterPanel matters={filtered} query={query} setQuery={setQuery}/>} {active !== "Matters" && <div className="empty-state">Production data connector ready for this workspace.</div>}</div></section>}
      {showNew && <div className="modal-backdrop"><form className="modal" onSubmit={addMatter}><div className="panel-head"><div><span className="eyebrow">MATTER INTAKE</span><h3>Open a new matter</h3></div><button type="button" onClick={() => setShowNew(false)}>×</button></div><label>Matter title<input name="title" required placeholder="Matter title"/></label><label>Client<input name="client" required placeholder="Client legal name"/></label><label>Practice area<select name="type"><option value="litigation">Litigation</option><option value="commercial">Commercial</option><option value="labour">Labour</option><option value="conveyancing">Conveyancing</option><option value="advisory">Advisory</option><option value="corporate">Corporate</option></select></label><button className="primary full">Create intake record</button></form></div>}
    </main>
  </div>;
}

function Login() {
  const [email,setEmail]=useState(""); const [password,setPassword]=useState(""); const [busy,setBusy]=useState(false); const [error,setError]=useState("");
  async function submit(e){e.preventDefault();setBusy(true);setError("");const {error:err}=await supabase.auth.signInWithPassword({email,password});if(err)setError(err.message);setBusy(false);}
  return <div className="login-screen"><form className="login-card" onSubmit={submit}><div className="brand login-brand"><div className="mark">BB</div><div><strong>Barya, Byamugisha</strong><span>& Co. Advocates</span></div></div><span className="eyebrow">INTERNAL PRACTICE PLATFORM</span><h1>Secure sign in</h1><p>Access is authenticated and matter-level permissions are enforced by the platform.</p><label>Email<input type="email" required value={email} onChange={e=>setEmail(e.target.value)} autoComplete="username"/></label><label>Password<input type="password" required value={password} onChange={e=>setPassword(e.target.value)} autoComplete="current-password"/></label>{error&&<div className="error-banner">{error}</div>}<button className="primary full" disabled={busy}>{busy?"Signing in…":"Sign in"}</button></form></div>;
}
function Metric({label,value}){return <div className="metric"><span>{label}</span><strong>{value}</strong></div>}
function MatterPanel({matters,query,setQuery}){return <div className="panel"><div className="panel-head"><div><span className="eyebrow">MATTER REGISTER</span><h3>Visible matters</h3></div><input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search matters…"/></div><div className="table-wrap"><table><thead><tr><th>Matter</th><th>Client</th><th>Area</th><th>Status</th></tr></thead><tbody>{matters.map(m=><tr key={m.id}><td><strong>{m.title}</strong><small>{m.matter_number}</small></td><td>{m.clients?.legal_name || "—"}</td><td>{m.practice_area}</td><td><span className={`pill ${m.status}`}>{m.status}</span></td></tr>)}{!matters.length&&<tr><td colSpan="4"><div className="empty-state">No matters are visible to this account.</div></td></tr>}</tbody></table></div></div>}
