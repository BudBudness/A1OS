-- Canonical production schema for the Barya, Byamugisha & Co. Advocates vertical.
-- Production currently uses the public schema with legal_* table names.

create table if not exists public.legal_profiles (
  user_id uuid primary key references auth.users(id) on delete cascade,
  full_name text not null,
  role text not null check (role in ('partner','advocate','clerk','finance','administrator','client')),
  active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.legal_clients (
  id uuid primary key default gen_random_uuid(),
  client_number text unique not null,
  client_type text not null,
  legal_name text not null,
  phone text,
  email text,
  address text,
  notes text,
  status text not null default 'active',
  created_by uuid references auth.users(id),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.legal_matters (
  id uuid primary key default gen_random_uuid(),
  matter_number text unique not null,
  title text not null,
  client_id uuid not null references public.legal_clients(id),
  practice_area text not null,
  matter_type text,
  status text not null default 'intake',
  confidentiality text not null default 'restricted',
  description text,
  opened_at date,
  closed_at date,
  created_by uuid references auth.users(id),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.legal_matter_members (
  matter_id uuid not null references public.legal_matters(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  assignment_role text not null,
  created_at timestamptz not null default now(),
  primary key (matter_id, user_id)
);

create table if not exists public.legal_parties (
  id uuid primary key default gen_random_uuid(),
  matter_id uuid not null references public.legal_matters(id) on delete cascade,
  name text not null,
  party_type text not null,
  contact text,
  notes text,
  created_at timestamptz not null default now()
);

create table if not exists public.legal_tasks (
  id uuid primary key default gen_random_uuid(),
  matter_id uuid references public.legal_matters(id) on delete cascade,
  title text not null,
  description text,
  assigned_to uuid references auth.users(id),
  status text not null default 'open',
  priority text not null default 'normal',
  due_at timestamptz,
  completed_at timestamptz,
  created_by uuid references auth.users(id),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.legal_deadlines (
  id uuid primary key default gen_random_uuid(),
  matter_id uuid not null references public.legal_matters(id) on delete cascade,
  title text not null,
  deadline_at timestamptz not null,
  source text,
  status text not null default 'open',
  owner_id uuid references auth.users(id),
  notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.legal_documents (
  id uuid primary key default gen_random_uuid(),
  matter_id uuid not null references public.legal_matters(id) on delete cascade,
  title text not null,
  document_type text not null,
  storage_path text,
  mime_type text,
  version integer not null default 1,
  checksum text,
  uploaded_by uuid references auth.users(id),
  created_at timestamptz not null default now()
);

create table if not exists public.legal_evidence (
  id uuid primary key default gen_random_uuid(),
  matter_id uuid not null references public.legal_matters(id) on delete cascade,
  reference text not null,
  description text not null,
  source text,
  storage_path text,
  exhibit_number text,
  collected_at timestamptz,
  recorded_by uuid references auth.users(id),
  created_at timestamptz not null default now()
);

create table if not exists public.legal_invoices (
  id uuid primary key default gen_random_uuid(),
  matter_id uuid not null references public.legal_matters(id) on delete cascade,
  invoice_number text unique not null,
  amount numeric(14,2) not null check (amount >= 0),
  currency text not null default 'UGX',
  status text not null default 'draft',
  due_date date,
  issued_at timestamptz,
  created_by uuid references auth.users(id),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.legal_payments (
  id uuid primary key default gen_random_uuid(),
  invoice_id uuid not null references public.legal_invoices(id) on delete cascade,
  amount numeric(14,2) not null check (amount > 0),
  currency text not null default 'UGX',
  method text,
  reference text,
  paid_at timestamptz not null default now(),
  recorded_by uuid references auth.users(id),
  created_at timestamptz not null default now()
);

create table if not exists public.legal_audit_events (
  id uuid primary key default gen_random_uuid(),
  actor_id uuid references auth.users(id),
  matter_id uuid references public.legal_matters(id) on delete set null,
  action text not null,
  entity_type text not null,
  entity_id text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists public.legal_research (
  id uuid primary key default gen_random_uuid(),
  matter_id uuid references public.legal_matters(id) on delete cascade,
  title text not null,
  source text not null,
  citation text,
  url text,
  notes text,
  created_by uuid references auth.users(id),
  created_at timestamptz not null default now()
);
