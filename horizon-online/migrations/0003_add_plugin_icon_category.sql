-- Add icon_url and category to plugins
ALTER TABLE plugins ADD COLUMN icon_url TEXT;
ALTER TABLE plugins ADD COLUMN category TEXT DEFAULT 'general';
