import sqlite3
def get_system_metrics():
    conn = sqlite3.connect('data/audit.db')
    cursor = conn.cursor()
    cursor.execute("SELECT state, COUNT(*) FROM tasks GROUP BY state")
    metrics = cursor.fetchall()
    conn.close()
    return metrics
print(get_system_metrics())
