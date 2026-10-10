-- Atomic task claiming for the A1OS cloud execution bridge.
-- Only the server-side service role may call this function.
create or replace function public.a1os_claim_task(p_task_id text)
returns setof public.a1os_tasks
language sql
security invoker
set search_path = public
as $$
  update public.a1os_tasks
     set status = 'running',
         attempts = attempts + 1,
         updated_at = now()
   where task_id = p_task_id
     and (
       status = 'queued'
       or (
         status = 'retry'
         and (next_attempt_at is null or next_attempt_at <= now())
       )
     )
  returning *;
$$;

revoke all on function public.a1os_claim_task(text) from public, anon, authenticated;
grant execute on function public.a1os_claim_task(text) to service_role;
