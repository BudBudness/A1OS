'use client';

import { FormEvent, useEffect, useMemo, useState } from 'react';

const API_BASE = (process.env.NEXT_PUBLIC_A1OS_API_BASE_URL || 'http://localhost:3013').replace(/\/$/, '');

type StaffUser = {
  id: number;
  full_name: string;
  email: string;
  role: string;
  permissions: string[];
};

type Resource = {
  key: string;
  label: string;
  read: string;
  write: string;
  fields: { key: string; label: string; required?: boolean; type?: string; placeholder?: string }[];
};

const RESOURCES: Resource[] = [
  { key: 'programs', label: 'Programs', read: 'charity:programs:read', write: 'charity:programs:write', fields: [
    { key: 'code', label: 'Program code', required: true }, { key: 'name', label: 'Program name', required: true },
    { key: 'description', label: 'Description' }, { key: 'start_date', label: 'Start date', type: 'date' },
    { key: 'end_date', label: 'End date', type: 'date' },
  ]},
  { key: 'beneficiaries', label: 'Beneficiaries', read: 'charity:beneficiaries:read', write: 'charity:beneficiaries:write', fields: [
    { key: 'beneficiary_ref', label: 'Beneficiary reference', required: true },
    { key: 'vulnerability_category', label: 'Support category', required: true },
    { key: 'household_ref', label: 'Household reference' }, { key: 'party_id', label: 'Existing party ID', type: 'number' },
    { key: 'restricted_attributes_json', label: 'Restricted attributes (JSON)', placeholder: '{}' },
  ]},
  { key: 'cases', label: 'Case management', read: 'charity:cases:read', write: 'charity:cases:write', fields: [
    { key: 'case_ref', label: 'Case reference', required: true }, { key: 'beneficiary_id', label: 'Beneficiary ID', required: true, type: 'number' },
    { key: 'program_id', label: 'Program ID', type: 'number' }, { key: 'case_type', label: 'Case type', required: true },
    { key: 'priority', label: 'Priority (low/normal/high/urgent)' }, { key: 'summary', label: 'Case summary', required: true },
    { key: 'restricted_notes', label: 'Restricted notes' },
  ]},
  { key: 'aid-allocations', label: 'Aid allocations', read: 'charity:aid:read', write: 'charity:aid:write', fields: [
    { key: 'allocation_ref', label: 'Allocation reference', required: true },
    { key: 'beneficiary_id', label: 'Beneficiary ID', required: true, type: 'number' },
    { key: 'case_id', label: 'Case ID', type: 'number' }, { key: 'program_id', label: 'Program ID', type: 'number' },
    { key: 'aid_type', label: 'Aid type', required: true }, { key: 'description', label: 'Description', required: true },
    { key: 'quantity', label: 'Quantity', type: 'number' }, { key: 'amount_ugx', label: 'Amount (UGX)', type: 'number' },
    { key: 'evidence_ref', label: 'Evidence reference' },
  ]},
  { key: 'donors', label: 'Donors', read: 'charity:donors:read', write: 'charity:donors:write', fields: [
    { key: 'donor_ref', label: 'Donor reference', required: true }, { key: 'party_id', label: 'Existing party ID', type: 'number' },
    { key: 'donor_type', label: 'Donor type (individual/organization/anonymous)' },
    { key: 'consent_to_contact', label: 'Consent to contact (0/1)', type: 'number' },
  ]},
  { key: 'donation-intents', label: 'Donation intents', read: 'charity:donations:read', write: 'charity:donations:write', fields: [
    { key: 'intent_ref', label: 'Intent reference', required: true }, { key: 'donor_id', label: 'Donor ID', type: 'number' },
    { key: 'program_id', label: 'Program ID', type: 'number' }, { key: 'amount_ugx', label: 'Amount (UGX)', required: true, type: 'number' },
    { key: 'channel', label: 'Channel' }, { key: 'idempotency_key', label: 'Idempotency key' },
  ]},
  { key: 'volunteers', label: 'Volunteers', read: 'charity:volunteers:read', write: 'charity:volunteers:write', fields: [
    { key: 'volunteer_ref', label: 'Volunteer reference', required: true }, { key: 'party_id', label: 'Existing party ID', type: 'number' },
    { key: 'skills_json', label: 'Skills (JSON array)', placeholder: '[]' }, { key: 'availability_json', label: 'Availability (JSON)', placeholder: '{}' },
  ]},
  { key: 'partnerships', label: 'Partnerships', read: 'charity:partnerships:read', write: 'charity:partnerships:write', fields: [
    { key: 'partnership_ref', label: 'Partnership reference', required: true }, { key: 'partnership_type', label: 'Partnership type', required: true },
    { key: 'party_id', label: 'Existing party ID', type: 'number' }, { key: 'agreement_ref', label: 'Agreement reference' },
    { key: 'start_date', label: 'Start date', type: 'date' }, { key: 'end_date', label: 'End date', type: 'date' }, { key: 'notes', label: 'Notes' },
  ]},
  { key: 'outreach-reports', label: 'Outreach reports', read: 'charity:reports:read', write: 'charity:reports:write', fields: [
    { key: 'report_ref', label: 'Report reference', required: true }, { key: 'program_id', label: 'Program ID', type: 'number' },
    { key: 'event_name', label: 'Activity name', required: true }, { key: 'event_date', label: 'Activity date', required: true, type: 'date' },
    { key: 'location', label: 'Location' }, { key: 'people_reached', label: 'People reached', type: 'number' },
    { key: 'summary', label: 'Outcome summary', required: true }, { key: 'evidence_refs_json', label: 'Evidence references (JSON array)', placeholder: '[]' },
  ]},
];

const NUMERIC_FIELDS = new Set(['party_id', 'beneficiary_id', 'program_id', 'case_id', 'donor_id', 'amount_ugx', 'quantity', 'people_reached', 'consent_to_contact']);

export default function CharityAdminPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [token, setToken] = useState('');
  const [user, setUser] = useState<StaffUser | null>(null);
  const [selected, setSelected] = useState('programs');
  const [items, setItems] = useState<Record<string, unknown>[]>([]);
  const [values, setValues] = useState<Record<string, string>>({});
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [busy, setBusy] = useState(false);

  const can = (permission: string) => Boolean(user && (user.permissions.includes('*') || user.permissions.includes(permission)));
  const allowed = useMemo(() => RESOURCES.filter((resource) => can(resource.read)), [user]);
  const current = RESOURCES.find((resource) => resource.key === selected) || RESOURCES[0];
  const canWrite = can(current.write);

  useEffect(() => {
    if (!token || !user || !can(current.read)) {
      setItems([]);
      return;
    }
    let active = true;
    (async () => {
      try {
        const response = await fetch(`${API_BASE}/v1/charity/${current.key}`, {
          headers: { Authorization: `Bearer ${token}` },
          cache: 'no-store',
        });
        const body = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(body.detail || `Load failed (${response.status})`);
        if (active) setItems(body.items || []);
      } catch (e) {
        if (active) setError(e instanceof Error ? e.message : 'Unable to load records');
      }
    })();
    return () => { active = false; };
  }, [token, user, selected]);

  async function signIn(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true); setError(''); setNotice('');
    try {
      const response = await fetch(`${API_BASE}/v1/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      const body = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(body.detail || 'Sign-in failed');
      setToken(body.token);
      setUser(body.user);
      setPassword('');
      const first = RESOURCES.find((resource) => body.user.permissions.includes('*') || body.user.permissions.includes(resource.read));
      if (first) setSelected(first.key);
      setNotice('Signed in. Session token is kept in memory for this browser tab only.');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Sign-in failed');
    } finally {
      setBusy(false);
    }
  }

  async function createRecord(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !canWrite) return;
    setBusy(true); setError(''); setNotice('');
    const payload: Record<string, unknown> = {};
    for (const field of current.fields) {
      const raw = (values[field.key] || '').trim();
      if (!raw) continue;
      payload[field.key] = NUMERIC_FIELDS.has(field.key) ? Number(raw) : raw;
    }
    try {
      const response = await fetch(`${API_BASE}/v1/charity/${current.key}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify(payload),
      });
      const body = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail || body));
      setValues({});
      setNotice(`Created ${current.label.toLowerCase()} record #${body.id}. Initial workflow status is assigned by the server.`);
      const refreshed = await fetch(`${API_BASE}/v1/charity/${current.key}`, { headers: { Authorization: `Bearer ${token}` }, cache: 'no-store' });
      const result = await refreshed.json().catch(() => ({}));
      if (refreshed.ok) setItems(result.items || []);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Create failed');
    } finally {
      setBusy(false);
    }
  }

  async function signOut() {
    try {
      await fetch(`${API_BASE}/v1/auth/logout`, { method: 'POST', headers: { Authorization: `Bearer ${token}` } });
    } finally {
      setToken(''); setUser(null); setItems([]); setValues({}); setNotice('Signed out.');
    }
  }

  if (!token || !user) {
    return (
      <main className="min-h-screen bg-[#0a0a0a] px-5 py-12 text-white">
        <div className="mx-auto max-w-md rounded-3xl border border-white/10 bg-white/[0.04] p-8">
          <a href="/" className="text-sm font-bold uppercase tracking-[0.25em] text-[#d62828]">Stramos Wisdom Charity</a>
          <h1 className="mt-6 text-3xl font-black">Staff portal</h1>
          <p className="mt-3 text-sm leading-6 text-white/65">Sign in with an A1OS platform account. Access is controlled by server-side permissions.</p>
          <form className="mt-7 space-y-4" onSubmit={signIn}>
            <label className="block text-sm">Email
              <input className="mt-2 w-full rounded-xl border border-white/15 bg-black px-4 py-3" type="email" autoComplete="username" required value={email} onChange={(e) => setEmail(e.target.value)} />
            </label>
            <label className="block text-sm">Password
              <input className="mt-2 w-full rounded-xl border border-white/15 bg-black px-4 py-3" type="password" autoComplete="current-password" required value={password} onChange={(e) => setPassword(e.target.value)} />
            </label>
            {error && <p role="alert" className="rounded-xl bg-red-950 p-3 text-sm text-red-200">{error}</p>}
            <button disabled={busy} className="w-full rounded-xl bg-[#d62828] px-4 py-3 font-bold disabled:opacity-50">{busy ? 'Signing in…' : 'Sign in securely'}</button>
          </form>
          <p className="mt-5 text-xs leading-5 text-white/45">API: {API_BASE}. Configure NEXT_PUBLIC_A1OS_API_BASE_URL for the deployed platform API.</p>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-[#f5f4f1] text-[#151515]">
      <header className="flex flex-wrap items-center justify-between gap-4 border-b border-black/10 bg-white px-5 py-4 md:px-10">
        <div><p className="text-xs font-bold uppercase tracking-[0.3em] text-[#d62828]">A1OS Charity</p><h1 className="text-xl font-black">Stramos Wisdom Operations</h1></div>
        <div className="flex items-center gap-3"><div className="text-right text-sm"><p className="font-bold">{user.full_name}</p><p className="text-black/55">{user.role}</p></div><button onClick={signOut} className="rounded-xl border border-black/15 px-4 py-2 text-sm font-bold">Sign out</button></div>
      </header>
      <div className="mx-auto grid max-w-7xl gap-6 p-5 md:p-8 lg:grid-cols-[230px_1fr]">
        <aside className="space-y-2">
          <p className="mb-3 text-xs font-bold uppercase tracking-[0.2em] text-black/50">Modules</p>
          {allowed.map((resource) => <button key={resource.key} onClick={() => { setSelected(resource.key); setValues({}); setError(''); setNotice(''); }} className={`block w-full rounded-xl px-4 py-3 text-left text-sm font-bold ${selected === resource.key ? 'bg-[#151515] text-white' : 'bg-white hover:bg-black/5'}`}>{resource.label}</button>)}
        </aside>
        <section className="min-w-0 space-y-5">
          <div className="flex flex-wrap items-end justify-between gap-3"><div><p className="text-xs font-bold uppercase tracking-[0.25em] text-[#d62828]">Tenant-scoped records</p><h2 className="mt-1 text-3xl font-black">{current.label}</h2></div><span className="rounded-full bg-white px-3 py-2 text-xs font-bold">{items.length} shown</span></div>
          {error && <p role="alert" className="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-800">{error}</p>}
          {notice && <p role="status" className="rounded-xl border border-green-200 bg-green-50 p-3 text-sm text-green-800">{notice}</p>}
          {canWrite && <form onSubmit={createRecord} className="rounded-2xl border border-black/10 bg-white p-5">
            <h3 className="mb-4 text-lg font-black">Create record</h3>
            <div className="grid gap-4 sm:grid-cols-2">
              {current.fields.map((field) => <label key={field.key} className="block text-sm font-semibold">{field.label}{field.required ? ' *' : ''}
                <input className="mt-2 w-full rounded-xl border border-black/15 bg-white px-3 py-2.5 font-normal" type={field.type || 'text'} placeholder={field.placeholder} required={field.required} value={values[field.key] || ''} onChange={(e) => setValues((old) => ({ ...old, [field.key]: e.target.value }))} />
              </label>)}
            </div>
            <button disabled={busy} className="mt-5 rounded-xl bg-[#d62828] px-5 py-3 font-bold text-white disabled:opacity-50">{busy ? 'Saving…' : 'Create record'}</button>
          </form>}
          <div className="space-y-3">
            <h3 className="text-lg font-black">Records</h3>
            {items.length === 0 && <div className="rounded-2xl border border-dashed border-black/20 bg-white p-8 text-sm text-black/55">No records returned for this organization, or your account lacks access.</div>}
            {items.map((item, index) => <article key={String(item.id ?? index)} className="rounded-2xl border border-black/10 bg-white p-4"><div className="mb-3 flex items-center justify-between"><span className="text-xs font-bold uppercase tracking-[0.15em] text-black/45">Record #{String(item.id ?? index + 1)}</span><span className="rounded-full bg-black/5 px-3 py-1 text-xs font-bold">{String(item.status || 'record')}</span></div><pre className="overflow-x-auto whitespace-pre-wrap break-words text-xs leading-5">{JSON.stringify(item, null, 2)}</pre></article>)}
          </div>
        </section>
      </div>
    </main>
  );
}
