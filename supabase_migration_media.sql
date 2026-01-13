-- Migration: Add media support to posts table
-- Run this in Supabase SQL Editor

-- Add media columns to posts table
ALTER TABLE posts 
ADD COLUMN IF NOT EXISTS media_urls TEXT[] DEFAULT NULL,
ADD COLUMN IF NOT EXISTS media_type TEXT CHECK (media_type IN ('code', 'chart', 'ai-image', 'infographic', 'carousel', 'demo')) DEFAULT NULL,
ADD COLUMN IF NOT EXISTS demo_url TEXT DEFAULT NULL;

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_posts_media_type ON posts(media_type);

-- Update RLS policies to allow media access
-- (Existing policies should already cover this, but verify)

COMMENT ON COLUMN posts.media_urls IS 'Array of Supabase Storage URLs for post media assets';
COMMENT ON COLUMN posts.media_type IS 'Primary type of media associated with this post';
COMMENT ON COLUMN posts.demo_url IS 'URL to interactive demo page for this post';
