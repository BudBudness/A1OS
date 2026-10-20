# Jere's Car Wash and Parking

A1OS frontend vertical for the single-branch operation at Nsambya Road Railway Grounds, Kampala, Uganda.

## V1 scope
- Vehicle intake and queue tracking
- Wash service catalogue and prices
- Day and overnight parking records
- Customer and vehicle history
- Payment/receipt records
- Staff assignments
- Stock and operating expenses
- Daily operational and revenue reporting
- Repeat-customer/loyalty surfaces

## Platform boundaries
This vertical owns UI, forms, workflows and presentation only. A1OS Core owns identity, tenant resolution, authorization and RBAC. A1OS Platform owns APIs, persistence, infrastructure and audit records. No separate database, backend, auth authority or deployment platform may be added here.

## API contract gate
The UI calls the A1OS Platform API through `src/api/client.js`. The required resource endpoints must be implemented and authorized by the platform before live operations are enabled. An unavailable API is shown as an explicit unavailable state; the interface must not fabricate business records or silently store operational data in browser storage.

## Local verification
`npm ci`, `npm test`, `npm run build`.
