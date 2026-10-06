import React, { useMemo, useState } from "react";

const seedMatters = [
  { id: "MAT-2026-001", title: "Gurindwa — Land Dispute", client: "Paul Gurindwa", type: "Litigation", status: "Active", advocate: "N. Byamugisha", next: "2026-10-09" },
  { id: "MAT-2026-002", title: "Commercial Advisory — Client A", client: "Client A", type: "Commercial", status: "Active", advocate: "J. Barya", next: "2026-10-14" },
  { id: "MAT-2026-003", title: "Employment Claim — Client B", client: "Client B", type: "Labour", status: "Pending", advocate: "B. Martin", next: "2026-10-21" }
];

const nav = ["Command Center", "Matters", "Clients", "Diary", "Documents", "Billing", "Research", "Audit"];

export function App() {
  const [active, setActive] = useState("Command Center");
  const [query, setQuery] = useState("");
  const [matters, setMatters] = useState(seedMatters);
  const [showNew, setShowNew] = useState(false);

  const filtered = useMemo(
    () => matters.filter(m => Object.values(m).join(" ").toLowerCase().includes(query.toLowerCase())),
    [matters, query]
  );

  function addMatter(event) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    setMatters(prev => [{
      id: `MAT-2026-${String(prev.length + 4).padStart(3, "0")}`,
      title: data.get("title"),
      client: data.get("client"),
      type: data.get("type"),
      status: "Intake",
      advocate: data.get("advocate") || "Unassigned",
      next: data.get("next") || "—"
    }, ...prev]);
    setShowNew(false);
    event.currentTarget.reset();
  }

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="mark">BB</div>
          <div><strong>Barya, Byamugisha</strong><span>& Co. Advocates</span></div>
        </div>
        <div className="workspace">INTERNAL PRACTICE PLATFORM</div>
        <nav>{nav.map(item => <button className={active === item ? "active" : ""} key={item} onClick={() => setActive(item)}>{item}</button>)}</nav>
        <div className="security">🔒 Matter-level confidentiality<br/><small>Governed by A1OS</small></div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div><span className="eyebrow">BARYA, BYAMUGISHA & CO.</span><h1>{active}</h1></div>
          <div className="top-actions"><span className="user">Partner · Moses</span><button className="primary" onClick={() => setShowNew(true)}>+ New matter</button></div>
        </header>

        {active === "Command Center" && <section>
          <div className="hero">
            <div><span className="eyebrow">PRACTICE OVERVIEW</span><h2>Know what needs attention.</h2><p>One governed workspace for matters, deadlines, documents, billing and legal work.</p></div>
            <div className="hero-status"><strong>Protected</strong><span>Role + matter access</span></div>
          </div>
          <div className="metrics">
            <Metric label="Active matters" value={matters.filter(m => m.status === "Active").length} />
            <Metric label="Upcoming deadlines" value="6" />
            <Metric label="Open tasks" value="14" />
            <Metric label="Outstanding fees" value="UGX 18.4M" />
          </div>
          <div className="panel">
            <div className="panel-head"><div><span className="eyebrow">MATTER REGISTER</span><h3>Recent matters</h3></div><input value={query} onChange={e => setQuery(e.target.value)} placeholder="Search matters…" /></div>
            <MatterTable matters={filtered} />
          </div>
        </section>}

        {active !== "Command Center" && <section className="panel page-panel">
          <span className="eyebrow">GOVERNED WORKSPACE</span>
          <h2>{active}</h2>
          <p>This workspace is part of the firm's governed practice platform. Records, actions and access will be persisted through A1OS + Supabase.</p>
          {active === "Matters" && <MatterTable matters={filtered} />}
          {active !== "Matters" && <div className="empty-state">Workspace foundation ready for connected production data.</div>}
        </section>}

        {showNew && <div className="modal-backdrop"><form className="modal" onSubmit={addMatter}>
          <div className="panel-head"><div><span className="eyebrow">MATTER INTAKE</span><h3>Open a new matter</h3></div><button type="button" onClick={() => setShowNew(false)}>×</button></div>
          <label>Matter title<input name="title" required placeholder="Matter title" /></label>
          <label>Client<input name="client" required placeholder="Client name" /></label>
          <label>Practice area<select name="type"><option>Litigation</option><option>Commercial</option><option>Labour</option><option>Conveyancing</option><option>Advisory</option></select></label>
          <label>Responsible advocate<input name="advocate" placeholder="Advocate" /></label>
          <label>Next deadline<input name="next" type="date" /></label>
          <button className="primary full">Create intake record</button>
        </form></div>}
      </main>
    </div>
  );
}

function Metric({label,value}) { return <div className="metric"><span>{label}</span><strong>{value}</strong></div>; }
function MatterTable({matters}) {
  return <div className="table-wrap"><table><thead><tr><th>Matter</th><th>Client</th><th>Area</th><th>Status</th><th>Next</th></tr></thead><tbody>{matters.map(m => <tr key={m.id}><td><strong>{m.title}</strong><small>{m.id} · {m.advocate}</small></td><td>{m.client}</td><td>{m.type}</td><td><span className={`pill ${m.status.toLowerCase()}`}>{m.status}</span></td><td>{m.next}</td></tr>)}</tbody></table></div>;
}
