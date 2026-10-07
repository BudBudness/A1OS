-- Barya, Byamugisha & Co. Advocates internal practice platform
create extension if not exists pgcrypto;
create table if not exists public.legal_profiles (
  user_id uuid primary key references auth.users(id) on delete cascade,
  full_name text not null,
  role text not null check (role in ('partner','advocate','clerk','finance','administrator','client')),
  active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create table if not exists public.legal_clients (
  id uuid primary key default gen_random_uuid(), client_number text not null unique,
  client_type text not null, legal_name text not null, phone text, email text, address text, notes text,
  status text not null default 'active', created_by uuid references auth.users(id),
  created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create table if not exists public.legal_matters (
  id uuid primary key default gen_random_uuid(), matter_number text not null unique, title text not null,
  client_id uuid not null references public.legal_clients(id), practice_area text not null, matter_type text,
  status text not null default 'intake', confidentiality text not null default 'restricted',
  description text, opened_at date, closed_at date, created_by uuid references auth.users(id),
  created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create table if not exists public.legal_matter_members (
  matter_id uuid not null references public.legal_matters(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  assignment_role text not null, created_at timestamptz not null default now(),
  primary key (matter_id,user_id)
);
create table if not exists public.legal_parties (
  id uuid primary key default gen_random_uuid(), matter_id uuid not null references public.legal_matters(id) on delete cascade,
  name text not null, party_type text not null, contact text, notes text, created_at timestamptz not null default now()
);
create table if not exists public.legal_tasks (
  id uuid primary key default gen_random_uuid(), matter_id uuid references public.legal_matters(id) on delete cascade,
  title text not null, description text, assigned_to uuid references auth.users(id),
  status text not null default 'open', priority text not null default 'normal', due_at timestamptz,
  completed_at timestamptz, created_by uuid references auth.users(id),
  created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create table if not exists public.legal_deadlines (
  id uuid primary key default gen_random_uuid(), matter_id uuid not null references public.legal_matters(id) on delete cascade,
  title text not null, deadline_at timestamptz not null, source text,
  status text not null default 'open', owner_id uuid references auth.users(id), notes text,
  created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create table if not exists public.legal_documents (
  id uuid primary key default gen_random_uuid(), matter_id uuid not null references public.legal_matters(id) on delete cascade,
  title text not null, document_type text not null, storage_path text, mime_type text,
  version integer not null default 1, checksum text, uploaded_by uuid references auth.users(id),
  created_at timestamptz not null default now()
);
create table if not exists public.legal_evidence (
  id uuid primary key default gen_random_uuid(), matter_id uuid not null references public.legal_matters(id) on delete cascade,
  reference text not null, description text not null, source text, storage_path text,
  exhibit_number text, collected_at timestamptz, recorded_by uuid references auth.users(id),
  created_at timestamptz not null default now()
);
create table if not exists public.legal_invoices (
  id uuid primary key default gen_random_uuid(), matter_id uuid not null references public.legal_matters(id) on delete cascade,
  invoice_number text not null unique, amount numeric(14,2) not null check (amount >= 0),
  currency text not null default 'UGX', status text not null default 'draft',
  due_date date, issued_at timestamptz, created_by uuid references auth.users(id),
  created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create table if not exists public.legal_payments (
  id uuid primary key default gen_random_uuid(), invoice_id uuid not null references public.legal_invoices(id) on delete cascade,
  amount numeric(14,2) not null check (amount > 0), currency text not null default 'UGX',
  method text, reference text, paid_at timestamptz not null default now(),
  recorded_by uuid references auth.users(id), created_at timestamptz not null default now()
);
create table if not exists public.legal_audit_events (
  id uuid primary key default gen_random_uuid(), actor_id uuid references auth.users(id),
  matter_id uuid references public.legal_matters(id) on delete set null, action text not null,
  entity_type text not null, entity_id text, metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists legal_clients_created_by_idx on public.legal_clients(created_by);
create index if not exists legal_matters_client_idx on public.legal_matters(client_id);
create index if not exists legal_matters_created_by_idx on public.legal_matters(created_by);
create index if not exists legal_members_user_idx on public.legal_matter_members(user_id);
create index if not exists legal_parties_matter_idx on public.legal_parties(matter_id);
create index if not exists legal_tasks_matter_idx on public.legal_tasks(matter_id);
create index if not exists legal_tasks_assigned_to_idx on public.legal_tasks(assigned_to);
create index if not exists legal_tasks_created_by_idx on public.legal_tasks(created_by);
create index if not exists legal_deadlines_matter_idx on public.legal_deadlines(matter_id);
create index if not exists legal_deadlines_owner_idx on public.legal_deadlines(owner_id);
create index if not exists legal_documents_matter_idx on public.legal_documents(matter_id);
create index if not exists legal_documents_uploaded_by_idx on public.legal_documents(uploaded_by);
create index if not exists legal_evidence_matter_idx on public.legal_evidence(matter_id);
create index if not exists legal_evidence_recorded_by_idx on public.legal_evidence(recorded_by);
create index if not exists legal_invoices_matter_idx on public.legal_invoices(matter_id);
create index if not exists legal_invoices_created_by_idx on public.legal_invoices(created_by);
create index if not exists legal_payments_invoice_idx on public.legal_payments(invoice_id);
create index if not exists legal_payments_recorded_by_idx on public.legal_payments(recorded_by);
create index if not exists legal_audit_matter_idx on public.legal_audit_events(matter_id);
create index if not exists legal_audit_actor_idx on public.legal_audit_events(actor_id);

create or replace function public.legal_is_staff() returns boolean language sql stable security definer set search_path=public
as $$ select exists(select 1 from public.legal_profiles p where p.user_id=(select auth.uid()) and p.active and p.role <> 'client') $$;
create or replace function public.legal_is_manager() returns boolean language sql stable security definer set search_path=public
as $$ select exists(select 1 from public.legal_profiles p where p.user_id=(select auth.uid()) and p.active and p.role in ('partner','administrator')) $$;
create or replace function public.legal_has_matter_access(p_matter uuid) returns boolean language sql stable security definer set search_path=public
as $$ select public.legal_is_manager() or exists(select 1 from public.legal_matter_members mm join public.legal_profiles p on p.user_id=mm.user_id where mm.matter_id=p_matter and mm.user_id=(select auth.uid()) and p.active) $$;

alter table public.legal_profiles enable row level security;
alter table public.legal_clients enable row level security;
alter table public.legal_matters enable row level security;
alter table public.legal_matter_members enable row level security;
alter table public.legal_parties enable row level security;
alter table public.legal_tasks enable row level security;
alter table public.legal_deadlines enable row level security;
alter table public.legal_documents enable row level security;
alter table public.legal_evidence enable row level security;
alter table public.legal_invoices enable row level security;
alter table public.legal_payments enable row level security;
alter table public.legal_audit_events enable row level security;

drop policy if exists profiles_self on public.legal_profiles;
create policy profiles_self on public.legal_profiles for select to authenticated using ((select auth.uid())=user_id or public.legal_is_manager());
drop policy if exists clients_staff on public.legal_clients;
create policy clients_staff on public.legal_clients for all to authenticated using (public.legal_is_staff()) with check (public.legal_is_staff());
drop policy if exists matters_access on public.legal_matters;
create policy matters_access on public.legal_matters for select to authenticated using (public.legal_has_matter_access(id));
drop policy if exists matters_manager_write on public.legal_matters;
drop policy if exists matters_manager_insert on public.legal_matters;
drop policy if exists matters_manager_update on public.legal_matters;
drop policy if exists matters_manager_delete on public.legal_matters;
create policy matters_manager_insert on public.legal_matters for insert to authenticated with check (public.legal_is_manager());
create policy matters_manager_update on public.legal_matters for update to authenticated using (public.legal_is_manager()) with check (public.legal_is_manager());
create policy matters_manager_delete on public.legal_matters for delete to authenticated using (public.legal_is_manager());
drop policy if exists members_access on public.legal_matter_members;
create policy members_access on public.legal_matter_members for select to authenticated using (public.legal_has_matter_access(matter_id));
drop policy if exists members_manager_write on public.legal_matter_members;
create policy members_manager_insert on public.legal_matter_members for insert to authenticated with check (public.legal_is_manager());
create policy members_manager_update on public.legal_matter_members for update to authenticated using (public.legal_is_manager()) with check (public.legal_is_manager());
create policy members_manager_delete on public.legal_matter_members for delete to authenticated using (public.legal_is_manager());
drop policy if exists parties_access on public.legal_parties;
create policy parties_access on public.legal_parties for all to authenticated using (public.legal_has_matter_access(matter_id)) with check (public.legal_has_matter_access(matter_id));
drop policy if exists tasks_access on public.legal_tasks;
create policy tasks_access on public.legal_tasks for all to authenticated using (matter_id is null or public.legal_has_matter_access(matter_id)) with check (matter_id is null or public.legal_has_matter_access(matter_id));
drop policy if exists deadlines_access on public.legal_deadlines;
create policy deadlines_access on public.legal_deadlines for all to authenticated using (public.legal_has_matter_access(matter_id)) with check (public.legal_has_matter_access(matter_id));
drop policy if exists documents_access on public.legal_documents;
create policy documents_access on public.legal_documents for all to authenticated using (public.legal_has_matter_access(matter_id)) with check (public.legal_has_matter_access(matter_id));
drop policy if exists evidence_access on public.legal_evidence;
create policy evidence_access on public.legal_evidence for all to authenticated using (public.legal_has_matter_access(matter_id)) with check (public.legal_has_matter_access(matter_id));
drop policy if exists invoices_access on public.legal_invoices;
create policy invoices_access on public.legal_invoices for all to authenticated using (public.legal_has_matter_access(matter_id)) with check (public.legal_has_matter_access(matter_id));
drop policy if exists payments_access on public.legal_payments;
create policy payments_access on public.legal_payments for all to authenticated using (public.legal_has_matter_access((select i.matter_id from public.legal_invoices i where i.id=invoice_id))) with check (public.legal_has_matter_access((select i.matter_id from public.legal_invoices i where i.id=invoice_id)));
drop policy if exists audit_access on public.legal_audit_events;
create policy audit_access on public.legal_audit_events for select to authenticated using (matter_id is null or public.legal_has_matter_access(matter_id));


grant select, insert, update, delete on public.legal_profiles, public.legal_clients, public.legal_matters, public.legal_matter_members, public.legal_parties, public.legal_tasks, public.legal_deadlines, public.legal_documents, public.legal_evidence, public.legal_invoices, public.legal_payments, public.legal_audit_events to authenticated;

revoke execute on function public.legal_is_staff() from public, anon, authenticated;
revoke execute on function public.legal_is_manager() from public, anon, authenticated;
revoke execute on function public.legal_has_matter_access(uuid) from public, anon, authenticated;
