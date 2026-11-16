const fields = {
  parent_name: [true, 120],
  child_name: [true, 120],
  child_age: [true, 40],
  programme: [false, 120],
  phone: [true, 40],
  message: [false, 2000],
};

function response(status, error) {
  return Response.json(error ? { error } : { ok: true }, {
    status, headers: { "Cache-Control": "no-store" },
  });
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

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname !== "/api/enquiries") return env.ASSETS.fetch(request);
    if (request.method !== "POST") return response(405, "Method not allowed");
    if (request.headers.get("Origin") !== url.origin) return response(403, "Origin rejected");
    if (request.headers.get("Content-Type")?.split(";")[0].trim().toLowerCase() !== "application/json") {
      return response(415, "JSON required");
    }
    if (!env.TURNSTILE_SECRET_KEY || !env.DB) return response(503, "Enquiries unavailable");

    let body;
    try {
      body = await readBody(request);
    } catch (error) {
      return error instanceof RangeError ? response(413, "Enquiry too large") : response(400, "Invalid JSON");
    }
    if (!body || typeof body !== "object" || Array.isArray(body)) return response(400, "Invalid enquiry");
    const values = [];
    for (const [key, [required, max]] of Object.entries(fields)) {
      const value = typeof body[key] === "string" ? body[key].trim() : null;
      if (value === null || (required && !value) || value.length > max) {
        return response(400, "Invalid enquiry fields");
      }
      values.push(value);
    }

    const token = body.turnstileToken;
    if (typeof token !== "string" || !token || token.length > 2048) {
      return response(400, "Verification required");
    }
    try {
      const verification = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", {
        method: "POST",
        body: new URLSearchParams({ secret: env.TURNSTILE_SECRET_KEY, response: token }),
        signal: AbortSignal.timeout(5000),
      });
      if (!verification.ok) return response(503, "Verification unavailable");
      const proof = await verification.json();
      if (!proof.success || proof.hostname !== url.hostname || proof.action !== "enquiry") {
        return response(403, "Verification failed");
      }

      const result = await env.DB.prepare(
        "INSERT INTO enquiries (id, parent_name, child_name, child_age, programme, phone, message) VALUES (?, ?, ?, ?, ?, ?, ?)"
      ).bind(crypto.randomUUID(), ...values).run();
      if (!result.success) return response(503, "Enquiries unavailable");
      return response(201);
    } catch {
      return response(503, "Enquiries unavailable");
    }
  },
};
