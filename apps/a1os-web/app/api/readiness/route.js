export async function GET() {
  return Response.json({
    status: "ready",
    service: "a1os-web",
    checks: { application: "ok" },
    timestamp: new Date().toISOString()
  });
}
