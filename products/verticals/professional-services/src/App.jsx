import React, { useEffect, useMemo, useState } from "react";
import { a1osApi } from "./api/client";
import "./styles.css";

const modules = [
  ["Dashboard","dashboard"],
  ["Clients","clients"],
  ["Projects","projects"],
  ["Quotes","quotes"],
  ["Invoices","invoices"],
  ["Payments","payments"],
  ["Tasks","tasks"],
  ["Documents","documents"],
  ["Reports","reports"],
  ["Settings","settings"],
];

const configs = {
  clients: {
    title:"Clients",
    fields:["name","email","phone","company","status"],
  },
  projects: {
    title:"Projects",
    fields:["name","client_id","status","description","budget","start_date","end_date"],
  },
  quotes: {
    title:"Quotes",
    fields:["client_id","title","description","amount","currency","status","valid_until"],
  },
  invoices: {
    title:"Invoices",
    fields:["client_id","quote_id","title","description","amount","paid_amount","currency","status","due_date"],
  },
  payments: {
    title:"Payments",
    fields:["invoice_id","amount","currency","method","reference"],
  },
  tasks: {
    title:"Tasks",
    fields:["title","description","status","priority","due_date"],
  },
  documents: {
    title:"Documents",
    fields:["name","description","document_type","url"],
  },
  settings: {
    title:"Settings",
    fields:["key","value"],
  },
};

function App() {
  const [page,setPage]=useState("dashboard");
  const [data,setData]=useState({});
  const [busy,setBusy]=useState(false);
  const [error,setError]=useState("");

  const load = async (p=page) => {
    setError("");
    if (p==="dashboard") {
      const [clients,projects,quotes,invoices,payments,tasks] =
        await Promise.all([
          a1osApi.clients.list(),
          a1osApi.projects.list(),
          a1osApi.quotes.list(),
          a1osApi.invoices.list(),
          a1osApi.payments.list(),
          a1osApi.tasks.list(),
        ]);
      setData({clients,projects,quotes,invoices,payments,tasks});
      return;
    }

    if (p==="reports") {
      const [financial,receivables]=await Promise.all([
        a1osApi.reports.financial(),
        a1osApi.reports.receivables(),
      ]);
      setData({financial,receivables});
      return;
    }

    if (p==="audit") {
      setData(await a1osApi.audit());
      return;
    }

    if (configs[p]) setData(await a1osApi[p].list());
  };

  useEffect(()=>{ load().catch(e=>setError(e.message)); },[page]);

  const stats=useMemo(()=>({
    clients:data.clients?.count ?? 0,
    projects:data.projects?.count ?? 0,
    quotes:data.quotes?.count ?? 0,
    invoices:data.invoices?.count ?? 0,
    payments:data.payments?.count ?? 0,
    tasks:data.tasks?.count ?? 0,
  }),[data]);

  const create = async (resource) => {
    const cfg=configs[resource];
    const values={};

    for (const field of cfg.fields) {
      const value=window.prompt(`Enter ${field.replaceAll("_"," ")}`);
      if (value!==null && value!=="") values[field]=value;
    }

    if (!Object.keys(values).length) return;

    setBusy(true);
    try {
      await a1osApi[resource].create(values);
      await load(resource);
    } catch(e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  const remove = async (resource,id) => {
    if (!window.confirm("Delete this record?")) return;
    setBusy(true);
    try {
      await a1osApi[resource].remove(id);
      await load(resource);
    } catch(e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="app">
      <aside>
        <div className="brand">
          <strong>A1OS</strong>
          <span>Professional Services</span>
        </div>

        <nav>
          {modules.map(([label,key])=>(
            <button
              key={key}
              className={page===key?"active":""}
              onClick={()=>setPage(key)}
            >
              {label}
            </button>
          ))}
        </nav>

        <button className="audit" onClick={()=>setPage("audit")}>
          Audit Log
        </button>
      </aside>

      <main>
        <header>
          <div>
            <small>A1OS / PROFESSIONAL SERVICES</small>
            <h1>{page==="dashboard"?"Dashboard":page==="audit"?"Audit Log":configs[page]?.title}</h1>
          </div>
          {configs[page] &&
            <button className="primary" onClick={()=>create(page)} disabled={busy}>
              + Create
            </button>
          }
        </header>

        {error && <div className="error">{error}</div>}

        {page==="dashboard" && (
          <>
            <section className="stats">
              <Card label="Clients" value={stats.clients}/>
              <Card label="Projects" value={stats.projects}/>
              <Card label="Quotes" value={stats.quotes}/>
              <Card label="Invoices" value={stats.invoices}/>
              <Card label="Payments" value={stats.payments}/>
              <Card label="Tasks" value={stats.tasks}/>
            </section>

            <section className="panel">
              <h2>Operations</h2>
              <p>Live operational data from the A1OS platform API.</p>
            </section>
          </>
        )}

        {configs[page] && (
          <CrudView
            resource={page}
            payload={data}
            onDelete={remove}
          />
        )}

        {page==="reports" && (
          <section className="grid">
            <section className="panel">
              <h2>Financial</h2>
              <pre>{JSON.stringify(data.financial ?? {},null,2)}</pre>
            </section>
            <section className="panel">
              <h2>Receivables</h2>
              <pre>{JSON.stringify(data.receivables ?? {},null,2)}</pre>
            </section>
          </section>
        )}

        {page==="audit" && (
          <section className="panel">
            <pre>{JSON.stringify(data,null,2)}</pre>
          </section>
        )}
      </main>
    </div>
  );
}

function Card({label,value}) {
  return <div className="card"><span>{label}</span><strong>{value}</strong></div>;
}

function CrudView({resource,payload,onDelete}) {
  const rows=payload?.[resource] ?? [];

  if (!rows.length)
    return <section className="panel empty">No {configs[resource].title.toLowerCase()} records.</section>;

  const columns=Object.keys(rows[0]).filter(k=>!["tenant_id","created_at","updated_at"].includes(k));

  return (
    <section className="panel table-wrap">
      <table>
        <thead>
          <tr>
            {columns.map(c=><th key={c}>{c.replaceAll("_"," ")}</th>)}
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(row=>(
            <tr key={row.id}>
              {columns.map(c=><td key={c}>{String(row[c] ?? "")}</td>)}
              <td>
                <button className="danger" onClick={()=>onDelete(resource,row.id)}>
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}

export { App };
