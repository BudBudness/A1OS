import hashlib, sqlite3

class LedgerSecurity:
    @staticmethod
    def calculate_hash(data, prev_hash):
        return hashlib.sha256(f"{data}{prev_hash}".encode()).hexdigest()

    @staticmethod
    def get_last_hash():
        conn = sqlite3.connect("/data/data/com.termux/files/home/A1OS/audit.db")
        cursor = conn.execute("SELECT hash FROM tasks ORDER BY rowid DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else "0"
