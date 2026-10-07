create index if not exists legal_parties_matter_idx on legal.parties(matter_id);
create index if not exists legal_payments_invoice_idx on legal.payments(invoice_id);
create index if not exists legal_research_matter_idx on legal.research(matter_id);
create index if not exists legal_research_created_by_idx on legal.research(created_by);
create index if not exists legal_tasks_created_by_idx on legal.tasks(created_by);
drop policy if exists matters_manager_write on legal.matters;
create policy matters_manager_insert on legal.matters for insert to authenticated with check (legal.is_manager());
create policy matters_manager_update on legal.matters for update to authenticated using (legal.is_manager()) with check (legal.is_manager());
create policy matters_manager_delete on legal.matters for delete to authenticated using (legal.is_manager());