import React from "react";
import { permissions } from "../rbac/permissions.js";

export function PermissionGate({ permission, children, fallback = null }) {
  return permissions.has(permission) ? children : fallback;
}
