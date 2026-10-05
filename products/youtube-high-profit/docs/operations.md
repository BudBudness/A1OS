# Operations

## Local
```bash
cd products/youtube-high-profit
docker compose up --build
```

Frontend: http://localhost:3000
API: http://localhost:8000/health

Copy .env.example to .env. Demo mode requires no paid provider.

Production:
1. Vercel → frontend root.
2. Supabase → run migration.
3. Container runtime → API/worker/render services.
4. Add encrypted provider secrets.
5. Verify health, job lifecycle and render/package outputs.
6. Enable publishing integrations only after the production gates pass.
