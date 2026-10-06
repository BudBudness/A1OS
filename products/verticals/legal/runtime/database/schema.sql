-- Barya, Byamugisha & Co. Advocates production schema
create extension if not exists pgcrypto;

create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  full_name text not null,
  role text not null check (role in ('partner','advocate','clerk','finance','administrator','client')),
  created_at timestamptz not null default now()
);
alter table public.profiles enable row level security;

create table if not exists public.clients (
  id uuid primary key default gen_random_uuid(), name text not null,
  client_type text not null default 'individual' check (client_type in ('individual','company','government','ngo','other')),
  phone text, email text, address text, notes text, created_by uuid references auth.users(id),
  created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
alter table public.clients enable row level security;

create table if not exists public.matters (
  id uuid primary key default gen_random_uuid(), matter_number text not null unique, title text not null,
  client_id uuid not null references public.clients(id),
  practice_area text not null check (practice_area in ('litigation','commercial','labour','conveyancing','advisory','family','other')),
  status text not null default 'intake' check (status in ('intake','conflict_check','active','pending','closed','archived')),
  description text, opened_at timestamptz, closed_at timestamptz, created_by uuid references auth.users(id),
  created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
alter table public.matters enable row level security;

create table if not exists public.matter_members (
  matter_id uuid not null references public.matters(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  access_level text not null default 'member' check (access_level in ('owner','member','viewer')),
  created_at timestamptz not null default now(), primary key (matter_id,user_id)
);
alter table public.matter_members enable row level security;

create table if not exists public.tasks (
  id uuid primary key default gen_random_uuid(), matter_id uuid not null references public.matters(id) on delete cascade,
  title text not null, description text, assigned_to uuid references auth.users(id),
  status text not null default 'open' check (status in ('open','in_progress','blocked','done')),
  due_at timestamptz, created_by uuid references auth.users(id), created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
alter table public.tasks enable row level security;

create table if not exists public.deadlines (
  id uuid primary key default gen_random_uuid(), matter_id uuid not null references public.matters(id) on delete cascade,
  title text not null, due_at timestamptz not null, status text not null default 'open' check (status in ('open','completed','missed')),
  created_by uuid references auth.users(id), created_at timestamptz not null default now()
);
alter table public.deadlines enable row level security;

create table if not exists public.documents (
  id uuid primary key default gen_random_uuid(), matter_id uuid not null references public.matters(id) on delete cascade,
  title text not null, document_type text not null default 'other', storage_path text, version integer not null default 1,
  uploaded_by uuid references auth.users(id), created_at timestamptz not null default now()
);
alter table public.documents enable row level security;

create table if not exists public.evidence (
  id uuid primary key default gen_random_uuid(), matter_id uuid not null references public.matters(id) on delete cascade,
  title text not null, description text, storage_path text, evidence_type text not null default 'document',
  captured_at timestamptz, created_by uuid references auth.users(id), created_at timestamptz not null default now()
);
alter table public.evidence enable row level security;

create table if not exists public.billing_items (
  id uuid primary key default gen_random_uuid(), matter_id uuid not null references public.matters(id) on delete cascade,
  description text not null, amount numeric(18,2) not null check (amount >= 0), currency text not null default 'UGX',
  status text not null default 'unbilled' check (status in ('unbilled','invoiced','paid','waived')),
  created_by uuid references auth.users(id), created_at timestamptz not null default now()
);
alter table public.billing_items enable row level security;

create table if not exists public.research_records (
  id uuid primary key default gen_random_uuid(), matter_id uuid references public.matters(id) on delete cascade,
  source text not null, citation text, query text, summary text, url text,
  created_by uuid references auth.users(id), created_at timestamptz not null default now()
);
alter table public.research_records enable row level security;

create table if not exists public.audit_events (
  id uuid primary key default gen_random_uuid(), actor_id uuid references auth.users(id),
  matter_id uuid references public.matters(id) on delete set null, action text not null,
  entity_type text not null, entity_id uuid, metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);
alter table public.audit_events enable row level security;

create index if not exists matters_client_idx on public.matters(client_id);
create index if not exists matter_members_user_idx on public.matter_members(user_id);
create index if not exists tasks_matter_due_idx on public.tasks(matter_id,due_at);
create index if not exists deadlines_due_idx on public.deadlines(due_at,status);
create index if not exists documents_matter_idx on public.documents(matter_id);
create index if not exists evidence_matter_idx on public.evidence(matter_id);
create index if not exists billing_matter_idx on public.billing_items(matter_id);
create index if not exists research_matter_idx on public.research_records(matter_id);
create index if not exists audit_matter_idx on public.audit_events(matter_id,created_at);

create or replace function public.has_matter_access(target_matter uuid)
returns boolean language sql stable security invoker as $$
  select exists (select 1 from public.matter_members mm where mm.matter_id = target_matter and mm.user_id = (select auth.uid()))
  or coalesce((select auth.jwt()->'app_metadata'->>'role'), '') in ('partner','administrator');
$$;

create policy profiles_self on public.profiles for select to authenticated
using (id = (select auth.uid()) or coalesce((select auth.jwt()->'app_metadata'->>'role'),'') in ('partner','administrator'));

create policy clients_staff_select on public.clients for select to authenticated
using (coalesce((select auth.jwt()->'app_metadata'->>'role'),'') in ('partner','advocate','clerk','finance','administrator'));
create policy clients_staff_insert on public.clients for insert to authenticated
with check (coalesce((select auth.jwt()->'app_metadata'->>'role'),'') in ('partner','advocate','clerk','administrator'));
create policy clients_staff_update on public.clients for update to authenticated
using (coalesce((select auth.jwt()->'app_metadata'->>'role'),'') in ('partner','advocate','clerk','administrator'))
with check (coalesce((select auth.jwt()->'app_metadata'->>'role'),'') in ('partner','advocate','clerk','administrator'));

create policy matters_select on public.matters for select to authenticated using (public.has_matter_access(id));
create policy matters_insert on public.matters for insert to authenticated
with check (coalesce((select auth.jwt()->'app_metadata'->>'role'),'') in ('partner','advocate','administrator'));
create policy matters_update on public.matters for update to authenticated
using (public.has_matter_access(id)) with check (public.has_matter_access(id));

create policy matter_members_select on public.matter_members for select to authenticated
using (user_id=(select auth.uid()) or public.has_matter_access(matter_id));
create policy matter_members_manage on public.matter_members for all to authenticated
using (coalesce((select auth.jwt()->'app_metadata'->>'role'),'') in ('partner','administrator'))
with check (coalesce((select auth.jwt()->'app_metadata'->>'role'),'') in ('partner','administrator'));

create policy tasks_select on public.tasks for select to authenticated using (public.has_matter_access(matter_id));
create policy tasks_insert on public.tasks for insert to authenticated with check (public.has_matter_access(matter_id));
create policy tasks_update on public.tasks for update to authenticated using (public.has_matter_access(matter_id)) with check (public.has_matter_access(matter_id));

create policy deadlines_select on public.deadlines for select to authenticated using (public.has_matter_access(matter_id));
create policy deadlines_insert on public.deadlines for insert to authenticated with check (public.has_matter_access(matter_id));
create policy deadlines_update on public.deadlines for update to authenticated using (public.has_matter_access(matter_id)) with check (public.has_matter_access(matter_id));

create policy documents_select on public.documents for select to authenticated using (public.has_matter_access(matter_id));
create policy documents_insert on public.documents for insert to authenticated with check (public.has_matter_access(matter_id));
create policy documents_update on public.documents for update to authenticated using (public.has_matter_access(matter_id)) with check (public.has_matter_access(matter_id));

create policy evidence_select on public.evidence for select to authenticated using (public.has_matter_access(matter_id));
create policy evidence_insert on public.evidence for insert to authenticated with check (public.has_matter_access(matter_id));

create policy billing_select on public.billing_items for select to authenticated using (public.has_matter_access(matter_id));
create policy billing_insert on public.billing_items for insert to authenticated with check (public.has_matter_access(matter_id));

create policy research_select on public.research_records for select to authenticated using (matter_id is null or public.has_matter_access(matter_id));
create policy research_insert on public.research_records for insert to authenticated with check (matter_id is null or public.has_matter_access(matter_id));

create policy audit_select on public.audit_events for select to authenticated
using (coalesce((select auth.jwt()->'app_metadata'->>'role'),'') in ('partner','administrator') or actor_id=(select auth.uid()));
create policy audit_insert on public.audit_events for insert to authenticated with check (actor_id=(select auth.uid()));

revoke all on all tables in schema public from anon;
