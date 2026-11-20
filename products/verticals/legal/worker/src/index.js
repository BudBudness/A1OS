import { createRemoteJWKSet, jwtVerify } from "jose";

const JSON_HEADERS = { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" };
const PRIVILEGED = new Set(["partner", "administrator"]);
const uuid = () => crypto.randomUUID();
const json = (data, status = 200) => new Response(JSON.stringify(data), { status, headers: JSON_HEADERS });
const fail = (message, status) => json({ error: message }, status);
const clean = (v) => typeof v === "string" ? v.trim() : "";

async function identity(request, env) {
  const issuer = `https://${env.ACCESS_TEAM_DOMAIN}`;
  if (!env.ACCESS_TEAM_DOMAIN || !env.ACCESS_AUD || env.ACCESS_TEAM_DOMAIN.startsWith("REPLACE_") || env.ACCESS_AUD.startsWith("REPLACE_")) {
    throw new Error("Cloudflare Access issuer and audience are not configured");
  }
  const token = request.headers.get("Cf-Access-Jwt-Assertion");
  if (!token) return null;
  const jwks = createRemoteJWKSet(new URL(`${issuer}/cdn-cgi/access/certs`));
  const { payload } = await jwtVerify(token, jwks, { issuer, audience: env.ACCESS_AUD });
  if (!payload.sub || !payload.email) return null;
  return { id: String(payload.sub), email: String(payload.email).toLowerCase() };
}

async function actor(request, env) {
  const who = await identity(request, env);
  if (!who) return null;
  return env.DB.prepare("SELECT user_id,email,full_name,role,active FROM profiles WHERE user_id=? AND lower(email)=? AND active=1")
    .bind(who.id, who.email).first();
}
const canSeeAll = (user) => PRIVILEGED.has(user.role);
async function audit(env, user, action, entity, id, matterId = null) {
  await env.DB.prepare("INSERT INTO audit_events (id,actor_id,matter_id,action,entity_type,entity_id) VALUES (?,?,?,?,?,?)")
    .bind(uuid(), user.user_id, matterId, action, entity, id).run();
}
async function allowedMatter(env, user, matterId) {
  if (canSeeAll(user)) return !!await env.DB.prepare("SELECT id FROM matters WHERE id=?").bind(matterId).first();
  return !!await env.DB.prepare("SELECT m.id FROM matters m JOIN matter_members mm ON mm.matter_id=m.id WHERE m.id=? AND mm.user_id=?")
    .bind(matterId, user.user_id).first();
}
async function rows(env, sql, user, all = false) {
  const statement = all || canSeeAll(user) ? sql : sql.replace(" WHERE ", " WHERE m.id IN (SELECT matter_id FROM matter_members WHERE user_id=?) AND ");
  const result = all || canSeeAll(user)
    ? await env.DB.prepare(sql).all()
    : await env.DB.prepare(statement).bind(user.user_id).all();
  return result.results || [];
}
async function workspace(env, user) {
  const matterSql = canSeeAll(user)
    ? "SELECT m.*, c.legal_name AS client FROM matters m LEFT JOIN clients c ON c.id=m.client_id ORDER BY m.created_at DESC"
    : "SELECT m.*, c.legal_name AS client FROM matters m LEFT JOIN clients c ON c.id=m.client_id WHERE m.id IN (SELECT matter_id FROM matter_members WHERE user_id=?) ORDER BY m.created_at DESC";
  const matterStatement = canSeeAll(user) ? env.DB.prepare(matterSql) : env.DB.prepare(matterSql).bind(user.user_id);
  const matters = await matterStatement.all();
  const matterIds = matters.results.map(x => x.id);
  const scoped = async (table, order, where = "") => {
    if (!matterIds.length) return [];
    const marks = matterIds.map(() => "?").join(",");
    const result = await env.DB.prepare(`SELECT * FROM ${table} WHERE matter_id IN (${marks}) ${where} ORDER BY ${order}`)
      .bind(...matterIds).all();
    return result.results || [];
  };
  const clients = canSeeAll(user)
    ? (await env.DB.prepare("SELECT id,client_number,legal_name,client_type,status,phone,email FROM clients ORDER BY created_at DESC").all()).results
    : (await env.DB.prepare("SELECT DISTINCT c.id,c.client_number,c.legal_name,c.client_type,c.status,c.phone,c.email FROM clients c JOIN matters m ON m.client_id=c.id WHERE m.id IN (SELECT matter_id FROM matter_members WHERE user_id=?) ORDER BY c.legal_name").bind(user.user_id).all()).results;
  const [deadlines,tasks,documents,invoices,research,auditEvents] = await Promise.all([
    scoped("deadlines","deadline_at","AND status='open'"),
    scoped("tasks","due_at","AND status!='completed'"),
    scoped("documents","created_at DESC"),
    scoped("invoices","created_at DESC"),
    scoped("research","created_at DESC"),
    (async()=>{ if(!matterIds.length)return []; const marks=matterIds.map(()=>"?").join(","); return (await env.DB.prepare(`SELECT * FROM audit_events WHERE matter_id IN (${marks}) ORDER BY created_at DESC LIMIT 50`).bind(...matterIds).all()).results; })()
  ]);
  return { matters: matters.results, clients, deadlines, tasks, documents: documents.map(({storage_path,...d})=>d), invoices, research, audit: auditEvents };
}
async function handle(request, env) {
  const url = new URL(request.url);
  if (url.pathname === "/health") return json({ ok: true, service: "barya-legal-api" });
  if (!url.pathname.startsWith("/api/")) return env.ASSETS ? env.ASSETS.fetch(request) : fail("Static assets binding is not configured",503);
  let user;
  try { user = await actor(request, env); } catch (e) { return fail("Identity verification failed or Access is not configured",503); }
  if (!user) return fail("Cloudflare Access authentication required",401);
  if (url.pathname === "/api/session" && request.method === "GET") return json({ user });
  if (url.pathname === "/api/workspace" && request.method === "GET") {
    try { return json(await workspace(env,user)); } catch { return fail("Unable to load practice data",500); }
  }
  if (url.pathname === "/api/clients" && request.method === "POST") {
    if (!PRIVILEGED.has(user.role)) return fail("Insufficient role",403);
    const body = await request.json();
    const legalName = clean(body.legal_name);
    if (!legalName) return fail("legal_name is required",400);
    const id=uuid(), number=clean(body.client_number)||`BB-C-${Date.now()}`;
    try {
      await env.DB.prepare("INSERT INTO clients (id,client_number,client_type,legal_name,phone,email,address,created_by) VALUES (?,?,?,?,?,?,?,?)")
        .bind(id,number,clean(body.client_type)||"individual",legalName,clean(body.phone)||null,clean(body.email)||null,clean(body.address)||null,user.user_id).run();
      await audit(env,user,"client_created","clients",id);
      return json({id},201);
    } catch { return fail("Client creation failed; verify unique client number and database schema",409); }
  }
  if (url.pathname === "/api/matters" && request.method === "POST") {
    if (!PRIVILEGED.has(user.role)) return fail("Insufficient role",403);
    const body=await request.json(), title=clean(body.title), number=clean(body.matter_number), clientId=clean(body.client_id);
    if (!title||!number||!clientId) return fail("matter_number, title and client_id are required",400);
    const id=uuid();
    try {
      await env.DB.batch([
        env.DB.prepare("INSERT INTO matters (id,matter_number,title,client_id,practice_area,matter_type,status,description,created_by) VALUES (?,?,?,?,?,?, 'intake',?,?)")
          .bind(id,number,title,clientId,clean(body.practice_area)||"Advisory",clean(body.matter_type)||null,clean(body.description)||null,user.user_id),
        env.DB.prepare("INSERT INTO matter_members (matter_id,user_id,assignment_role) VALUES (?,?,?)").bind(id,user.user_id,user.role),
        env.DB.prepare("INSERT INTO audit_events (id,actor_id,matter_id,action,entity_type,entity_id) VALUES (?,?,?,?,?,?)").bind(uuid(),user.user_id,id,"matter_created","matters",id)
      ]);
      return json({id},201);
    } catch { return fail("Matter creation failed; verify client and unique matter number",409); }
  }
  const docMatch=url.pathname.match(/^\/api\/documents\/([0-9a-f-]+)$/i);
  if (docMatch && request.method==="GET") {
    const doc=await env.DB.prepare("SELECT * FROM documents WHERE id=?").bind(docMatch[1]).first();
    if (!doc) return fail("Document not found",404);
    if (!await allowedMatter(env,user,doc.matter_id)) return fail("Matter access denied",403);
    const object=await env.DOCUMENTS.get(doc.storage_path);
    if (!object) return fail("Document object missing",404);
    const headers=new Headers(JSON_HEADERS); headers.set("content-type",doc.mime_type||"application/octet-stream");
    headers.set("content-disposition",`attachment; filename="${doc.title.replace(/["\\r\\n]/g,"_")}"`);
    return new Response(object.body,{headers});
  }
  if (url.pathname==="/api/documents" && request.method==="POST") {
    const matterId=clean(request.headers.get("x-matter-id"));
    if (!matterId || !await allowedMatter(env,user,matterId)) return fail("Matter access denied",403);
    const title=clean(request.headers.get("x-document-title")), type=clean(request.headers.get("x-document-type"))||"file";
    const length = Number(request.headers.get("content-length") || 0);
    if (!title || !request.body) return fail("Document title and body are required",400);
    if (!length || length > 25 * 1024 * 1024) return fail("Document upload must include Content-Length and be no larger than 25 MB",413);
    const bytes = await request.arrayBuffer();
    if (bytes.byteLength > 25 * 1024 * 1024) return fail("Document exceeds the 25 MB upload limit",413);
    const id=uuid(), key=`matters/${matterId}/${id}`;
    await env.DOCUMENTS.put(key,bytes,{httpMetadata:{contentType:request.headers.get("content-type")||"application/octet-stream"}});
    try {
      await env.DB.prepare("INSERT INTO documents (id,matter_id,title,document_type,storage_path,mime_type,uploaded_by) VALUES (?,?,?,?,?,?,?)")
        .bind(id,matterId,title,type,key,request.headers.get("content-type"),user.user_id).run();
      await audit(env,user,"document_uploaded","documents",id,matterId);
      return json({id},201);
    } catch { await env.DOCUMENTS.delete(key); return fail("Document metadata write failed",500); }
  }
  return fail("Not found",404);
}
export default { fetch(request,env) { return handle(request,env).catch(()=>fail("Internal server error",500)); } };
