interface D1Result<T = Record<string, unknown>> {
  results?: T[];
  success: boolean;
  meta?: { changes?: number };
}
interface D1PreparedStatement {
  bind(...values: unknown[]): D1PreparedStatement;
  all<T = Record<string, unknown>>(): Promise<D1Result<T>>;
  first<T = Record<string, unknown>>(): Promise<T | null>;
  run(): Promise<D1Result>;
}
interface D1Database {
  prepare(query: string): D1PreparedStatement;
}
interface Env {
  DB: D1Database;
  TASK_QUEUE_TOKEN: string;
}

type TaskRow = {
  task_id: string;
  target: string;
  role: string;
  action: string;
  payload_json: string;
  status: string;
  attempts: number;
  max_attempts: number;
  error: string | null;
  next_attempt_at: string | null;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
};

const json = (data: unknown, status = 200): Response =>
  new Response(JSON.stringify(data), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
      "x-content-type-options": "nosniff",
    },
  });

async function sameSecret(left: string, right: string): Promise<boolean> {
  if (!left || !right) return false;
  const encoder = new TextEncoder();
  const [a, b] = await Promise.all([
    crypto.subtle.digest("SHA-256", encoder.encode(left)),
    crypto.subtle.digest("SHA-256", encoder.encode(right)),
  ]);
  const aa = new Uint8Array(a);
  const bb = new Uint8Array(b);
  let mismatch = 0;
  for (let i = 0; i < aa.length; i += 1) mismatch |= aa[i] ^ bb[i];
  return mismatch === 0;
}

function publicTask(row: TaskRow | null): Record<string, unknown> | null {
  if (!row) return null;
  let payload: unknown;
  try { payload = JSON.parse(row.payload_json); } catch { payload = null; }
  return {
    task_id: row.task_id,
    target: row.target,
    role: row.role,
    action: row.action,
    payload,
    status: row.status,
    attempts: row.attempts,
    max_attempts: row.max_attempts,
    error: row.error,
    next_attempt_at: row.next_attempt_at,
    created_at: row.created_at,
    updated_at: row.updated_at,
    completed_at: row.completed_at,
  };
}

async function bodyJson(request: Request): Promise<Record<string, unknown> | null> {
  const declared = Number(request.headers.get("content-length") ?? "0");
  if (declared > 262144) return null;
  const raw = await request.text();
  if (raw.length > 262144) return null;
  try {
    const parsed: unknown = JSON.parse(raw);
    return parsed && typeof parsed === "object" && !Array.isArray(parsed)
      ? parsed as Record<string, unknown>
      : null;
  } catch {
    return null;
  }
}

async function enqueue(request: Request, env: Env): Promise<Response> {
  const body = await bodyJson(request);
  if (!body) return json({ error: "Invalid JSON object or request too large" }, 400);
  const target = typeof body.target === "string" ? body.target.trim() : "";
  const role = typeof body.role === "string" ? body.role.trim() : "";
  const action = typeof body.action === "string" ? body.action.trim() : "";
  const taskId = typeof body.task_id === "string" && body.task_id.trim()
    ? body.task_id.trim()
    : crypto.randomUUID();
  const payload = body.payload ?? {};
  const maxAttempts = Number.isInteger(body.max_attempts) ? Number(body.max_attempts) : 3;
  if (!target || target.length > 120 || !role || role.length > 80 ||
      !action || action.length > 120 || taskId.length > 120 ||
      maxAttempts < 1 || maxAttempts > 20 ||
      payload === null || typeof payload !== "object") {
    return json({ error: "Invalid task fields" }, 400);
  }

  const payloadJson = JSON.stringify(payload);
  const inserted = await env.DB.prepare(
    "INSERT OR IGNORE INTO tasks(task_id,target,role,action,payload_json,max_attempts) VALUES(?,?,?,?,?,?)",
  ).bind(taskId, target, role, action, payloadJson, maxAttempts).run?.();
  // D1's prepared statement contract is kept minimal; determine idempotency by reading the key.
  const row = await env.DB.prepare("SELECT * FROM tasks WHERE task_id = ? LIMIT 1")
    .bind(taskId).first<TaskRow>();
  if (!row) return json({ error: "Task could not be persisted" }, 500);
  const sameRequest = row.target === target && row.role === role &&
    row.action === action && row.payload_json === payloadJson &&
    row.max_attempts === maxAttempts;
  if (!sameRequest) return json({ error: "task_id already exists with different content" }, 409);
  const created = (inserted?.meta?.changes ?? 0) > 0;
  return json({ task_id: taskId, created, task: publicTask(row) }, created ? 201 : 200);
}

async function getTask(taskId: string, env: Env): Promise<Response> {
  const row = await env.DB.prepare("SELECT * FROM tasks WHERE task_id = ? LIMIT 1")
    .bind(taskId).first<TaskRow>();
  return row ? json({ data: publicTask(row) }) : json({ error: "Task not found" }, 404);
}

async function pending(url: URL, env: Env): Promise<Response> {
  const rawLimit = url.searchParams.get("limit") ?? "20";
  const limit = /^\d+$/.test(rawLimit) ? Math.min(100, Math.max(1, Number(rawLimit))) : 20;
  const rows = await env.DB.prepare(
    "SELECT * FROM tasks WHERE status IN ('queued','retry') AND (next_attempt_at IS NULL OR datetime(next_attempt_at) <= CURRENT_TIMESTAMP) ORDER BY created_at ASC LIMIT ?",
  ).bind(limit).all<TaskRow>();
  return json({ data: (rows.results ?? []).map((row) => publicTask(row)) });
}

async function claim(taskId: string, env: Env): Promise<Response> {
  const row = await env.DB.prepare(
    "UPDATE tasks SET status='running', attempts=attempts+1, updated_at=CURRENT_TIMESTAMP WHERE task_id=? AND (status='queued' OR (status='retry' AND (next_attempt_at IS NULL OR datetime(next_attempt_at) <= CURRENT_TIMESTAMP))) RETURNING *",
  ).bind(taskId).first<TaskRow>();
  return row ? json({ claimed: true, task: publicTask(row) }) : json({ claimed: false }, 409);
}

async function complete(taskId: string, env: Env): Promise<Response> {
  const row = await env.DB.prepare(
    "UPDATE tasks SET status='completed', error=NULL, next_attempt_at=NULL, completed_at=CURRENT_TIMESTAMP, updated_at=CURRENT_TIMESTAMP WHERE task_id=? AND status='running' RETURNING *",
  ).bind(taskId).first<TaskRow>();
  return row ? json({ task: publicTask(row) }) : json({ error: "Task is not running or does not exist" }, 409);
}

async function fail(taskId: string, request: Request, env: Env): Promise<Response> {
  const body = await bodyJson(request);
  if (!body || typeof body.error !== "string" || !body.error.trim()) {
    return json({ error: "A non-empty error string is required" }, 400);
  }
  const current = await env.DB.prepare("SELECT attempts,max_attempts,status FROM tasks WHERE task_id=? LIMIT 1")
    .bind(taskId).first<{ attempts: number; max_attempts: number; status: string }>();
  if (!current || current.status !== "running") return json({ error: "Task is not running or does not exist" }, 409);
  const message = body.error.replace(/[\r\n]+/g, " ").slice(0, 1000);
  const terminal = message.startsWith("ApprovalDenied:") || current.attempts >= current.max_attempts;
  const delaySeconds = Math.min(300, 2 ** current.attempts);
  const nextAttempt = terminal ? null : new Date(Date.now() + delaySeconds * 1000).toISOString();
  const row = await env.DB.prepare(
    "UPDATE tasks SET status=?, error=?, next_attempt_at=?, updated_at=CURRENT_TIMESTAMP WHERE task_id=? AND status='running' AND attempts=? RETURNING *",
  ).bind(terminal ? "failed" : "retry", message, nextAttempt, taskId, current.attempts).first<TaskRow>();
  return row ? json({ task: publicTask(row) }) : json({ error: "Task state changed; retry the read" }, 409);
}

async function recover(request: Request, env: Env): Promise<Response> {
  const body = await bodyJson(request);
  const staleSeconds = body && Number.isInteger(body.stale_after_seconds)
    ? Math.min(86400, Math.max(30, Number(body.stale_after_seconds)))
    : 300;
  const limit = body && Number.isInteger(body.limit)
    ? Math.min(100, Math.max(1, Number(body.limit)))
    : 100;
  const rows = await env.DB.prepare(
    "UPDATE tasks SET status=CASE WHEN attempts >= max_attempts THEN 'failed' ELSE 'retry' END, error='Recovered stale running task after worker interruption', next_attempt_at=CASE WHEN attempts >= max_attempts THEN NULL ELSE CURRENT_TIMESTAMP END, updated_at=CURRENT_TIMESTAMP WHERE task_id IN (SELECT task_id FROM tasks WHERE status='running' AND datetime(updated_at) < datetime('now', ? || ' seconds') ORDER BY updated_at ASC LIMIT ?) RETURNING task_id,status",
  ).bind("-" + staleSeconds, limit).all<{ task_id: string; status: string }>();
  return json({ recovered: rows.results?.length ?? 0, tasks: rows.results ?? [] });
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    if (url.pathname === "/health") {
      return request.method === "GET"
        ? json({ ok: true, service: "a1os-d1-task-queue" })
        : json({ error: "Method not allowed" }, 405);
    }
    const authorization = request.headers.get("authorization") ?? "";
    const match = authorization.match(/^Bearer\s+(.+)$/i);
    if (!match || !(await sameSecret(match[1], env.TASK_QUEUE_TOKEN ?? ""))) {
      return json({ error: "Unauthorized" }, 401);
    }
    try {
      if (url.pathname === "/v1/tasks" && request.method === "POST") return await enqueue(request, env);
      if (url.pathname === "/v1/tasks/pending" && request.method === "GET") return await pending(url, env);
      if (url.pathname === "/v1/tasks/recover" && request.method === "POST") return await recover(request, env);
      const taskRoute = url.pathname.match(/^\/v1\/tasks\/([A-Za-z0-9._:-]{1,120})(?:\/(claim|complete|fail))?$/);
      if (!taskRoute) return json({ error: "Not found" }, 404);
      const taskId = taskRoute[1];
      const action = taskRoute[2];
      if (!action && request.method === "GET") return await getTask(taskId, env);
      if (action === "claim" && request.method === "POST") return await claim(taskId, env);
      if (action === "complete" && request.method === "POST") return await complete(taskId, env);
      if (action === "fail" && request.method === "POST") return await fail(taskId, request, env);
      return json({ error: "Method not allowed" }, 405);
    } catch {
      return json({ error: "Task queue temporarily unavailable" }, 503);
    }
  },
};
