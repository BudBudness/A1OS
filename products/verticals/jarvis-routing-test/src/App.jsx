import React from "react";
import { api } from "./api/client.js";
import { auth } from "./core/auth.js";
import { tenant } from "./core/tenant.js";
import { permissions } from "./rbac/permissions.js";

export function App() {
  return (
    <main>
      <h1>A1OS Vertical</h1>
      <p>Frontend runtime connected to the A1OS shared control plane.</p>
      <section>
        <strong>API:</strong> {api.provider}
      </section>
      <section>
        <strong>Authentication:</strong> {auth.owner}
      </section>
      <section>
        <strong>Tenancy:</strong> {tenant.owner}
      </section>
      <section>
        <strong>RBAC:</strong> {permissions.owner}
      </section>
    </main>
  );
}
