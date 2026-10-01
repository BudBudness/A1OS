create table if not exists public.a1os_tasks (
  task_id text primary key,
  target text not null,
  role text not null,
  action text not null,
  payload jsonb not null default '{}'::jsonb,
  status text not null default 'queued',
  attempts integer not null default 0,
  max_attempts integer not null default 3,
  error text,
  next_attempt_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  completed_at timestamptz
);

create index if not exists a1os_tasks_status_idx
  on public.a1os_tasks(status, created_at);

alter table public.a1os_tasks enable row level security;

revoke all on table public.a1os_tasks from anon, authenticated;
