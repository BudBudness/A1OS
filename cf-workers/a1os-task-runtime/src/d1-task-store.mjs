
export const sql = {
  enqueue: `INSERT INTO a1os_tasks
    (task_id, target, role, action, payload, created_at, updated_at)
    VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?6)`,
  get: `SELECT task_id, target, role, action, payload, status, attempts,
    max_attempts, error, next_attempt_at, created_at, updated_at, completed_at
    FROM a1os_tasks WHERE task_id = ?1`,
  claim: `UPDATE a1os_tasks
    SET status = 'running', attempts = attempts + 1, updated_at = ?1,
        lease_token = ?2, lease_expires_at = ?3
    WHERE task_id = (
      SELECT task_id FROM a1os_tasks
      WHERE status IN ('queued', 'retry') AND attempts < max_attempts
        AND (next_attempt_at IS NULL OR next_attempt_at <= ?1)
      ORDER BY created_at, task_id LIMIT 1
    )
    RETURNING task_id, target, role, action, payload, lease_token`,
  complete: `UPDATE a1os_tasks
    SET status = 'completed', completed_at = ?3, updated_at = ?3,
        error = NULL, next_attempt_at = NULL, lease_token = NULL, lease_expires_at = NULL
    WHERE task_id = ?1 AND lease_token = ?2 AND status = 'running'
      AND lease_expires_at > ?3
    RETURNING task_id`,
  fail: `UPDATE a1os_tasks
    SET status = CASE WHEN ?5 OR attempts >= max_attempts THEN 'failed' ELSE 'retry' END,
        next_attempt_at = CASE WHEN ?5 OR attempts >= max_attempts THEN NULL
          ELSE strftime('%Y-%m-%dT%H:%M:%fZ', ?3,
                        printf('+%d seconds', 1 << min(attempts, 20))) END,
        updated_at = ?3, error = ?4, lease_token = NULL, lease_expires_at = NULL
    WHERE task_id = ?1 AND lease_token = ?2 AND status = 'running'
      AND lease_expires_at > ?3
    RETURNING task_id`,
  recover: `UPDATE a1os_tasks
    SET status = CASE WHEN attempts >= max_attempts THEN 'failed' ELSE 'retry' END,
        next_attempt_at = CASE WHEN attempts >= max_attempts THEN NULL ELSE ?1 END,
        updated_at = ?1, error = 'Worker lease expired',
        lease_token = NULL, lease_expires_at = NULL
    WHERE status = 'running' AND lease_expires_at <= ?1`,
};

export class D1TaskStore {
  constructor(db) {
    this.db = db;
  }

  async enqueue({ target, role, action, data }, taskId = crypto.randomUUID()) {
    await this.db.prepare(sql.enqueue)
      .bind(taskId, target, role, action, JSON.stringify(data ?? {}), new Date().toISOString())
      .run();
    return taskId;
  }

  async getTask(taskId) {
    const row = await this.db.prepare(sql.get).bind(taskId).first();
    if (row) row.payload = JSON.parse(row.payload);
    return row;
  }

  async claimNext() {
    const now = new Date();
    const expires = new Date(now.getTime() + 300_000);
    const row = await this.db.prepare(sql.claim)
      .bind(now.toISOString(), crypto.randomUUID(), expires.toISOString()).first();
    if (row) row.payload = JSON.parse(row.payload);
    return row;
  }

  async complete(taskId, leaseToken) {
    return Boolean(await this.db.prepare(sql.complete)
      .bind(taskId, leaseToken, new Date().toISOString()).first());
  }

  async fail(taskId, leaseToken, error) {
    const message = String(error).replace(/[\r\n]/g, " ").slice(0, 1000);
    return Boolean(await this.db.prepare(sql.fail)
      .bind(taskId, leaseToken, new Date().toISOString(), message,
            Number(message.startsWith("ApprovalDenied:"))).first());
  }

  async recoverExpired() {
    const result = await this.db.prepare(sql.recover).bind(new Date().toISOString()).run();
    return result.meta.changes;
  }
}
