-- Add the 3 new OAuth columns (simple ADD COLUMN — no table rebuild needed)
-- The old password_hash / password columns stay but are never written by OAuth
ALTER TABLE users ADD COLUMN rapnss_id TEXT;
ALTER TABLE users ADD COLUMN avatar_url TEXT;
ALTER TABLE users ADD COLUMN provider TEXT DEFAULT 'rapnss';

-- Unique index so we can look up by rapnss_id fast
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_rapnss_id ON users(rapnss_id) WHERE rapnss_id IS NOT NULL;
