PRAGMA foreign_keys=OFF;
CREATE TABLE users_clean (id TEXT PRIMARY KEY, rapnss_id TEXT, email TEXT, username TEXT, handle TEXT, full_name TEXT, avatar_url TEXT, provider TEXT DEFAULT 'rapnss', verified INTEGER DEFAULT 1, created_at DATETIME DEFAULT CURRENT_TIMESTAMP);
INSERT INTO users_clean (id, rapnss_id, email, username, handle, full_name, verified, created_at) SELECT id, NULL, email, username, handle, full_name, 1, created_at FROM users;
DROP TABLE users;
ALTER TABLE users_clean RENAME TO users;
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_rapnss_id ON users(rapnss_id) WHERE rapnss_id IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users(email) WHERE email IS NOT NULL;
PRAGMA foreign_keys=ON;
