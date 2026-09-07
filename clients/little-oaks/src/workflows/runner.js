import { api } from "../api/client.js";

export async function runWorkflow(workflow, input = {}) {
  if (!workflow || !workflow.name) {
    throw new Error("Invalid A1OS workflow");
  }

  return api.post("/workflows/execute", {
    workflow: workflow.name,
    input
  });
}
