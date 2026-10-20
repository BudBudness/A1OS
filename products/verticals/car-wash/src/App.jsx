import React, { useEffect, useState } from "react";
import { api, getErrorMessage } from "./api/client.js";

const navItems = [
  ["overview", "Overview"],
  ["queue", "Vehicle queue"],
  ["services", "Wash services"],
  ["parking", "Parking"],
  ["customers", "Customers"],
  ["payments", "Payments & receipts"],
  ["inventory", "Inventory"],
  ["expenses", "Expenses"],
  ["reports", "Reports"]
];

const blankVehicle = { registration: "", customerName: "", phone: "", service: "standard-wash", notes: "" };

export function App() {
  const [section, setSection] = useState("overview");
  const [summary, setSummary] = useState(null);
  const [queue, setQueue] = useState([]);
  const [parking, setParking] = useState([]);
  const [services, setServices] = useState([]);
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showIntake, setShowIntake] = useState(false);
  const [showServiceForm, setShowServiceForm] = useState(false);
  const [showParkingForm, setShowParkingForm] = useState(false);
  const [showPaymentForm, setShowPaymentForm] = useState(false);
  const [serviceForm, setServiceForm] = useState({ id: "standard-wash", name: "Standard wash", price: "" });
  const [parkingForm, setParkingForm] = useState({ registration: "", customerName: "", customerPhone: "", parkingType: "day", expectedCheckoutAt: "", notes: "" });
  const [paymentForm, setPaymentForm] = useState({ vehicleId: "", amount: "", method: "cash", reference: "" });
  const [vehicle, setVehicle] = useState(blankVehicle);
  const [saving, setSaving] = useState(false);
  const [notice, setNotice] = useState("");

  async function loadData() {
    setLoading(true);
    setError("");
    try {
      const [dashboard, queueResult, parkingResult, serviceResult, paymentResult] = await Promise.all([
        api.get("/car-wash/dashboard"),
        api.get("/car-wash/vehicles?status=active"),
        api.get("/car-wash/parking?status=active"),
        api.get("/car-wash/services"),
        api.get("/car-wash/payments")
      ]);
      setSummary(dashboard);
      setQueue(Array.isArray(queueResult?.items) ? queueResult.items : []);
      setParking(Array.isArray(parkingResult?.items) ? parkingResult.items : []);
      setServices(Array.isArray(serviceResult?.items) ? serviceResult.items : []);
      setPayments(Array.isArray(paymentResult?.items) ? paymentResult.items : []);
    } catch (e) {
      setError(getErrorMessage(e));
      setSummary(null);
      setQueue([]);
      setParking([]);
      setServices([]);
      setPayments([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadData(); }, []);

  async function submitIntake(event) {
    event.preventDefault();
    setSaving(true);
    setError("");
    setNotice("");
    try {
      await api.post("/car-wash/vehicles", {
        registration: vehicle.registration.trim().toUpperCase(),
        customer: { name: vehicle.customerName.trim(), phone: vehicle.phone.trim() },
        serviceId: vehicle.service,
        notes: vehicle.notes.trim() || null
      });
      setVehicle(blankVehicle);
      setShowIntake(false);
      setNotice("Vehicle intake saved.");
      await loadData();
    } catch (e) {
      setError(getErrorMessage(e));
    } finally {
      setSaving(false);
    }
  }

  async function submitService(event) {
    event.preventDefault();
    setSaving(true);
    setError("");
    setNotice("");
    try {
      const id = serviceForm.id.trim().toLowerCase();
      const name = serviceForm.name.trim();
      const price = Number(serviceForm.price);
      if (!/^[a-z0-9][a-z0-9-]{1,47}$/.test(id) || !name || !Number.isFinite(price) || price <= 0) {
        throw new Error("Enter a valid service code, name and positive price.");
      }
      await api.post("/car-wash/services", { id, name, price });
      setShowServiceForm(false);
      setServiceForm({ id: "", name: "", price: "" });
      setNotice("Wash service saved to the A1OS Platform.");
      await loadData();
    } catch (e) {
      setError(e?.message === "AUTH_REQUIRED" || e?.message === "ACCESS_DENIED" ? getErrorMessage(e) : e?.message || getErrorMessage(e));
    } finally {
      setSaving(false);
    }
  }

  async function submitParking(event) {
    event.preventDefault();
    setSaving(true);
    setError("");
    setNotice("");
    try {
      await api.post("/car-wash/parking", {
        registration: parkingForm.registration.trim().toUpperCase(),
        customerName: parkingForm.customerName.trim(),
        customerPhone: parkingForm.customerPhone.trim() || null,
        parkingType: parkingForm.parkingType,
        expectedCheckoutAt: parkingForm.expectedCheckoutAt || null,
        notes: parkingForm.notes.trim() || null
      });
      setParkingForm({ registration: "", customerName: "", customerPhone: "", parkingType: "day", expectedCheckoutAt: "", notes: "" });
      setShowParkingForm(false);
      setNotice("Parking entry saved.");
      await loadData();
    } catch (e) {
      setError(getErrorMessage(e));
    } finally {
      setSaving(false);
    }
  }

  async function submitPayment(event) {
    event.preventDefault();
    setSaving(true);
    setError("");
    setNotice("");
    try {
      await api.post("/car-wash/payments", {
        vehicleId: Number(paymentForm.vehicleId),
        amount: Number(paymentForm.amount),
        method: paymentForm.method,
        reference: paymentForm.reference.trim() || null
      });
      setPaymentForm({ vehicleId: "", amount: "", method: "cash", reference: "" });
      setShowPaymentForm(false);
      setNotice("Payment recorded.");
      await loadData();
    } catch (e) {
      setError(getErrorMessage(e));
    } finally {
      setSaving(false);
    }
  }

  async function updateVehicleStatus(vehicleId, status) {
    setError("");
    setNotice("");
    try {
      await api.patch(`/car-wash/vehicles/${vehicleId}`, { status });
      setNotice("Vehicle status updated.");
      await loadData();
    } catch (e) {
      setError(getErrorMessage(e));
    }
  }

  async function checkoutParking(parkingId) {
    setError("");
    setNotice("");
    try {
      await api.patch(`/car-wash/parking/${parkingId}`, { status: "checked_out" });
      setNotice("Parking checkout recorded.");
      await loadData();
    } catch (e) {
      setError(getErrorMessage(e));
    }
  }

  function openPaymentForVehicle(vehicleId) {
    setPaymentForm({ vehicleId: String(vehicleId), amount: "", method: "cash", reference: "" });
    setSection("payments");
    setShowPaymentForm(true);
  }

  const money = (value) => new Intl.NumberFormat("en-UG", {
    style: "currency", currency: "UGX", maximumFractionDigits: 0
  }).format(Number(value || 0));

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="#overview" onClick={() => setSection("overview")}>
          <span className="brand-icon">J</span>
          <span><strong>JERE'S</strong><small>CAR WASH & PARKING</small></span>
        </a>
        <div className="branch-label"><span className="live-dot" /> NSAMBYA BRANCH</div>
        <nav aria-label="Main navigation">
          {navItems.map(([id, label], index) => (
            <button key={id} className={section === id ? "nav-item active" : "nav-item"} onClick={() => setSection(id)}>
              <span className="nav-number">{String(index + 1).padStart(2, "0")}</span>{label}
            </button>
          ))}
        </nav>
        <div className="sidebar-foot"><span className="shield">◆</span><span>SECURED BY A1OS<small>Identity · Access · Audit</small></span></div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div><p className="eyebrow">OPERATIONS / KAMPALA</p><h1>{navItems.find(([id]) => id === section)?.[1] || "Overview"}</h1></div>
          <div className="top-actions"><span className="today">{new Date().toLocaleDateString("en-UG", { weekday: "short", day: "2-digit", month: "short", year: "numeric" })}</span><button className="btn secondary" onClick={loadData} disabled={loading}>↻ Refresh</button><button className="btn primary" onClick={() => { setShowIntake(true); setSection("queue"); }}>+ Vehicle intake</button></div>
        </header>

        {error && <div className="alert" role="alert"><strong>Operations unavailable</strong><span>{error}</span><button onClick={loadData}>Retry</button></div>}
        {notice && <div className="notice" role="status">{notice}</div>}

        {section === "overview" && <>
          <section className="welcome"><div><p className="eyebrow">DAILY OPERATIONS</p><h2>Keep every vehicle moving.</h2><p>One view for washing, parking, payments and the team.</p></div><div className="capacity"><span>WASH BAY CAPACITY</span><strong>{queue.filter(v => ["washing", "in-progress"].includes(v.status)).length}<small> / 4 active bays</small></strong><div className="capacity-track"><span style={{ width: `${Math.min(100, queue.filter(v => ["washing", "in-progress"].includes(v.status)).length / 4 * 100)}%` }} /></div></div></section>
          <section className="metrics" aria-label="Daily metrics">
            <Metric label="Vehicles today" value={summary?.vehiclesToday ?? "—"} note="Wash intake" />
            <Metric label="Active wash queue" value={queue.length} note="Current active records" />
            <Metric label="Parking occupancy" value={parking.length} note="Day + overnight" />
            <Metric label="Revenue today" value={summary ? money(summary.revenueToday) : "—"} note="Recorded payments" />
          </section>
          <section className="content-grid"><div className="panel"><div className="panel-head"><div><p className="eyebrow">LIVE WORK</p><h3>Vehicle queue</h3></div><button className="text-button" onClick={() => setSection("queue")}>View queue →</button></div><QueueTable items={queue.slice(0, 5)} money={money} onStatusChange={updateVehicleStatus} onPayment={openPaymentForVehicle} /></div>
          <div className="panel"><div className="panel-head"><div><p className="eyebrow">PARKING</p><h3>On site now</h3></div><button className="text-button" onClick={() => setSection("parking")}>View parking →</button></div><ParkingList items={parking.slice(0, 5)} /></div></section>
        </>}

        {section === "services" && <section className="panel"><div className="panel-head"><div><p className="eyebrow">PRICE LIST</p><h3>Wash services</h3></div><button className="btn primary" onClick={() => { setServiceForm({ id: "", name: "", price: "" }); setShowServiceForm(true); }}>+ Add service</button></div>{services.length === 0 ? <div className="empty"><span>¤</span><strong>No wash services configured</strong><p>Add the actual service names and prices before accepting vehicle intake.</p></div> : <div className="table-wrap"><table><thead><tr><th>Service</th><th>Service code</th><th>Price (UGX)</th></tr></thead><tbody>{services.map(s => <tr key={s.id}><td><strong>{s.name}</strong></td><td>{s.id}</td><td>{money(s.price)}</td></tr>)}</tbody></table></div>}</section>}
        {section === "queue" && <section className="panel"><div className="panel-head"><div><p className="eyebrow">WASH FLOOR</p><h3>Vehicle queue</h3></div><button className="btn primary" onClick={() => setShowIntake(true)}>+ Vehicle intake</button></div><QueueTable items={queue} money={money} onStatusChange={updateVehicleStatus} onPayment={openPaymentForVehicle} /></section>}
        {section === "parking" && <section className="panel"><div className="panel-head"><div><p className="eyebrow">DAY & OVERNIGHT</p><h3>Parking register</h3></div><button className="btn primary" onClick={() => setShowParkingForm(true)}>+ Parking intake</button></div><ParkingList items={parking} onCheckout={checkoutParking} /></section>}
        {section === "payments" && <section className="panel"><div className="panel-head"><div><p className="eyebrow">CASH CONTROL</p><h3>Payments & receipts</h3></div><button className="btn primary" disabled={!queue.length} onClick={() => openPaymentForVehicle(queue[0].id)}>+ Record payment</button></div>{payments.length === 0 ? <div className="empty"><span>¤</span><strong>No payments recorded</strong><p>Record a payment against an active vehicle to start the receipt ledger.</p></div> : <div className="table-wrap"><table><thead><tr><th>Vehicle</th><th>Amount</th><th>Method</th><th>Reference</th><th>Recorded</th></tr></thead><tbody>{payments.map(p => <tr key={p.id}><td>{p.registration || `Vehicle #${p.vehicle_id}`}</td><td>{money(p.amount)}</td><td>{p.method}</td><td>{p.reference || "—"}</td><td>{String(p.created_at || "").replace("T", " ").slice(0, 16)}</td></tr>)}</tbody></table></div>}</section>}
        {["customers", "inventory", "expenses", "reports"].includes(section) && <section className="panel coming"><span className="coming-mark">A1</span><p className="eyebrow">PLATFORM INTEGRATION REQUIRED</p><h3>{navItems.find(([id]) => id === section)?.[1]}</h3><p>This module becomes operational when its authorized A1OS Platform API resource is connected. No demo or fabricated records are shown.</p></section>}
        {loading && <p className="loading" role="status">Synchronizing with A1OS Platform…</p>}

        <footer><span>Jere's Car Wash & Parking</span><span>Nsambya Road Railway Grounds, Kampala, Uganda</span><span>© {new Date().getFullYear()} · A1OS Platform</span></footer>
      </main>

      {showParkingForm && <div className="modal-backdrop" role="presentation" onMouseDown={(e) => { if (e.target === e.currentTarget) setShowParkingForm(false); }}><section className="modal" role="dialog" aria-modal="true" aria-labelledby="parking-title"><div className="modal-head"><div><p className="eyebrow">PARKING REGISTER</p><h2 id="parking-title">New parking entry</h2></div><button className="icon-button" onClick={() => setShowParkingForm(false)} aria-label="Close parking form">×</button></div><form onSubmit={submitParking}><label>Registration number<input required maxLength="16" value={parkingForm.registration} onChange={e => setParkingForm({ ...parkingForm, registration: e.target.value })} placeholder="e.g. UBA 123X" /></label><label>Customer name<input required maxLength="120" value={parkingForm.customerName} onChange={e => setParkingForm({ ...parkingForm, customerName: e.target.value })} /></label><label>Phone (optional)<input maxLength="24" inputMode="tel" value={parkingForm.customerPhone} onChange={e => setParkingForm({ ...parkingForm, customerPhone: e.target.value })} /></label><div className="form-row"><label>Parking type<select value={parkingForm.parkingType} onChange={e => setParkingForm({ ...parkingForm, parkingType: e.target.value })}><option value="day">Day parking</option><option value="overnight">Overnight parking</option></select></label><label>Expected checkout<input type="datetime-local" value={parkingForm.expectedCheckoutAt} onChange={e => setParkingForm({ ...parkingForm, expectedCheckoutAt: e.target.value })} /></label></div><label>Notes (optional)<textarea rows="2" maxLength="500" value={parkingForm.notes} onChange={e => setParkingForm({ ...parkingForm, notes: e.target.value })} /></label><p className="form-note">Parking charges are not collected by this form; record payment through the platform payment workflow.</p><div className="modal-actions"><button type="button" className="btn secondary" onClick={() => setShowParkingForm(false)}>Cancel</button><button className="btn primary" type="submit" disabled={saving}>{saving ? "Saving…" : "Save parking entry"}</button></div></form></section></div>}
      {showPaymentForm && <div className="modal-backdrop" role="presentation" onMouseDown={(e) => { if (e.target === e.currentTarget) setShowPaymentForm(false); }}><section className="modal" role="dialog" aria-modal="true" aria-labelledby="payment-title"><div className="modal-head"><div><p className="eyebrow">PAYMENT RECORD</p><h2 id="payment-title">Record vehicle payment</h2></div><button className="icon-button" onClick={() => setShowPaymentForm(false)} aria-label="Close payment form">×</button></div><form onSubmit={submitPayment}><label>Vehicle<select required value={paymentForm.vehicleId} onChange={e => setPaymentForm({ ...paymentForm, vehicleId: e.target.value })}><option value="">Select active vehicle</option>{queue.map(v => <option key={v.id} value={v.id}>{v.registration} · {v.customer?.name || "Customer"} · {money(v.price)}</option>)}</select></label><label>Amount (UGX)<input required type="number" min="1" step="1" value={paymentForm.amount} onChange={e => setPaymentForm({ ...paymentForm, amount: e.target.value })} /></label><label>Payment method<select value={paymentForm.method} onChange={e => setPaymentForm({ ...paymentForm, method: e.target.value })}><option value="cash">Cash</option><option value="mobile_money">Mobile money</option><option value="bank_transfer">Bank transfer</option><option value="card">Card</option><option value="other">Other</option></select></label><label>Reference (optional)<input maxLength="120" value={paymentForm.reference} onChange={e => setPaymentForm({ ...paymentForm, reference: e.target.value })} /></label><p className="form-note">The platform rejects payments that exceed the configured wash-service balance.</p><div className="modal-actions"><button type="button" className="btn secondary" onClick={() => setShowPaymentForm(false)}>Cancel</button><button className="btn primary" type="submit" disabled={saving || !queue.length}>{saving ? "Saving…" : "Record payment"}</button></div></form></section></div>}
      {showServiceForm && <div className="modal-backdrop" role="presentation" onMouseDown={(e) => { if (e.target === e.currentTarget) setShowServiceForm(false); }}><section className="modal" role="dialog" aria-modal="true" aria-labelledby="service-title"><div className="modal-head"><div><p className="eyebrow">SERVICE CATALOGUE</p><h2 id="service-title">Configure wash service</h2></div><button className="icon-button" onClick={() => setShowServiceForm(false)} aria-label="Close service form">×</button></div><form onSubmit={submitService}><label>Service code<input required maxLength="48" pattern="[a-z0-9][a-z0-9-]{1,47}" value={serviceForm.id} onChange={e => setServiceForm({ ...serviceForm, id: e.target.value })} placeholder="e.g. standard-wash" /><small>Use lowercase letters, numbers and hyphens.</small></label><label>Service name<input required maxLength="100" value={serviceForm.name} onChange={e => setServiceForm({ ...serviceForm, name: e.target.value })} placeholder="e.g. Standard wash" /></label><label>Price (UGX)<input required type="number" min="1" step="1" value={serviceForm.price} onChange={e => setServiceForm({ ...serviceForm, price: e.target.value })} placeholder="Enter actual price" /></label><p className="form-note">Prices are saved per A1OS organization. Only configured services can be used for new vehicle intake.</p><div className="modal-actions"><button type="button" className="btn secondary" onClick={() => setShowServiceForm(false)}>Cancel</button><button className="btn primary" type="submit" disabled={saving}>{saving ? "Saving…" : "Save service"}</button></div></form></section></div>}
      {showIntake && <div className="modal-backdrop" role="presentation" onMouseDown={(e) => { if (e.target === e.currentTarget) setShowIntake(false); }}><section className="modal" role="dialog" aria-modal="true" aria-labelledby="intake-title"><div className="modal-head"><div><p className="eyebrow">NEW RECORD</p><h2 id="intake-title">Vehicle intake</h2></div><button className="icon-button" onClick={() => setShowIntake(false)} aria-label="Close intake">×</button></div>
        <form onSubmit={submitIntake}><label>Registration number<input required maxLength="16" value={vehicle.registration} onChange={e => setVehicle({ ...vehicle, registration: e.target.value })} placeholder="e.g. UBA 123X" /></label><div className="form-row"><label>Customer name<input required maxLength="120" value={vehicle.customerName} onChange={e => setVehicle({ ...vehicle, customerName: e.target.value })} /></label><label>Phone number<input required maxLength="24" inputMode="tel" value={vehicle.phone} onChange={e => setVehicle({ ...vehicle, phone: e.target.value })} placeholder="+256…" /></label></div><label>Service<select value={vehicle.service} onChange={e => setVehicle({ ...vehicle, service: e.target.value })}><option value="standard-wash">Standard wash</option>{services.map(s => <option key={s.id} value={s.id}>{s.name} — {money(s.price)}</option>)}</select></label><label>Notes (optional)<textarea rows="3" maxLength="500" value={vehicle.notes} onChange={e => setVehicle({ ...vehicle, notes: e.target.value })} /></label><p className="form-note">Records are saved to the A1OS Platform API. They are not stored locally.</p><div className="modal-actions"><button type="button" className="btn secondary" onClick={() => setShowIntake(false)}>Cancel</button><button className="btn primary" type="submit" disabled={saving || loading}>{saving ? "Saving…" : "Save intake"}</button></div></form></section></div>}
    </div>
  );
}

function Metric({ label, value, note }) {
  return <article className="metric"><span>{label}</span><strong>{value}</strong><small>{note}</small></article>;
}

function QueueTable({ items, money, onStatusChange, onPayment }) {
  if (!items.length) return <div className="empty"><span>▤</span><strong>No vehicle records available</strong><p>Connect to the A1OS Platform API to load the live queue.</p></div>;
  const nextStatuses = { queued: ["washing", "cancelled"], washing: ["in-progress", "completed", "cancelled"], "in-progress": ["completed", "cancelled"], completed: [], cancelled: [] };
  return <div className="table-wrap"><table><thead><tr><th>Vehicle</th><th>Service</th><th>Status</th><th>Price</th><th>Actions</th></tr></thead><tbody>{items.map((v) => <tr key={v.id}><td><strong>{v.registration}</strong><small>{v.customer?.name || v.customerName || "Customer not provided"}</small></td><td>{v.service?.name || v.serviceName || "Wash"}</td><td><span className={`status ${String(v.status || "queued").toLowerCase()}`}>{v.status || "queued"}</span></td><td>{money(v.price ?? v.service?.price)}</td><td><div className="row-actions"><select aria-label={`Update status for ${v.registration}`} value="" disabled={!nextStatuses[v.status]?.length} onChange={e => { if (e.target.value) onStatusChange?.(v.id, e.target.value); }}><option value="">Update status</option>{(nextStatuses[v.status] || []).map(status => <option key={status} value={status}>{status}</option>)}</select><button className="text-button" onClick={() => onPayment?.(v.id)}>Payment</button></div></td></tr>)}</tbody></table></div>;
}

function ParkingList({ items, onCheckout }) {
  if (!items.length) return <div className="empty"><span>▦</span><strong>No active parking records</strong><p>Create a parking entry to start tracking day and overnight occupancy.</p></div>;
  return <div className="parking-list">{items.map(p => <div className="parking-row" key={p.id}><span className="car-mark">P</span><div><strong>{p.registration}</strong><small>{p.customerName || p.customer?.name || "Customer"} · {p.period || p.type || "Parking"}</small></div><span className="status">{p.status || "parked"}</span><button className="text-button" onClick={() => onCheckout?.(p.id)}>Check out</button></div>)}</div>;
}
