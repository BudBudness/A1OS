// The executor must use task_id to deduplicate any external side effects.
export async function processTaskBatch(store, executeTask, limit = 3) {
  if (!Number.isInteger(limit) || limit < 1 || limit > 5) {
    throw new RangeError("Task batch limit must be an integer from 1 to 5");
  }

  const recovered = await store.recoverExpired();
  let processed = 0;
  let lostLeases = 0;

  while (processed < limit) {
    const task = await store.claimNext();
    if (!task) break;

    let result;
    try {
      result = await executeTask({
        task_id: task.task_id,
        target: task.target,
        role: task.role,
        action: task.action,
        data: task.payload,
      });
    } catch (error) {
      result = { error: error instanceof Error ? error.message : String(error) };
    }

    const recorded = result?.status === "completed"
      ? await store.complete(task.task_id, task.lease_token)
      : await store.fail(task.task_id, task.lease_token, result?.error ?? "Task execution failed");
    if (!recorded) lostLeases += 1;
    processed += 1;
  }

  return { recovered, processed, lostLeases };
}
