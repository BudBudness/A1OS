import React from "react";
import { resource } from "../data/resource.js";

const customers = resource("/customers");

export function Customers() {
  return (
    <section>
      <h2>Customers</h2>
      <p>Customer data is owned by the A1OS Platform API.</p>
      <button onClick={() => customers.list()}>
        Load customers
      </button>
    </section>
  );
}
