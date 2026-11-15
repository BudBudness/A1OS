function decode(value) {
  if (!/^[\w-]+$/.test(value)) throw new Error("Invalid JWT encoding");
  return Uint8Array.from(atob(value.replaceAll("-", "+").replaceAll("_", "/")), c => c.charCodeAt(0));
}

async function staffIdentity(request, env) {
  const token = request.headers.get("Cf-Access-Jwt-Assertion");
  if (!token || token.length > 8192 || !env.STAFF_ACCESS_AUD ||
      !env.STAFF_ACCESS_ISSUER || !env.STAFF_DIRECTOR_EMAIL || !env.STAFF_HEAD_EMAIL) return null;

  try {
    const parts = token.split(".");
    if (parts.length !== 3) return null;
    const [header, payload, signature] = parts;
    const parse = value => JSON.parse(new TextDecoder().decode(decode(value)));
    const { alg, kid } = parse(header);
    const claims = parse(payload);
    const now = Math.floor(Date.now() / 1000);
    if (alg !== "RS256" || typeof kid !== "string" || claims.iss !== env.STAFF_ACCESS_ISSUER ||
        !Array.isArray(claims.aud) || !claims.aud.includes(env.STAFF_ACCESS_AUD) ||
        !Number.isFinite(claims.exp) || claims.exp <= now ||
        (claims.nbf !== undefined && (!Number.isFinite(claims.nbf) || claims.nbf > now))) return null;

    const email = typeof claims.email === "string" ? claims.email.toLowerCase() : "";
    const role = email === env.STAFF_DIRECTOR_EMAIL.toLowerCase() ? "director" :
      email === env.STAFF_HEAD_EMAIL.toLowerCase() ? "head_teacher" : null;
    if (!role) return null;

    const response = await fetch(new URL("/cdn-cgi/access/certs", env.STAFF_ACCESS_ISSUER), {
      signal: AbortSignal.timeout(4000),
    });
    if (!response.ok) return null;
    const { keys } = await response.json();
    const jwk = keys.find(key => key.kid === kid && key.kty === "RSA");
    if (!jwk) return null;
    const algorithm = { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" };
    const key = await crypto.subtle.importKey("jwk", jwk, algorithm, false, ["verify"]);
    const verified = await crypto.subtle.verify(
      algorithm, key, decode(signature), new TextEncoder().encode(header + "." + payload),
    );
    return verified ? { email, role } : null;
  } catch {
    return null;
  }
}

const decisions = ["needs_review", "follow_up", "test_or_duplicate", "closed"];
const headers = { "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff" };
const json = (body, status = 200) => Response.json(body, { status, headers });

async function inbox(request, env, url, readBody) {
  const identity = await staffIdentity(request, env);
  if (!identity) return json({ error: "Unauthorized" }, 401);

  try {
    if (request.method === "GET") {
      const page = Number(url.searchParams.get("page") ?? 0);
      if (!Number.isInteger(page) || page < 0 || page > 10000) return json({ error: "Invalid page" }, 400);
      const { results, success } = await env.DB.prepare(`
        SELECT e.*, COALESCE(r.decision, 'needs_review') AS review_decision,
               COALESCE(r.assignee, '') AS assignee, COALESCE(r.next_action, '') AS next_action,
               CASE WHEN trim(COALESCE(e.phone, '')) = '' THEN 1
                 ELSE (SELECT COUNT(*) FROM enquiries AS shared WHERE shared.phone = e.phone)
               END AS shared_phone_count
        FROM enquiries e LEFT JOIN enquiry_reviews r ON r.enquiry_id = e.id
        WHERE (? = 1 OR r.decision IS NULL OR r.decision <> 'test_or_duplicate')
        ORDER BY e.created_at DESC, e.id DESC LIMIT 26 OFFSET ?
      `).bind(url.searchParams.get("include_tests") === "1" ? 1 : 0, page * 25).all();
      if (!success) return json({ error: "Inbox unavailable" }, 503);
      return json({ role: identity.role, enquiries: results.slice(0, 25), has_more: results.length > 25 });
    }

    if (request.method !== "POST") return json({ error: "Method not allowed" }, 405);
    if (request.headers.get("Origin") !== url.origin) return json({ error: "Origin rejected" }, 403);
    if (request.headers.get("Content-Type")?.split(";")[0].trim() !== "application/json") {
      return json({ error: "JSON required" }, 415);
    }
    let body;
    try {
      body = await readBody(request);
    } catch {
      return json({ error: "Invalid review body" }, 400);
    }
    if (!body || typeof body.id !== "string" || body.id.length > 128 || !body.id ||
        !decisions.includes(body.decision) || typeof body.assignee !== "string" ||
        body.assignee.length > 120 || typeof body.next_action !== "string" || body.next_action.length > 1000) {
      return json({ error: "Invalid review" }, 400);
    }
    const result = await env.DB.prepare(`
      INSERT INTO enquiry_reviews (enquiry_id, decision, assignee, next_action)
      SELECT e.id, ?, CASE WHEN ? THEN ? ELSE COALESCE(r.assignee, '') END, ?
      FROM enquiries e LEFT JOIN enquiry_reviews r ON r.enquiry_id = e.id WHERE e.id = ?
      ON CONFLICT(enquiry_id) DO UPDATE SET decision=excluded.decision, assignee=excluded.assignee,
        next_action=excluded.next_action, updated_at=strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
    `).bind(body.decision, identity.role === "director" ? 1 : 0, body.assignee.trim(), body.next_action.trim(), body.id).run();
    if (!result.success) return json({ error: "Inbox unavailable" }, 503);
    return result.meta.changes ? json({ ok: true }) : json({ error: "Enquiry not found" }, 404);
  } catch {
    return json({ error: "Inbox unavailable" }, 503);
  }
}
async function readBody(request) {
  const reader = request.body.getReader();
  const decoder = new TextDecoder();
  let size = 0;
  let body = "";
  for (;;) {
    const { done, value } = await reader.read();
    if (done) return JSON.parse(body + decoder.decode());
    size += value.byteLength;
    if (size > 16_384) {
      await reader.cancel();
      throw new RangeError("Request body is too large");
    }
    body += decoder.decode(value, { stream: true });
  }
}


export default {async fetch(req,env){
 const url=new URL(req.url);
 if(url.pathname==='/api/staff/enquiries') return inbox(req,env,url,readBody);
 const h={'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Content-Security-Policy':"default-src 'none'; script-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"};
 if(!await staffIdentity(req,env)) return new Response('Unauthorized',{status:401,headers:h});
 if(req.method!=='GET')return new Response(null,{status:405,headers:h});
 const js=url.pathname==='/staff-inbox.js';
 if(!js&&url.pathname!=='/'&&url.pathname!=='/staff.html')return new Response(null,{status:404,headers:h});
 h['Content-Type']=js?'text/javascript; charset=utf-8':'text/html; charset=utf-8';
 return new Response(js?"const element = (id) => document.getElementById(id);\nconst notice = element(\"notice\");\nconst records = element(\"records\");\nconst pages = element(\"pages\");\n\nlet page = 0;\nlet requestNumber = 0;\n\nasync function api(path = \"\", options = {}) {\n  const response = await fetch(\"/api/staff/enquiries\" + path, {\n    ...options,\n    headers: { \"Content-Type\": \"application/json\" },\n    cache: \"no-store\",\n  });\n  const data = await response.json();\n  if (!response.ok) throw new Error(data.error || \"Request failed\");\n  return data;\n}\n\nfunction render(row, role) {\n  const card = document.createElement(\"article\");\n  const title = document.createElement(\"h2\");\n  title.textContent = [row.parent_name, row.programme, row.created_at].filter(Boolean).join(\" · \");\n  const details = document.createElement(\"p\");\n  details.textContent = [row.child_name, row.child_age, row.phone, row.message,\n    row.shared_phone_count > 1 ? `Shared phone: ${row.shared_phone_count} submissions` : \"\"]\n    .filter(Boolean).join(\" · \");\n  const form = document.createElement(\"form\");\n  const decision = document.createElement(\"select\");\n  for (const [value, label] of [[\"needs_review\", \"Needs review\"], [\"follow_up\", \"Follow up\"],\n    [\"test_or_duplicate\", \"Test or duplicate\"], [\"closed\", \"Closed\"]]) {\n    decision.add(new Option(label, value));\n  }\n  decision.value = row.review_decision;\n  decision.setAttribute(\"aria-label\", \"Review decision\");\n  const assignee = document.createElement(\"input\");\n  assignee.placeholder = \"Assigned staff\";\n  assignee.setAttribute(\"aria-label\", \"Assigned staff\");\n  assignee.maxLength = 120;\n  assignee.value = row.assignee;\n  assignee.disabled = role !== \"director\";\n  const action = document.createElement(\"input\");\n  action.placeholder = \"Next action\";\n  action.setAttribute(\"aria-label\", \"Next action\");\n  action.maxLength = 1000;\n  action.value = row.next_action;\n  const save = document.createElement(\"button\");\n  save.textContent = \"Save review\";\n  form.append(decision, assignee, action, save);\n  form.addEventListener(\"submit\", async (event) => {\n    event.preventDefault();\n    save.disabled = true;\n    try {\n      await api(\"\", { method: \"POST\", body: JSON.stringify({\n        id: row.id, decision: decision.value, assignee: assignee.value, next_action: action.value,\n      }) });\n      notice.textContent = \"Review saved.\";\n    } catch (error) {\n      notice.textContent = error.message;\n    } finally {\n      save.disabled = false;\n    }\n  });\n  card.append(title, details, form);\n  return card;\n}\n\nasync function load(target) {\n  const currentRequest = ++requestNumber;\n  notice.textContent = \"\";\n  try {\n    const includeTests = element(\"include-tests\").checked;\n    const data = await api(\"?page=\" + target + \"&include_tests=\" + Number(includeTests));\n    if (currentRequest !== requestNumber) return;\n    page = target;\n    records.replaceChildren(...data.enquiries.map(row => render(row, data.role)));\n    pages.hidden = false;\n    element(\"previous\").disabled = page === 0;\n    element(\"next\").disabled = !data.has_more;\n    if (!data.enquiries.length) notice.textContent = includeTests ? \"No enquiries.\" : \"No enquiries in the follow-up queue.\";\n  } catch (error) {\n    notice.textContent = error.message;\n  }\n}\n\nelement(\"include-tests\").onchange = () => load(0);\nelement(\"previous\").onclick = () => load(page - 1);\nelement(\"next\").onclick = () => load(page + 1);\nload(0);\n":"<!doctype html>\n<html lang=\"en\">\n<meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n<meta name=\"robots\" content=\"noindex, nofollow\">\n<title>Little Oaks staff enquiries</title>\n<h1>Little Oaks staff enquiries</h1>\n<p id=\"notice\" role=\"status\"></p>\n<label><input id=\"include-tests\" type=\"checkbox\"> Show test and duplicate submissions</label>\n<nav id=\"pages\" hidden aria-label=\"Enquiry pages\">\n  <button id=\"previous\">Previous</button>\n  <button id=\"next\">Next</button>\n  <a href=\"/cdn-cgi/access/logout\">Sign out</a>\n</nav>\n<section id=\"records\" aria-label=\"Enquiries\"></section>\n<script src=\"/staff-inbox.js\" defer></script>\n</html>\n",{headers:h});
}};
