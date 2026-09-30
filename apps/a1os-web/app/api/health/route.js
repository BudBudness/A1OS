export async function GET() {
  return Response.json({
    status: "healthy",
    service: "a1os-web",
    timestamp: new Date().toISOString()
  });
}
