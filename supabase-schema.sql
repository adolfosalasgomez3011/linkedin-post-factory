-- LinkedIn Post Factory - Supabase Database Schema
-- Run this in your Supabase SQL Editor

-- Create posts table
create table if not exists posts (
  id uuid default gen_random_uuid() primary key,
  pillar text not null,
  format text not null,
  topic text,
  text text not null,
  hashtags text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  status text default 'raw'::text not null check (status in ('raw', 'review', 'approved', 'scheduled', 'posted')),
  voice_score numeric,
  length integer
);

-- Create engagement table (for future analytics)
create table if not exists engagement (
  id serial primary key,
  post_id uuid references posts(id) on delete cascade,
  views integer default 0,
  likes integer default 0,
  comments integer default 0,
  shares integer default 0,
  engagement_rate numeric,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create indexes for better query performance
create index if not exists posts_pillar_idx on posts(pillar);
create index if not exists posts_status_idx on posts(status);
create index if not exists posts_created_at_idx on posts(created_at desc);
create index if not exists posts_format_idx on posts(format);
create index if not exists engagement_post_id_idx on engagement(post_id);

-- Enable Row Level Security (RLS)
alter table posts enable row level security;
alter table engagement enable row level security;

-- Create policies (for now, allow all operations - adjust based on your auth requirements)
create policy "Enable all operations for all users" on posts
  for all using (true) with check (true);

create policy "Enable all operations for all users" on engagement
  for all using (true) with check (true);

-- Create a function to update engagement metrics
create or replace function update_engagement_metrics()
returns trigger as $$
begin
  new.engagement_rate = (new.likes + new.comments * 2 + new.shares * 3)::numeric / nullif(new.views, 0) * 100;
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

-- Create trigger to auto-calculate engagement rate
create trigger calculate_engagement_rate
  before insert or update on engagement
  for each row
  execute function update_engagement_metrics();

-- Insert some sample data (optional - for testing)
-- insert into posts (pillar, format, topic, text, status, voice_score, length) values
--   ('AI & Innovation', 'Story', 'AI in Healthcare', 'Last week, I witnessed something remarkable...', 'raw', 8.5, 250),
--   ('Tech Leadership', 'Insight', 'Team Management', 'Great leaders dont create followers, they create more leaders.', 'review', 9.0, 180),
--   ('Career Growth', 'How-To', 'Skill Development', 'Here are 5 steps to accelerate your career growth...', 'approved', 8.8, 320);

-- Query to verify setup
select 'Setup complete!' as status, count(*) as post_count from posts;
