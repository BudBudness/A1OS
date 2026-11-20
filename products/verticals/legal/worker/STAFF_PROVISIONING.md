# Legal staff provisioning — Cloudflare Access + D1

This is an operator-only procedure. Do not expose the D1 database to browsers and do not accept role assignments from client-side forms.

## Identity flow

1. Create a Cloudflare Access self-hosted application for the Legal hostname.
2. Restrict the Access policy to named firm identities and approved email domains. Require MFA.
3. Set the Worker's `ACCESS_TEAM_DOMAIN` to the exact Access team hostname (without `https://`) and `ACCESS_AUD` to the application audience tag.
4. The Worker verifies the `Cf-Access-Jwt-Assertion` signature against the Access JWKS, then checks issuer, audience, subject and email.
5. The verified Access subject must match an active row in `profiles.user_id`; email must also match. No automatic registration exists.

## Provision a staff profile

Obtain the exact Access subject from a verified Access JWT through a secure operator process. Never paste JWTs or private keys into GitHub, chat, tickets or source files.

Run this command from an authenticated operator environment after D1 is provisioned. Replace every placeholder and choose only a firm-approved role:

```bash
npx wrangler d1 execute barya-legal --remote --command \
  "INSERT INTO profiles (user_id,email,full_name,role,active) VALUES ('ACCESS_SUBJECT_UUID','person@example.org','Full Name','advocate',1);"
```

Allowed roles: `partner`, `advocate`, `clerk`, `finance`, `administrator`, `client`.

Only `partner` and `administrator` can create clients and matters. Other staff can see matters only after an explicit `matter_members` assignment. A matter creator is assigned to the matter automatically.

## Revoke access

Disable the profile in D1 immediately and remove the identity from the Cloudflare Access policy:

```sql
UPDATE profiles SET active = 0 WHERE user_id = 'ACCESS_SUBJECT_UUID';
```

## Matter assignment

```sql
INSERT INTO matter_members (matter_id,user_id,assignment_role)
VALUES ('MATTER_UUID','ACCESS_SUBJECT_UUID','advocate');
```

Review audit events after any role or assignment change. Role changes must be approved and performed by an authorized platform operator.
