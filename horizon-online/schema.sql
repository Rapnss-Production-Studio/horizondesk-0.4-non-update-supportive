-- Users table — Pure OAuth-first (No passwords, no profile pics stored)
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    rapnss_id TEXT UNIQUE,          -- Rapnss OAuth user ID (primary lookup key)
    email TEXT UNIQUE,              -- May be null if Rapnss doesn't expose it
    username TEXT,                  -- Display name
    handle TEXT,                    -- @handle / slug
    full_name TEXT,
    provider TEXT DEFAULT 'rapnss', -- Always 'rapnss'
    verified INTEGER DEFAULT 1,     -- OAuth users are always verified
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Developers Table (linked to users via Rapnss OAuth)
CREATE TABLE IF NOT EXISTS developers (
    id TEXT PRIMARY KEY,
    user_id TEXT UNIQUE,
    agreed_to_terms INTEGER DEFAULT 0,
    free_releases_left INTEGER DEFAULT 1,
    ad_balance REAL DEFAULT 10.00,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Plugins Table
CREATE TABLE IF NOT EXISTS plugins (
    id TEXT PRIMARY KEY,
    developer_id TEXT,
    name TEXT,
    description TEXT,
    version TEXT,
    category TEXT DEFAULT 'general',
    icon_url TEXT,
    tigris_url TEXT,
    status TEXT DEFAULT 'pending_review',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
