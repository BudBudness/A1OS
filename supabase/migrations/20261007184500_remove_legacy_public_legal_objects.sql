drop table if exists public.legal_payments,public.legal_invoices,public.legal_evidence,public.legal_documents,public.legal_deadlines,public.legal_tasks,public.legal_parties,public.legal_matter_members,public.legal_matters,public.legal_clients,public.legal_profiles,public.legal_audit_events,public.legal_research cascade;
drop function if exists public.legal_has_matter_access(uuid) cascade;
drop function if exists public.legal_is_manager() cascade;
drop function if exists public.legal_is_staff() cascade;