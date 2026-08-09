import { describe, expect, it } from "vitest";
import {
  DEFAULT_ENDPOINTS,
  escapeHtml,
  overallFor,
  parseEndpoints,
  type ServiceStatus,
} from "../src/index";

const base = { url: "", failures: 0, lastCheckedAt: null } as const;

describe("parseEndpoints", () => {
  it("uses defaults when no override is configured", () => {
    expect(parseEndpoints({})).toEqual(DEFAULT_ENDPOINTS);
  });

  it("parses a JSON override", () => {
    const env = {
      ENDPOINTS_JSON: JSON.stringify([
        { name: "test", url: "https://example.com/health" },
      ]),
    };
    const eps = parseEndpoints(env);
    expect(eps).toHaveLength(1);
    expect(eps[0].name).toBe("test");
  });

  it("falls back to defaults on invalid JSON", () => {
    expect(parseEndpoints({ ENDPOINTS_JSON: "not json" })).toEqual(DEFAULT_ENDPOINTS);
  });
});

describe("overallFor", () => {
  const svc = (name: string, status: ServiceStatus["status"]): ServiceStatus => ({
    ...base,
    name,
    status,
  });

  it("reports ok when everything is ok", () => {
    expect(overallFor([svc("a", "ok"), svc("b", "ok")])).toBe("ok");
  });

  it("reports down when any service is down", () => {
    expect(overallFor([svc("a", "ok"), svc("b", "down")])).toBe("down");
  });

  it("reports unknown when there is no data yet", () => {
    expect(overallFor([svc("a", "unknown")])).toBe("unknown");
  });
});

describe("escapeHtml", () => {
  it("escapes dangerous characters", () => {
    expect(escapeHtml(`<script>"x"&'y'`)).toBe(
      "&lt;script&gt;&quot;x&quot;&amp;&#39;y&#39;",
    );
  });
});
