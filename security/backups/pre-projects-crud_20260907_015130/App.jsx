import React, { useEffect, useState } from "react";
import { a1osApi } from "./api/client.js";
import "./styles.css";

const navItems = [
  "Dashboard",
  "Clients",
  "Projects",
  "Quotes",
  "Invoices",
  "Payments",
  "Tasks",
  "Documents",
  "Reports",
  "Settings",
];

const demoProjects = [
  ["Nile Heights Development", "Construction", "UGX 8.2M", "68%"],
  ["Kampala Office Fit-out", "Commercial", "UGX 4.6M", "44%"],
  ["Brand & Digital Strategy", "Strategy", "UGX 2.1M", "82%"],
  ["Operations Consultancy", "Consulting", "UGX 3.8M", "31%"],
];

export function App() {
  const [active, setActive] = useState("Dashboard");
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [modal, setModal] = useState(false);
  const [editing, setEditing] = useState(null);
  const [saving, setSaving] = useState(false);

  const emptyForm = {
    name: "",
    company: "",
    email: "",
    phone: "",
    status: "active",
  };

  const [form, setForm] = useState(emptyForm);

  async function loadClients() {
    setLoading(true);
    setError("");

    try {
      const result = await a1osApi.clients.list();
      setClients(Array.isArray(result) ? result : result.clients || []);
    } catch (err) {
      setError(err?.message || "Unable to load clients.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadClients();
  }, []);

  function createClient() {
    setEditing(null);
    setForm(emptyForm);
    setModal(true);
  }

  function editClient(client) {
    setEditing(client);
    setForm({
      name: client.name || "",
      company: client.company || "",
      email: client.email || "",
      phone: client.phone || "",
      status: client.status || "active",
    });
    setModal(true);
  }

  async function saveClient(event) {
    event.preventDefault();

    if (!form.name.trim()) return;

    setSaving(true);
    setError("");

    try {
      if (editing?.id) {
        const updated = await a1osApi.clients.update(editing.id, form);
        setClients((items) =>
          items.map((item) => item.id === editing.id ? updated : item)
        );
      } else {
        const created = await a1osApi.clients.create(form);
        setClients((items) => [created, ...items]);
      }

      setModal(false);
      setEditing(null);
      setForm(emptyForm);
    } catch (err) {
      setError(err?.message || "Unable to save client.");
    } finally {
      setSaving(false);
    }
  }

  async function removeClient(client) {
    if (!client?.id) return;

    try {
      await a1osApi.clients.remove(client.id);
      setClients((items) => items.filter((item) => item.id !== client.id));
    } catch (err) {
      setError(err?.message || "Unable to delete client.");
    }
  }

  function initials(name = "") {
    return name
      .split(/\s+/)
      .filter(Boolean)
      .slice(0, 2)
      .map((x) => x[0])
      .join("")
      .toUpperCase() || "?";
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">A</div>
          <div>
            <strong>A1OS</strong>
            <span>Professional Services</span>
          </div>
        </div>

        <div className="workspace">
          <span>WORKSPACE</span>
          <strong>Professional Services</strong>
          <small>Primary workspace</small>
        </div>

        <nav>
          {navItems.map((item) => (
            <button
              key={item}
              className={active === item ? "nav-item active" : "nav-item"}
              onClick={() => setActive(item)}
            >
              <span>{item === "Dashboard" ? "⌂" : item[0]}</span>
              {item}
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="system-status">
            <i />
            <span>A1OS Control Plane<br /><small>Connected</small></span>
          </div>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div className="search">⌕ <span>Search anything...</span></div>
          <div className="top-actions">
            <button>⌁</button>
            <button>?</button>
            <div className="user">EB</div>
          </div>
        </header>

        {active === "Dashboard" && (
          <div className="content">
            <div className="welcome">
              <div>
                <span className="eyebrow">MONDAY, SEPTEMBER 7, 2026</span>
                <h1>Good morning.</h1>
                <p>Here is what is happening across your business.</p>
              </div>
              <button className="primary" onClick={createClient}>+ Create client</button>
            </div>

            <section className="stats">
              <article><span>Active Clients</span><strong>{clients.length || 24}</strong><small>↑ 12% this month</small></article>
              <article><span>Open Projects</span><strong>12</strong><small>3 due this week</small></article>
              <article><span>Outstanding</span><strong>UGX 18.4M</strong><small>5 invoices overdue</small></article>
              <article><span>Revenue</span><strong>UGX 42.8M</strong><small>↑ 18% vs last month</small></article>
            </section>

            <div className="grid-two">
              <section className="panel">
                <div className="panel-head">
                  <div><h2>Active projects</h2><p>Current engagements</p></div>
                  <button className="link">View all</button>
                </div>
                {demoProjects.map(([name, type, amount, progress]) => (
                  <div className="project" key={name}>
                    <div className="project-main">
                      <strong>{name}</strong>
                      <span>{type}</span>
                    </div>
                    <b>{amount}</b>
                    <div className="progress"><i style={{width: progress}} /></div>
                    <small>{progress}</small>
                  </div>
                ))}
              </section>

              <section className="panel">
                <div className="panel-head">
                  <div><h2>Cash flow</h2><p>Last 6 months</p></div>
                  <strong>UGX 42.8M</strong>
                </div>
                <div className="chart">
                  {[42,58,48,76,64,88,72,94,81,100,87,96].map((h, i) =>
                    <i key={i} style={{height: `${h}%`}} />
                  )}
                </div>
                <div className="chart-labels"><span>Apr</span><span>May</span><span>Jun</span><span>Jul</span><span>Aug</span><span>Sep</span></div>
              </section>
            </div>

            <section className="panel">
              <div className="panel-head">
                <div><h2>Recent clients</h2><p>Live A1OS client records</p></div>
                <button className="link" onClick={() => setActive("Clients")}>View clients</button>
              </div>

              {loading && <div className="empty">Loading clients...</div>}
              {!loading && error && <div className="empty error">{error}</div>}
              {!loading && !error && clients.length === 0 && (
                <div className="empty">
                  <strong>No client records yet</strong>
                  <span>Create your first client to begin.</span>
                  <button className="primary" onClick={createClient}>Create client</button>
                </div>
              )}

              {clients.length > 0 && (
                <div className="client-list">
                  {clients.slice(0, 6).map((client) => (
                    <div className="client-row" key={client.id}>
                      <div className="avatar">{initials(client.name)}</div>
                      <div className="client-info">
                        <strong>{client.name}</strong>
                        <span>{client.company || client.email || client.phone || "Client"}</span>
                      </div>
                      <span className="badge">{client.status || "active"}</span>
                      <button className="small" onClick={() => editClient(client)}>Edit</button>
                      <button className="small danger" onClick={() => removeClient(client)}>Delete</button>
                    </div>
                  ))}
                </div>
              )}
            </section>
          </div>
        )}

        {active === "Clients" && (
          <div className="content">
            <div className="welcome">
              <div>
                <span className="eyebrow">A1OS / CLIENTS</span>
                <h1>Clients</h1>
                <p>Manage your professional relationships.</p>
              </div>
              <button className="primary" onClick={createClient}>+ Create client</button>
            </div>

            <section className="panel">
              {loading && <div className="empty">Loading clients...</div>}
              {!loading && error && <div className="empty error">{error}</div>}
              {!loading && !error && clients.length === 0 && (
                <div className="empty">
                  <strong>No clients yet</strong>
                  <span>Your first client will appear here.</span>
                  <button className="primary" onClick={createClient}>Create client</button>
                </div>
              )}

              {clients.length > 0 && (
                <div className="client-table">
                  <div className="table-head">
                    <span>CLIENT</span><span>COMPANY</span><span>CONTACT</span><span>STATUS</span><span />
                  </div>
                  {clients.map((client) => (
                    <div className="table-row" key={client.id}>
                      <strong>{client.name}</strong>
                      <span>{client.company || "—"}</span>
                      <span>{client.email || client.phone || "—"}</span>
                      <span className="badge">{client.status || "active"}</span>
                      <div>
                        <button className="small" onClick={() => editClient(client)}>Edit</button>
                        <button className="small danger" onClick={() => removeClient(client)}>Delete</button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </section>
          </div>
        )}

        {!["Dashboard", "Clients"].includes(active) && (
          <div className="content">
            <div className="welcome">
              <div>
                <span className="eyebrow">A1OS / {active.toUpperCase()}</span>
                <h1>{active}</h1>
                <p>This workspace is ready for the next operational module.</p>
              </div>
            </div>
            <section className="panel placeholder">
              <strong>{active} module</strong>
              <span>Connected to the Professional Services vertical runtime.</span>
            </section>
          </div>
        )}
      </main>

      {modal && (
        <div className="modal-backdrop" onClick={() => setModal(false)}>
          <form className="modal" onSubmit={saveClient} onClick={(e) => e.stopPropagation()}>
            <div className="modal-head">
              <div><span className="eyebrow">A1OS CLIENTS</span><h2>{editing ? "Edit client" : "Create client"}</h2></div>
              <button type="button" className="close" onClick={() => setModal(false)}>×</button>
            </div>

            <label>Name<input required value={form.name} onChange={(e) => setForm({...form, name:e.target.value})} /></label>
            <label>Company<input value={form.company} onChange={(e) => setForm({...form, company:e.target.value})} /></label>

            <div className="form-grid">
              <label>Email<input type="email" value={form.email} onChange={(e) => setForm({...form, email:e.target.value})} /></label>
              <label>Phone<input value={form.phone} onChange={(e) => setForm({...form, phone:e.target.value})} /></label>
            </div>

            <label>Status
              <select value={form.status} onChange={(e) => setForm({...form, status:e.target.value})}>
                <option value="active">Active</option>
                <option value="prospect">Prospect</option>
                <option value="inactive">Inactive</option>
              </select>
            </label>

            <div className="modal-actions">
              <button type="button" className="secondary" onClick={() => setModal(false)}>Cancel</button>
              <button className="primary" disabled={saving}>{saving ? "Saving..." : editing ? "Save changes" : "Create client"}</button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
