#!/usr/bin/env node
/**
 * A1OS queue executor adapter. Explicitly registered handlers only.
 * No shell evaluation, dynamic imports, or arbitrary remote code execution.
 */
const endpoint = process.env.A1OS_QUEUE_URL?.replace(/\/$/, '');
const token = process.env.A1OS_QUEUE_TOKEN;
if (!endpoint || !token) {
  console.error('A1OS_QUEUE_URL and A1OS_QUEUE_TOKEN are required');
  process.exit(2);
}
const handlers = new Map([
  ['staging:smoke:noop', async () => ({ ok: true })],
]);
async function api(path, method = 'GET', body) {
  const response = await fetch(endpoint + path, {
    method,
    headers: {
      authorization: 'Bearer ' + token,
      ...(body === undefined ? {} : { 'content-type': 'application/json' }),
    },
    body: body === undefined ? undefined : JSON.stringify(body),
    signal: AbortSignal.timeout(15000),
  });
  const data = await response.json();
  if (!response.ok && response.status !== 409) throw Error('Queue HTTP ' + response.status);
  return { status: response.status, data };
}
const pending = await api('/v1/tasks/pending?limit=20');
if (pending.status !== 200) throw Error('Pending request rejected');
let processed = 0;
for (const task of pending.data.data ?? []) {
  const key = [task.target, task.role, task.action].join(':');
  const handler = handlers.get(key);
  if (!handler) continue; // Unregistered tasks remain queued for their intended executor.
  const claim = await api('/v1/tasks/' + encodeURIComponent(task.task_id) + '/claim', 'POST');
  if (claim.status === 409) continue;
  try {
    await handler(task.payload);
    const result = await api('/v1/tasks/' + encodeURIComponent(task.task_id) + '/complete', 'POST');
    if (result.status !== 200) throw Error('Task completion rejected');
  } catch (error) {
    await api('/v1/tasks/' + encodeURIComponent(task.task_id) + '/fail', 'POST', {
      error: String(error?.message ?? error).slice(0, 1000),
    });
  }
  processed++;
}
console.log(JSON.stringify({ processed, registered_handlers: [...handlers.keys()] }));
