import test from "node:test";
import assert from "node:assert/strict";

import worker from "../worker/index.mjs";

const validBody = {
  parent_name: "Test Parent",
  child_name: "Test Child",
  child_age: "4 years",
  programme: "Montessori Nursery",
  phone: "+256700000001",
  message: "Please contact me about enrolment.",
  turnstileToken: "valid-test-token",
};

function makeEnv({ verification = { success: true, hostname: "school.example", action: "enquiry" }, dbSuccess = true } = {}) {
  const inserted = [];
  const env = {
    TURNSTILE_SECRET_KEY: "test-secret",
    DB: {
      prepare(sql) {
        assert.match(sql, /INSERT INTO enquiries/);
        return {
          bind(...values) {
            inserted.push(values);
            return { run: async () => ({ success: dbSuccess }) };
          },
        };
      },
    },
  };
  const originalFetch = globalThis.fetch;
  globalThis.fetch = async (url, options) => {
    assert.equal(String(url), "https://challenges.cloudflare.com/turnstile/v0/siteverify");
    assert.equal(options.method, "POST");
    return Response.json(verification);
  };
  return {
    env,
    inserted,
    restore() {
      globalThis.fetch = originalFetch;
    },
  };
}

function request(body = validBody, { method = "POST", origin = "https://school.example", contentType = "application/json" } = {}) {
  return new Request("https://school.example/api/enquiries", {
    method,
    headers: { Origin: origin, "Content-Type": contentType },
    body: method === "GET" ? undefined : JSON.stringify(body),
  });
}

test("accepts a valid enquiry and inserts only validated fields", async () => {
  const mock = makeEnv();
  try {
    const response = await worker.fetch(request(), mock.env);
    assert.equal(response.status, 201);
    assert.equal((await response.json()).ok, true);
    assert.equal(mock.inserted.length, 1);
    assert.equal(mock.inserted[0].length, 7);
    assert.equal(mock.inserted[0][1], "Test Parent");
    assert.equal(mock.inserted[0][2], "Test Child");
  } finally {
    mock.restore();
  }
});

test("rejects cross-origin submissions before verification or persistence", async () => {
  const mock = makeEnv();
  try {
    const response = await worker.fetch(request(validBody, { origin: "https://attacker.example" }), mock.env);
    assert.equal(response.status, 403);
    assert.equal(mock.inserted.length, 0);
  } finally {
    mock.restore();
  }
});

test("rejects non-JSON submissions", async () => {
  const mock = makeEnv();
  try {
    const response = await worker.fetch(request(validBody, { contentType: "text/plain" }), mock.env);
    assert.equal(response.status, 415);
    assert.equal(mock.inserted.length, 0);
  } finally {
    mock.restore();
  }
});

test("rejects missing required fields", async () => {
  const mock = makeEnv();
  try {
    const response = await worker.fetch(request({ ...validBody, parent_name: " " }), mock.env);
    assert.equal(response.status, 400);
    assert.equal(mock.inserted.length, 0);
  } finally {
    mock.restore();
  }
});

test("rejects Turnstile proof for the wrong hostname or action", async () => {
  const mock = makeEnv({ verification: { success: true, hostname: "attacker.example", action: "login" } });
  try {
    const response = await worker.fetch(request(), mock.env);
    assert.equal(response.status, 403);
    assert.equal(mock.inserted.length, 0);
  } finally {
    mock.restore();
  }
});

test("fails closed when D1 persistence fails", async () => {
  const mock = makeEnv({ dbSuccess: false });
  try {
    const response = await worker.fetch(request(), mock.env);
    assert.equal(response.status, 503);
  } finally {
    mock.restore();
  }
});

test("rejects methods other than POST on the enquiry endpoint", async () => {
  const mock = makeEnv();
  try {
    const response = await worker.fetch(request(validBody, { method: "GET" }), mock.env);
    assert.equal(response.status, 405);
    assert.equal(mock.inserted.length, 0);
  } finally {
    mock.restore();
  }
});
