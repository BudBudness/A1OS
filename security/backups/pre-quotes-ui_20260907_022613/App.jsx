import React, { useEffect, useMemo, useState } from "react";
import { a1osApi } from "./api/client.js";
import "./styles.css";

const navItems = [
  "Dashboard","Clients","Projects","Quotes","Invoices",
  "Payments","Tasks","Documents","Reports","Settings",
];

const emptyProject = {
  name: "",
  client_id: "",
  service_type: "",
  status: "active",
  value_ugx: 0,
  progress: 0,
  start_date: "",
  due_date: "",
  description: "",
};

const emptyClient = {
  name: "",
  email: "",
  phone: "",
  company: "",
};

const money = (n) =>
  `UGX ${Number(n || 0).toLocaleString("en-UG")}`;

export function App() {
  const [page, setPage] = useState("Dashboard");
  const [clients, setClients] = useState([]);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [projectModal, setProjectModal] = useState(null);
  const [clientModal, setClientModal] = useState(null);
  const [projectForm, setProjectForm] = useState(emptyProject);
  const [clientForm, setClientForm] = useState(emptyClient);
  const [saving, setSaving] = useState(false);

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const [c, p] = await Promise.all([
        a1osApi.clients.list(),
        a1osApi.projects.list(),
      ]);
      setClients(c.clients || []);
      setProjects(p.projects || []);
    } catch (e) {
      setError(e.message || "Unable to load data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const activeProjects = projects.filter(p => p.status === "active").length;
  const outstanding = projects.reduce((s, p) => s + Number(p.value_ugx || 0), 0);

  const openProjectCreate = () => {
    setProjectForm(emptyProject);
    setProjectModal("create");
  };

  const openProjectEdit = (project) => {
    setProjectForm({
      name: project.name || "",
      client_id: project.client_id || "",
      service_type: project.service_type || "",
      status: project.status || "active",
      value_ugx: project.value_ugx || 0,
      progress: project.progress || 0,
      start_date: project.start_date || "",
      due_date: project.due_date || "",
      description: project.description || "",
    });
    setProjectModal(project.id);
  };

  const saveProject = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      if (projectModal === "create") {
        await a1osApi.projects.create(projectForm);
      } else {
        await a1osApi.projects.update(projectModal, projectForm);
      }
      setProjectModal(null);
      await load();
    } catch (e) {
      setError(e.message || "Unable to save project");
    } finally {
      setSaving(false);
    }
  };

  const deleteProject = async (id) => {
    if (!confirm("Delete this project?")) return;
    try {
      await a1osApi.projects.remove(id);
      await load();
    } catch (e) {
      setError(e.message || "Unable to delete project");
    }
  };

  const saveClient = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      if (clientModal === "create") {
        await a1osApi.clients.create(clientForm);
      } else {
        await a1osApi.clients.update(clientModal, clientForm);
      }
      setClientModal(null);
      await load();
    } catch (e) {
      setError(e.message || "Unable to save client");
    } finally {
      setSaving(false);
    }
  };

  const clientName = useMemo(
    () => Object.fromEntries(clients.map(c => [c.id, c.name])),
    [clients]
  );

  const dashboard = (
    <>
      <div className="hero">
        <div>
          <div className="eyebrow">WORKSPACE OVERVIEW</div>
          <h1>Good morning.</h1>
          <p>Manage your professional services operation from one control surface.</p>
        </div>
        <button className="primary" onClick={openProjectCreate}>+ New Project</button>
      </div>

      <div className="stats">
        <div className="stat"><span>Active Clients</span><strong>{clients.filter(c => c.status !== "inactive").length}</strong></div>
        <div className="stat"><span>Open Projects</span><strong>{activeProjects}</strong></div>
        <div className="stat"><span>Project Value</span><strong>{money(outstanding)}</strong></div>
        <div className="stat"><span>Completion</span><strong>{projects.length ? Math.round(projects.reduce((s,p)=>s+Number(p.progress||0),0)/projects.length) : 0}%</strong></div>
      </div>

      <section className="panel">
        <div className="panel-head">
          <div><h2>Active Projects</h2><span>Live A1OS project records</span></div>
          <button className="ghost" onClick={() => setPage("Projects")}>View all</button>
        </div>
        {projects.length === 0 ? (
          <div className="empty">No projects yet. Create the first project.</div>
        ) : (
          <div className="project-list">
            {projects.slice(0, 5).map(p => (
              <div className="project-row" key={p.id}>
                <div>
                  <b>{p.name}</b>
                  <span>{p.client_name || "No client"} · {p.service_type || "Professional Service"}</span>
                </div>
                <div className="project-value">{money(p.value_ugx)}</div>
                <div className="progress-wrap">
                  <div className="progress"><i style={{width:`${p.progress || 0}%`}} /></div>
                  <small>{p.progress || 0}%</small>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </>
  );

  const clientsPage = (
    <section className="panel">
      <div className="panel-head">
        <div><h2>Clients</h2><span>{clients.length} client records</span></div>
        <button className="primary" onClick={() => {setClientForm(emptyClient);setClientModal("create")}}>+ New Client</button>
      </div>
      {clients.length === 0 ? <div className="empty">No clients yet.</div> :
        <div className="table">
          {clients.map(c => (
            <div className="table-row" key={c.id}>
              <div><b>{c.name}</b><span>{c.company || "Independent client"}</span></div>
              <span>{c.email || "—"}</span>
              <span>{c.phone || "—"}</span>
              <button className="ghost" onClick={() => {setClientForm({name:c.name,email:c.email||"",phone:c.phone||"",company:c.company||""});setClientModal(c.id)}}>Edit</button>
            </div>
          ))}
        </div>
      }
    </section>
  );

  const projectsPage = (
    <section className="panel">
      <div className="panel-head">
        <div><h2>Projects</h2><span>{projects.length} project records</span></div>
        <button className="primary" onClick={openProjectCreate}>+ New Project</button>
      </div>
      {projects.length === 0 ? <div className="empty">No projects yet. Create the first one.</div> :
        <div className="table projects-table">
          {projects.map(p => (
            <div className="table-row project-table-row" key={p.id}>
              <div>
                <b>{p.name}</b>
                <span>{p.client_name || "No client"} · {p.service_type || "Professional Service"}</span>
              </div>
              <span className={`status ${p.status}`}>{p.status}</span>
              <span>{money(p.value_ugx)}</span>
              <span>{p.progress || 0}%</span>
              <div className="actions">
                <button className="ghost" onClick={() => openProjectEdit(p)}>Edit</button>
                <button className="danger" onClick={() => deleteProject(p.id)}>Delete</button>
              </div>
            </div>
          ))}
        </div>
      }
    </section>
  );

  const placeholder = (
    <section className="panel placeholder">
      <div className="eyebrow">MODULE READY</div>
      <h2>{page}</h2>
      <p>This workspace is registered in the Professional Services vertical. The next module can be connected to the same A1OS control plane.</p>
    </section>
  );

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><div className="brand-mark">A</div><div><b>A1OS</b><span>Professional Services</span></div></div>
        <div className="workspace">PROFESSIONAL SERVICES <span>⌄</span></div>
        <nav>{navItems.map(item => <button key={item} className={page===item?"active":""} onClick={()=>setPage(item)}>{item}</button>)}</nav>
        <div className="side-footer"><span>Managed by A1OS</span><small>Production</small></div>
      </aside>

      <main className="main">
        <header className="topbar"><div className="search">⌕ <span>Search workspace...</span></div><div className="top-actions"><span>◔</span><span>●</span></div></header>

        <div className="content">
          {error && <div className="error">{error}</div>}
          {loading ? <div className="loading">Loading workspace…</div> :
            page === "Dashboard" ? dashboard :
            page === "Clients" ? clientsPage :
            page === "Projects" ? projectsPage :
            placeholder}
        </div>
      </main>

      {projectModal && (
        <div className="modal-backdrop" onMouseDown={()=>setProjectModal(null)}>
          <form className="modal" onSubmit={saveProject} onMouseDown={e=>e.stopPropagation()}>
            <div className="modal-head"><div><h2>{projectModal==="create"?"New Project":"Edit Project"}</h2><span>Project record</span></div><button type="button" className="close" onClick={()=>setProjectModal(null)}>×</button></div>
            <label>Project name<input required value={projectForm.name} onChange={e=>setProjectForm({...projectForm,name:e.target.value})}/></label>
            <label>Client<select value={projectForm.client_id} onChange={e=>setProjectForm({...projectForm,client_id:e.target.value})}><option value="">No client</option>{clients.map(c=><option key={c.id} value={c.id}>{c.name}</option>)}</select></label>
            <div className="form-grid"><label>Service type<input value={projectForm.service_type} onChange={e=>setProjectForm({...projectForm,service_type:e.target.value})}/></label><label>Status<select value={projectForm.status} onChange={e=>setProjectForm({...projectForm,status:e.target.value})}><option value="active">Active</option><option value="on-hold">On hold</option><option value="completed">Completed</option></select></label></div>
            <div className="form-grid"><label>Value (UGX)<input type="number" min="0" value={projectForm.value_ugx} onChange={e=>setProjectForm({...projectForm,value_ugx:e.target.value})}/></label><label>Progress (%)<input type="number" min="0" max="100" value={projectForm.progress} onChange={e=>setProjectForm({...projectForm,progress:e.target.value})}/></label></div>
            <div className="form-grid"><label>Start date<input type="date" value={projectForm.start_date} onChange={e=>setProjectForm({...projectForm,start_date:e.target.value})}/></label><label>Due date<input type="date" value={projectForm.due_date} onChange={e=>setProjectForm({...projectForm,due_date:e.target.value})}/></label></div>
            <label>Description<textarea rows="3" value={projectForm.description} onChange={e=>setProjectForm({...projectForm,description:e.target.value})}/></label>
            <div className="modal-actions"><button type="button" className="ghost" onClick={()=>setProjectModal(null)}>Cancel</button><button className="primary" disabled={saving}>{saving?"Saving…":"Save Project"}</button></div>
          </form>
        </div>
      )}

      {clientModal && (
        <div className="modal-backdrop" onMouseDown={()=>setClientModal(null)}>
          <form className="modal" onSubmit={saveClient} onMouseDown={e=>e.stopPropagation()}>
            <div className="modal-head"><div><h2>{clientModal==="create"?"New Client":"Edit Client"}</h2><span>Client record</span></div><button type="button" className="close" onClick={()=>setClientModal(null)}>×</button></div>
            <label>Name<input required value={clientForm.name} onChange={e=>setClientForm({...clientForm,name:e.target.value})}/></label>
            <label>Company<input value={clientForm.company} onChange={e=>setClientForm({...clientForm,company:e.target.value})}/></label>
            <label>Email<input type="email" value={clientForm.email} onChange={e=>setClientForm({...clientForm,email:e.target.value})}/></label>
            <label>Phone<input value={clientForm.phone} onChange={e=>setClientForm({...clientForm,phone:e.target.value})}/></label>
            <div className="modal-actions"><button type="button" className="ghost" onClick={()=>setClientModal(null)}>Cancel</button><button className="primary" disabled={saving}>{saving?"Saving…":"Save Client"}</button></div>
          </form>
        </div>
      )}
    </div>
  );
}
