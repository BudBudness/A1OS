import React from "react";
import { api } from "./api/client.js";
import { auth } from "./core/auth.js";
import { tenant } from "./core/tenant.js";
import { permissions } from "./rbac/permissions.js";

function LittleOaksProfile() {
  return (
    <section
      aria-label="Little Oaks Montessori profile"
      style={{
        maxWidth: "960px",
        margin: "40px auto",
        padding: "32px",
        borderRadius: "20px",
        background: "#fffdf5",
        border: "1px solid #d9e6d5",
        boxShadow: "0 8px 30px rgba(0,0,0,0.06)",
        lineHeight: 1.6,
      }}
    >
      <header>
        <p
          style={{
            margin: 0,
            fontSize: "0.85rem",
            fontWeight: 700,
            letterSpacing: "0.12em",
            textTransform: "uppercase",
            color: "#176b3a",
          }}
        >
          NURTURE · EXPLORE · GROW
        </p>

        <h2
          style={{
            margin: "8px 0 4px",
            fontSize: "2rem",
            color: "#145c35",
          }}
        >
          Little Oaks Montessori Kindergarten &amp; Day Care Centre (U) Limited
        </h2>

        <p style={{ margin: 0, color: "#555" }}>
          A Montessori-inspired early childhood learning and daycare centre
          serving children from <strong>18 months to 6 years</strong>.
        </p>
      </header>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
          gap: "20px",
          marginTop: "28px",
        }}
      >
        <div>
          <h3>About Little Oaks</h3>
          <p>
            Little Oaks provides a safe, nurturing and engaging environment
            combining Montessori-inspired early learning with dedicated
            full-day daycare services.
          </p>
        </div>

        <div>
          <h3>Age Range</h3>
          <p>
            <strong>18 months to 6 years</strong>
          </p>
          <p>
            Early childhood programmes designed around foundational learning,
            social development, independence and exploration.
          </p>
        </div>

        <div>
          <h3>Programmes</h3>
          <ul>
            <li>Montessori-inspired early education</li>
            <li>Full-day daycare</li>
            <li>Foundational literacy and early development</li>
            <li>Creative arts and social development</li>
          </ul>
        </div>

        <div>
          <h3>Location &amp; Contact</h3>
          <p>
            <strong>Nyamitanga, Mbarara</strong>
            <br />
            Along Isingiro Road, Uganda
          </p>
          <p>
            <strong>Phone:</strong> 0762 023393
          </p>
          <p>
            <strong>WhatsApp:</strong> +256 762 023393 · +256 705 074279
          </p>
          <p>
            <strong>Email:</strong> admin@littleoaksmontessori.ac.ug
          </p>
          <p>
            <strong>Website:</strong> www.littleoaksmontessori.ac.ug
          </p>
        </div>
      </div>

      <footer
        style={{
          marginTop: "28px",
          paddingTop: "20px",
          borderTop: "1px solid #d9e6d5",
          color: "#555",
        }}
      >
        <strong>URSB Registration:</strong> 80034303611084
      </footer>
    </section>
  );
}

export function App() {
  return (
    <main>
      <section
        style={{
          maxWidth: "960px",
          margin: "40px auto 0",
          padding: "0 32px",
        }}
      >
        <h1>A1OS Vertical</h1>
        <p>
          Frontend runtime connected to the A1OS shared control plane.
        </p>
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
      </section>

      <LittleOaksProfile />
    </main>
  );
}
