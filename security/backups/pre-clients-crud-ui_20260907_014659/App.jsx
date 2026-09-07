import React, { useEffect, useState } from "react";
import { a1osApi } from "./api/client.js";
import "./styles.css";

const stats = [
  ["Active Clients", "24", "+8.2%", "clients"],
  ["Open Projects", "12", "+3 this month", "projects"],
  ["Outstanding", "UGX 18.4M", "7 invoices", "money"],
  ["Revenue", "UGX 42.8M", "+14.6%", "revenue"],
];

const projects = [
  { name: "Nile Heights Development", client: "Nile Heights Ltd", status: "In Progress", value: "UGX 12.5M", due: "18 Sep 2026", progress: 72 },
  { name: "Kampala Office Fit-out", client: "Vertex Holdings", status: "In Progress", value: "UGX 8.2M", due: "25 Sep 2026", progress: 48 },
  { name: "Brand & Digital Strategy", client: "Kato Enterprises", status: "Review", value: "UGX 4.8M", due: "12 Sep 2026", progress: 86 },
  { name: "Operations Consultancy", client: "Lakeview Group", status: "Planning", value: "UGX 6.1M", due: "30 Sep 2026", progress: 22 },
];

const clients = [
  ["Nile Heights Ltd", "Construction", "UGX 12.5M", "Active"],
  ["Vertex Holdings", "Corporate", "UGX 8.2M", "Active"],
  ["Kato Enterprises", "Business", "UGX 4.8M", "Review"],
  ["Lakeview Group", "Consulting", "UGX 6.1M", "Planning"],
];

function Icon({ children }) {
  return <span className="icon">{children}</span>;
}

export function App() {
  const [clients, setClients] = useState([]);
  const [clientsLoading, setClientsLoading] = useState(false);
  const [clientsError, setClientsError] = useState("");

  useEffect(() => {
    let active = true;

    async function loadClients() {
      setClientsLoading(true);
      setClientsError("");

      try {
        const result = await a1osApi.clients.list();
        const rows = Array.isArray(result)
          ? result
          : Array.isArray(result?.clients)
            ? result.clients
            : [];

        if (active) setClients(rows);
      } catch (error) {
        if (active) {
          setClientsError(error?.message || "Unable to load clients.");
        }
      } finally {
        if (active) setClientsLoading(false);
      }
    }

    loadClients();
    return () => {
      active = false;
    };
  }, []);

  const [page, setPage] = useState("Dashboard");
  const [menu, setMenu] = useState(false);

  const nav = [
    ["Dashboard", "⌂"],
    ["Clients", "♙"],
    ["Projects", "▣"],
    ["Quotes", "▤"],
    ["Invoices", "▥"],
    ["Payments", "◆"],
    ["Tasks", "✓"],
    ["Documents", "□"],
    ["Reports", "◒"],
  ];

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brandMark">A</div>
          <div><strong>Professional</strong><small>Services</small></div>
        </div>

        <div className="workspace">
          <span>WORKSPACE</span>
          <button>Professional Services <b>⌄</b></button>
        </div>

        <nav>
          {nav.map(([name, icon]) => (
            <button key={name} className={page === name ? "nav active" : "nav"} onClick={() => setPage(name)}>
              <Icon>{icon}</Icon>{name}
            </button>
          ))}
        </nav>

        <div className="sidebarBottom">
          <button className="nav"><Icon>⚙</Icon>Settings</button>
          <div className="user">
            <div className="avatar">EB</div>
            <div><strong>Administrator</strong><small>Owner</small></div>
            <span>•••</span>
          </div>
        </div>
      </aside>

      <main className="main">
        <header>
          <div>
            <div className="crumb">Workspace / <strong>{page}</strong></div>
            <h1>{page}</h1>
          </div>
          <div className="headerActions">
            <button className="search">⌕ <span>Search</span><kbd>⌘ K</kbd></button>
            <button className="notification">♢<i></i></button>
            <button className="primary" onClick={() => setMenu(!menu)}>+ Create</button>
          </div>
        </header>

        {menu && <div className="createMenu">
          <button onClick={() => setMenu(false)}>New Client</button>
          <button onClick={() => setMenu(false)}>New Project</button>
          <button onClick={() => setMenu(false)}>New Quote</button>
          <button onClick={() => setMenu(false)}>New Invoice</button>
        </div>}

        {page === "Dashboard" ? (
          <>
            <section className="welcome">
              <div>
                <span className="eyebrow">MONDAY, 7 SEPTEMBER 2026</span>
                <h2>Good afternoon, Administrator.</h2>
                <p>Here is what is happening across your business.</p>
              </div>
              <button className="secondary">View reports →</button>
            </section>

            <section className="stats">
              {stats.map(([label, value, change, type]) => (
                <div className="stat" key={label}>
                  <div className="statTop"><span>{label}</span><span className={"statIcon " + type}>◈</span></div>
                  <strong>{value}</strong>
                  <small>{change}</small>
                </div>
              ))}
            </section>

            <section className="grid">
              <div className="panel projects">
                <div className="panelHead"><div><h3>Active projects</h3><p>Current work across your clients</p></div><button onClick={() => setPage("Projects")}>View all →</button></div>
                <div className="table">
                  {projects.map(p => <div className="project" key={p.name}>
                    <div className="projectName"><div className="projectBadge">{p.name[0]}</div><div><strong>{p.name}</strong><small>{p.client}</small></div></div>
                    <span className={"status " + p.status.toLowerCase().replace(" ","-")}>{p.status}</span>
                    <span className="amount">{p.value}</span>
                    <div className="progress"><div style={{width:p.progress+"%"}}></div><small>{p.progress}%</small></div>
                  </div>)}
                </div>
              </div>

              <div className="panel">
                <div className="panelHead"><div><h3>Cash flow</h3><p>Last 6 months</p></div><button>Monthly⌄</button></div>
                <div className="chart">
                  {[42,58,48,71,64,88].map((h,i)=><div className="barWrap" key={i}><div className="bar" style={{height:h+"%"}}></div><small>{["Apr","May","Jun","Jul","Aug","Sep"][i]}</small></div>)}
                </div>
                <div className="chartLegend"><span><i></i>Revenue</span><strong>UGX 42.8M</strong></div>
              </div>
            </section>

            <section className="grid bottom">
              <div className="panel">
                <div className="panelHead"><div><h3>Recent clients</h3><p>Latest client activity</p></div><button onClick={() => setPage("Clients")}>View all →</button></div>
                {clients.map(c=><div className="client" key={c[0]}><div className="clientAvatar">{c[0].split(" ").map(x=>x[0]).join("").slice(0,2)}</div><div><strong>{c[0]}</strong><small>{c[1]}</small></div><strong className="clientAmount">{c[2]}</strong><span className="dotStatus">● {c[3]}</span></div>)}
              </div>
              <div className="panel attention">
                <div className="panelHead"><div><h3>Needs attention</h3><p>Items requiring action</p></div></div>
                <div className="alert"><b>7</b><div><strong>Outstanding invoices</strong><small>UGX 18.4M awaiting payment</small></div><span>→</span></div>
                <div className="alert"><b>3</b><div><strong>Quotes awaiting response</strong><small>Follow up with prospects</small></div><span>→</span></div>
                <div className="alert"><b>5</b><div><strong>Tasks due this week</strong><small>Keep projects on schedule</small></div><span>→</span></div>
              </div>
            </section>
          </>
        ) : (
          <section className="pagePanel">
            <div className="emptyHead">
              <div><span className="eyebrow">MANAGEMENT</span><h2>{page}</h2><p>Manage your {page.toLowerCase()} from the A1OS workspace.</p></div>
              <button className="primary">+ New {page.slice(0,-1) || page}</button>
            </div>
            <div className="coming">
              <div className="bigIcon">◈</div>
              <h2>{page} workspace</h2>
              <p>The module is connected to the Professional Services vertical and ready for A1OS platform integration.</p>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
