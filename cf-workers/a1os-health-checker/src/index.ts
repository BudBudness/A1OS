import type { ExportedHandler, ScheduledEvent, ExecutionContext } from "cloudflare:workers";

/**
 * A1OS external health checker.
 *
 * Probes the public A1OS endpoints from the Cloudflare edge on a cron
 * schedule, records per-service state in KV, observes external availability and alerts via ntfy only on DOWN /
 * RECOVERY transitions (no alert spam), and exposes JSON + HTML status pages.
 *
 * Bindings (see wrangler.jsonc):
 *   - HEALTH_STATE   KV                 — last known state per service
 *   - HEALTH_EVENTS  Analytics Engine   — one datapoint per probe (history)
 *   - NTFY_TOPIC     secret             — ntfy topic name or full ntfy URL
 *   - RUN_TOKEN      secret (optional)  — if set, GET /run requires ?token=
 *
 * Optional var:
 *   - ENDPOINTS_JSON — JSON array overriding the default endpoint list below
 */

export interface HealthEndpoint {
  name: string;
  url: string;
  /** Expected HTTP status; defaults to 200. */
  expectedStatus?: number;
  /** If set, the response body must contain this substring. */
  keyword?: string;
  timeoutMs?: number;
}

export interface Env {
  HEALTH_STATE: KVNamespace;
  HEALTH_EVENTS: AnalyticsEngineDataset;
  NTFY_TOPIC: string;
  ENDPOINTS_JSON?: string;
  RUN_TOKEN?: string;
}

export interface EndpointState {
  status: "ok" | "down";
  failures: number;
  lastCheckedAt: string;
  lastOkAt?: string;
  lastFailAt?: string;
  message?: string;
}

export interface ServiceStatus extends Omit<EndpointState, "status"> {
  name: string;
  url: string;
  status: "ok" | "down" | "unknown";
}

export const DEFAULT_ENDPOINTS: HealthEndpoint[] = [
  { name: "a1os-core", url: "https://edge.pyongcity.org/v1/health" },
  { name: "pos-edge", url: "https://pos.edge.pyongcity.org/v1/health" },
  { name: "edu-api", url: "https://little-oaks.pyongcity.org/api/health" },
  { name: "edu-frontend", url: "https://little-oaks.pyongcity.org/" },
  { name: "roastery", url: "https://roastery.pyongcity.org/login" },
  { name: "roastery-api", url: "https://roastery-api.pyongcity.org/v1/health" },
];

const JSON_HEADERS = {
  "content-type": "application/json; charset=utf-8",
  "cache-control": "no-store",
  "x-content-type-options": "nosniff",
};

export function parseEndpoints(env: { ENDPOINTS_JSON?: string }): HealthEndpoint[] {
  if (env.ENDPOINTS_JSON) {
    try {
      const parsed = JSON.parse(env.ENDPOINTS_JSON) as HealthEndpoint[];
      if (Array.isArray(parsed) && parsed.length > 0) return parsed;
      console.error("ENDPOINTS_JSON did not parse to a non-empty array; using defaults");
    } catch (err) {
      console.error("invalid ENDPOINTS_JSON:", err);
    }
  }
  return DEFAULT_ENDPOINTS;
}

export function overallFor(services: ServiceStatus[]): "ok" | "down" | "unknown" {
  if (services.length === 0) return "unknown";
  if (services.some((s) => s.status === "down")) return "down";
  if (services.some((s) => s.status === "unknown")) return "unknown";
  return "ok";
}

export function escapeHtml(value: string): string {
  const map: Record<string, string> = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  };
  return value.replace(/[&<>"']/g, (c) => map[c]);
}

async function readState(env: Env, key: string): Promise<EndpointState | null> {
  const raw = await env.HEALTH_STATE.get(key);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as EndpointState;
  } catch {
    return null;
  }
}

async function notify(env: Env, text: string): Promise<void> {
  const topic = (env.NTFY_TOPIC ?? "").trim();
  if (!topic) return;
  const url = /^https?:\/\//.test(topic) ? topic : `https://ntfy.sh/${encodeURIComponent(topic)}`;
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: {
        Title: "A1OS health alert",
        Priority: "3",
        "Content-Type": "text/plain",
      },
      body: text,
    });
    if (!res.ok) console.error("ntfy notify failed:", res.status);
  } catch (err) {
    console.error("ntfy notify error:", err);
  }
}

async function checkEndpoint(env: Env, ep: HealthEndpoint): Promise<void> {
  const key = `state:${ep.name}`;
  const prev = await readState(env, key);
  const startedAt = Date.now();
  let ok: boolean;
  let message: string;

  try {
    const res = await fetch(ep.url, {
      method: "GET",
      redirect: "follow",
      headers: { "user-agent": "a1os-health-checker/1.0" },
      signal: AbortSignal.timeout(ep.timeoutMs ?? 8_000),
    });
    const expected = ep.expectedStatus ?? 200;
    ok = res.status === expected;
    message = `HTTP ${res.status}`;
    if (ok && ep.keyword) {
      const body = await res.text();
      ok = body.includes(ep.keyword);
      message = ok ? message : `missing keyword "${ep.keyword}"`;
    }
    if (!ok) message = `${ep.url} -> ${message}`;
  } catch (err) {
    ok = false;
    message = `${ep.url} -> ${err instanceof Error ? err.message : String(err)}`;
  }

  const latencyMs = Date.now() - startedAt;

  // Non-blocking: one datapoint per probe so history is queryable via SQL.
  env.HEALTH_EVENTS.writeDataPoint({
    indexes: [ep.name],
    doubles: [latencyMs, ok ? 1 : 0],
    blobs: [ep.url, message],
  });

  const now = new Date().toISOString();
  const current: EndpointState = {
    status: ok ? "ok" : "down",
    failures: ok ? 0 : (prev?.status === "down" ? prev.failures + 1 : 1),
    lastCheckedAt: now,
    lastOkAt: ok ? now : prev?.lastOkAt,
    lastFailAt: ok ? prev?.lastFailAt : now,
    message,
  };
  await env.HEALTH_STATE.put(key, JSON.stringify(current));
  console.log(`[${ep.name}] ${ok ? "ok" : "down"} ${message} (${latencyMs}ms)`);

  // Alert only on state transitions to avoid spamming ntfy every 5 minutes.
  const prevStatus = prev?.status ?? "unknown";
  if (ok && prevStatus !== "ok") {
    await notify(env, `[A1OS] RECOVERED: ${ep.name} (${message}, ${latencyMs}ms)`);
  } else if (!ok && prevStatus !== "down") {
    await notify(env, `[A1OS] DOWN: ${ep.name} - ${message}`);
  }
}

async function collectStatus(env: Env): Promise<ServiceStatus[]> {
  const services: ServiceStatus[] = [];
  for (const ep of parseEndpoints(env)) {
    const state = await readState(env, `state:${ep.name}`);
    services.push({
      name: ep.name,
      url: ep.url,
      status: state?.status ?? "unknown",
      failures: state?.failures ?? 0,
      lastCheckedAt: state?.lastCheckedAt ?? null,
      lastOkAt: state?.lastOkAt,
      lastFailAt: state?.lastFailAt,
      message: state?.message,
    });
  }
  return services;
}

function renderHtml(services: ServiceStatus[]): Response {
  const rows = services
    .map((s) => {
      const color = s.status === "ok" ? "#16a34a" : s.status === "down" ? "#dc2626" : "#f59e0b";
      return [
        `<tr>`,
        `<td style="padding:8px;border-bottom:1px solid #eee">${escapeHtml(s.name)}</td>`,
        `<td style="padding:8px;border-bottom:1px solid #eee"><span style="color:${color}">${s.status}</span></td>`,
        `<td style="padding:8px;border-bottom:1px solid #eee">${s.lastCheckedAt ? escapeHtml(s.lastCheckedAt) : "-"}</td>`,
        `<td style="padding:8px;border-bottom:1px solid #eee">${s.message ? escapeHtml(s.message) : "-"}</td>`,
        `</tr>`,
      ].join("");
    })
    .join("");
  const html = [
    `<!doctype html><html lang="en"><head><meta charset="utf-8">`,
    `<meta name="viewport" content="width=device-width,initial-scale=1"><title>A1OS status</title></head>`,
    `<body style="font-family:system-ui,sans-serif;max-width:760px;margin:2rem auto;padding:0 1rem">`,
    `<h1>A1OS status</h1>`,
    `<table style="border-collapse:collapse;width:100%"><thead><tr>`,
    `<th style="text-align:left;padding:8px">Service</th><th style="text-align:left;padding:8px">Status</th>`,
    `<th style="text-align:left;padding:8px">Last check</th><th style="text-align:left;padding:8px">Message</th>`,
    `</tr></thead><tbody>${rows}</tbody></table>`,
    `</body></html>`,
  ].join("");
  return new Response(html, {
    status: 200,
    headers: {
      "content-type": "text/html; charset=utf-8",
      "cache-control": "no-store",
      "x-content-type-options": "nosniff",
    },
  });
}

function json(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data, null, 2), { status, headers: JSON_HEADERS });
}

export default {
  async scheduled(_event: ScheduledEvent, env: Env, _ctx: ExecutionContext): Promise<void> {
    const endpoints = parseEndpoints(env);
    console.log(`running health check for ${endpoints.length} endpoints`);
    const results = await Promise.allSettled(endpoints.map((ep) => checkEndpoint(env, ep)));
    for (const r of results) {
      if (r.status === "rejected") console.error("health check rejected:", r.reason);
    }
  },

  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === "/run") {
      // Optional on-demand check, protected only when RUN_TOKEN is set.
      if (env.RUN_TOKEN && url.searchParams.get("token") !== env.RUN_TOKEN) {
        return json({ error: "forbidden" }, 403);
      }
      await Promise.allSettled(parseEndpoints(env).map((ep) => checkEndpoint(env, ep)));
      const services = await collectStatus(env);
      return json({ overall: overallFor(services), services });
    }

    if (url.pathname === "/status" || url.pathname === "/") {
      const services = await collectStatus(env);
      return url.pathname === "/"
        ? renderHtml(services)
        : json({
            overall: overallFor(services),
            updatedAt: new Date().toISOString(),
            services,
          });
    }

    return json({
      ok: true,
      service: "a1os-health-checker",
      endpoints: ["/", "/status", "/run?token=..."],
    });
  },
} satisfies ExportedHandler<Env>;
