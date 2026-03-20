import sqlite3
import os
import time

class MemorySystem:
    def __init__(self):
        # Path to memory database
        home = os.path.expanduser("~")
        self.memory_dir = os.path.join(os.environ.get('USERPROFILE', home), "AppData", "Local", "Omniagent", "Brain")
        if not os.path.exists(self.memory_dir):
            os.makedirs(self.memory_dir)
            
        self.db_path = os.path.join(self.memory_dir, "long_term_memory.db")
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            # Facts table: User facts, preferences, knowledge
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    date_str TEXT NOT NULL
                )
            ''')
            # Events table: System events, actions taken
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    date_str TEXT NOT NULL
                )
            ''')
            # Goals table: User goals tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    goal TEXT NOT NULL,
                    status TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    date_str TEXT NOT NULL
                )
            ''')
            # App Settings table: key-value store for GUI/Core config
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            ''')
            # Request logs for rate limiting
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS request_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL
                )
            ''')
            conn.commit()
        finally:
            conn.close()

    def set_setting(self, key, value):
        """Stores an application setting."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)',
                (key, str(value))
            )
            conn.commit()
        finally:
            conn.close()

    def get_setting(self, key, default=None):
        """Retrieves an application setting."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
            row = cursor.fetchone()
            if row:
                return row[0]
            return default
        finally:
            conn.close()

    def add_memory(self, topic, content):
        """Stores a fact or preference."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO facts (topic, content, timestamp, date_str) VALUES (?, ?, ?, ?)',
                (topic, content, time.time(), time.strftime("%Y-%m-%d %H:%M"))
            )
            conn.commit()
        finally:
            conn.close()
        return f"Memory stored under '{topic}': {content}"

    def get_all_memories(self):
        """Returns a formatted string of recent memories for prompt context."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            # Get the top 20 most recent facts
            cursor.execute('SELECT topic, content FROM facts ORDER BY timestamp DESC LIMIT 20')
            rows = cursor.fetchall()
            
            cursor.execute('SELECT goal, status FROM goals WHERE status != "completed" ORDER BY timestamp DESC LIMIT 5')
            goals = cursor.fetchall()
        finally:
            conn.close()

        if not rows and not goals:
            return "No long-term memories or active goals yet."
        
        lines = ["--- Long-Term Memory & Context ---"]
        if rows:
            lines.append("Known Facts:")
            for row in rows:
                lines.append(f"- [{row[0]}]: {row[1]}")
        if goals:
            lines.append("\nActive Goals:")
            for g in goals:
                lines.append(f"- {g[0]} (Status: {g[1]})")
        
        return "\n".join(lines)

    def search_memory(self, query):
        """Simple keyword search across facts."""
        query = f"%{query}%"
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT topic, content FROM facts WHERE topic LIKE ? OR content LIKE ? ORDER BY timestamp DESC LIMIT 10', (query, query))
            rows = cursor.fetchall()
        finally:
            conn.close()
        
        if not rows:
            return "No matching memories found."
            
        return "\n".join([f"[{r[0]}]: {r[1]}" for r in rows])

    def log_event(self, event_type, description):
        """Logs a system action or daily event."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO events (event_type, description, timestamp, date_str) VALUES (?, ?, ?, ?)',
                (event_type, description, time.time(), time.strftime("%Y-%m-%d %H:%M"))
            )
            conn.commit()
        finally:
            conn.close()

    def add_goal(self, goal_desc):
        """Adds a long-term goal."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO goals (goal, status, timestamp, date_str) VALUES (?, ?, ?, ?)',
                (goal_desc, "active", time.time(), time.strftime("%Y-%m-%d %H:%M"))
            )
            conn.commit()
        finally:
            conn.close()
        return f"Goal added: {goal_desc}"

    def log_request(self):
        """Logs a request timestamp for rate limiting."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO request_logs (timestamp) VALUES (?)', (time.time(),))
            conn.commit()
        finally:
            conn.close()

    def get_recent_request_count(self, seconds=3600):
        """Returns the number of requests in the last N seconds."""
        cutoff = time.time() - seconds
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM request_logs WHERE timestamp > ?', (cutoff,))
            count = cursor.fetchone()[0]
            # Clean up old logs while we're here
            cursor.execute('DELETE FROM request_logs WHERE timestamp <= ?', (cutoff - 86400,)) # Keep 1 day extra
            conn.commit()
            return count
        finally:
            conn.close()
