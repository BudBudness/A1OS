A1OS PRODUCT IMPLEMENTATION PHASE
===============================

RULE: A1OS CORE IS FROZEN
RULE: PRODUCT DEVELOPMENT OCCURS ABOVE THE CORE
RULE: EACH PRODUCT MUST SOLVE A REAL ORGANIZATIONAL PROBLEM
RULE: EACH DEPLOYMENT MUST BE CAPABLE OF GENERATING OR SUPPORTING REVENUE
RULE: ONE BACKEND, MANY INDUSTRY FRONTENDS — the A1OS Platform API is the shared
     multi-tenant backend; products are UI-only frontends consuming its APIs.

PLATFORM LAYER:
- products/a1os-platform-api — multi-tenant FastAPI backend (:3013). Auth
  (SSO-style opaque tokens, PBKDF2), organizations, users/roles/permissions,
  parties, products, double-entry ledger, inventory, notifications, audit,
  realtime WebSocket. One codebase serves every industry frontend.

PRODUCT IMPLEMENTATION PRIORITY:
1. Education OS
   - Little Oaks (legacy single-tenant monolith, live :3012/:8080)
   - Taibah
2. Charity / NGO OS
   - StramosWisdomCharityOrg
3. Business OS
   - Image Coffee Roastery  ← first Platform-API frontend (coffee ERP)
4. Music Label OS
   - Pyong Recordz Ltd
5. Future Domain OS Products

IMPLEMENTATION MODEL:
A1OS CORE
    ↓
SHARED IDENTITY / AUTHORIZATION / EXECUTION / MEMORY / KNOWLEDGE / AUDIT
    ↓
A1OS PLATFORM API (multi-tenant backend)
    ↓
INDUSTRY FRONTENDS (UI-only: school OS, coffee ERP, charity, music label)
    ↓
ORGANIZATION DEPLOYMENT
    ↓
REAL OPERATIONS
    ↓
REVENUE / EFFICIENCY / DATA / RETENTION
