-- Remove legacy public legal objects, normalize matter write policy,
-- and cover remaining foreign keys for the canonical legal schema.
drop table if exists public.legal_payments,public.legal_invoices,public.legal_evidence,public.legal_documents,public.legal_deadlines,public.legal_tasks,public.legal_parties,public.legal_matter_members,public.legal_matters,public.legal_clients,public.legal_profiles,public.legal_audit_events,public.legal_research cascade;
drop function if exists public.legal_has_matter_access(uuid) cascade;
drop function if exists public.legal_is_manager() cascade;
drop function if exists public.legal_is_staff() cascade;
drop policy if exists matters_manager_insert on legal.matters;
drop policy if exists matters_manager_update on legal.matters;
drop policy if exists matters_manager_delete on legal.matters;
drop policy if exists matters_manager_write on legal.matters;
create policy matters_manager_write on legal.matters for all to authenticated using (legal.is_manager()) with check (legal.is_manager());
create index if not exists legal_clients_created_by_idx on legal.clients(created_by);
create index if not exists legal_deadlines_owner_idx on legal.deadlines(owner_id);
create index if not exists legal_documents_uploaded_by_idx on legal.documents(uploaded_by);
create index if not exists legal_evidence_recorded_by_idx on legal.evidence(recorded_by);
create index if not exists legal_invoices_created_by_idx on legal.invoices(created_by);
create index if not exists legal_payments_recorded_by_idx on legal.payments(recorded_by);
create index if not exists legal_audit_actor_idx on legal.audit_events(actor_id);
create index if not exists legal_tasks_assigned_to_idx on legal.tasks(assigned_to);
create index if not exists legal_tasks_created_by_idx on legal.tasks(created_by);
create index if not exists legal_research_created_by_idx on legal.research(created_by);
drop policy if exists profiles_self on legal.profiles;
create policy profiles_self on legal.profiles for select to authenticated using ((select auth.uid())=user_id or legal.is_manager());
