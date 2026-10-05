# YouTube High Profit

AI YouTube Video Production Engine.

Topic → opportunity → angle → research → script → voice → visuals → timeline → edit → thumbnail/SEO/chapters → publish-ready package.

This is a deterministic production system, not a general autonomous agent. Each stage is explicit, versioned, retryable and independently reviewable.

## Stack
- Frontend: Next.js
- API/worker: FastAPI + Python
- Data: Supabase/PostgreSQL
- Heavy media: Docker worker + FFmpeg
- Source control: GitHub
- Web deployment: Vercel

Filmora is not assumed to expose a stable CLI. FFmpeg/Python is the canonical automated renderer; Filmora can be integrated later through a verified project/export adapter.

See docs/architecture.md and docs/verification.md.
