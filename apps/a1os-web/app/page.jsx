const checks = [
  ["Application", "Next.js / Vercel"],
  ["API", "FastAPI"],
  ["Data", "Supabase"],
  ["Deployment", "Provider HTTPS first"],
];

export default function Home() {
  return (
    <main className="shell">
      <header>
        <span className="eyebrow">A1OS</span>
        <h1>Operational intelligence, under human control.</h1>
        <p className="lede">A production interface for the A1OS platform. Deployment, API and readiness are exposed as independently verifiable layers.</p>
      </header>

      <section className="grid" aria-label="Platform status">
        {checks.map(([label, value]) => (
          <article className="card" key={label}>
            <span>{label}</span>
            <strong>{value}</strong>
          </article>
        ))}
      </section>

      <section className="status">
        <div>
          <span className="eyebrow">PRODUCTION GATE</span>
          <h2>Application layer</h2>
          <p>Custom DNS is not a prerequisite for verifying the deployed application.</p>
        </div>
        <div className="links">
          <a href="/api/health">Health</a>
          <a href="/api/readiness">Readiness</a>
        </div>
      </section>
    </main>
  );
}
