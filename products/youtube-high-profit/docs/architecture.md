# Architecture

Vercel hosts the operator console. Long-running research, TTS, visual generation and video rendering run in a worker runtime, not inside a serverless request.

```
Next.js
  ↓
FastAPI
  ↓
job orchestrator
  ├─ opportunity
  ├─ angle
  ├─ research
  ├─ script
  ├─ voice
  ├─ visuals
  ├─ timeline
  ├─ render
  ├─ thumbnail
  ├─ seo
  └─ chapters
  ↓
Supabase/Postgres + object storage
```

Every stage returns a JSON contract and referenced assets. Production providers are adapters; demo mode keeps the system verifiable without external credentials.

Optimization targets: demand, CTR, retention, watch time, production cost, publishing frequency and monetization fit.
