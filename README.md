# LinkedIn Post Factory - Frontend

A modern Next.js application for generating, managing, and analyzing LinkedIn posts using AI.

## Features

- 🤖 **AI Post Generation**: Generate LinkedIn posts using OpenAI or Anthropic
- 📚 **Post Library**: Manage all your generated posts with filtering and search
- 📊 **Analytics Dashboard**: Track your content performance and strategy
- 🎯 **Content Pillars**: Organize posts by content pillars
- 📝 **Multiple Formats**: Support for various post formats (Story, Insight, How-To, etc.)
- ✅ **Workflow Management**: Track post status from raw to published

## Tech Stack

- **Framework**: Next.js 16 with React 19
- **Styling**: Tailwind CSS v4
- **UI Components**: Radix UI
- **Database**: Supabase
- **Charts**: Recharts
- **Icons**: Lucide React

## Getting Started

### Prerequisites

- Node.js 20+
- A Supabase account and project
- Backend API running (separate repository)

### Installation

1. Clone the repository:
```bash
cd post-app
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp .env.local.example .env.local
```

Edit `.env.local` and add your credentials:
- `NEXT_PUBLIC_SUPABASE_URL`: Your Supabase project URL
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`: Your Supabase anonymous key
- `NEXT_PUBLIC_API_URL`: Backend API URL (default: http://localhost:8000)

### Supabase Setup

Create the following table in your Supabase project:

```sql
-- Create posts table
create table posts (
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

-- Create engagement table (optional)
create table engagement (
  id serial primary key,
  post_id uuid references posts(id) on delete cascade,
  views integer default 0,
  likes integer default 0,
  comments integer default 0,
  shares integer default 0,
  engagement_rate numeric,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create indexes
create index posts_pillar_idx on posts(pillar);
create index posts_status_idx on posts(status);
create index posts_created_at_idx on posts(created_at desc);
```

### Development

Run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
post-app/
├── app/                    # Next.js app directory
│   ├── page.tsx           # Main dashboard page
│   ├── layout.tsx         # Root layout
│   └── globals.css        # Global styles
├── components/            # React components
│   ├── ui/               # Shadcn UI components
│   ├── post-generator.tsx # Post generation interface
│   ├── post-library.tsx   # Post management table
│   └── analytics.tsx      # Analytics dashboard
├── lib/                   # Utility libraries
│   ├── api.ts            # Backend API client
│   ├── supabase.ts       # Supabase client & services
│   └── utils.ts          # Helper functions
└── types/                 # TypeScript types
    └── database.ts       # Supabase database types
```

## Usage

### Generate Posts

1. Navigate to the **Generate** tab
2. Select a content pillar (e.g., "AI & Innovation")
3. Choose a post format (e.g., "Story", "How-To")
4. Optionally specify a topic
5. Click "Generate Post" or "Batch (10)" for multiple posts

### Manage Posts

1. Navigate to the **Library** tab
2. Search and filter posts by status
3. Edit post content by clicking the edit icon
4. Update post status using the dropdown
5. Delete posts you no longer need

### View Analytics

1. Navigate to the **Analytics** tab
2. View key metrics (total posts, published, scheduled, avg voice score)
3. Analyze distribution by content pillar and format
4. Review workflow status breakdown

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `NEXT_PUBLIC_SUPABASE_URL` | Your Supabase project URL | Yes |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Your Supabase anonymous key | Yes |
| `NEXT_PUBLIC_API_URL` | Backend API URL | Yes |

## API Integration

This frontend connects to a separate backend API that handles:
- AI post generation (OpenAI/Anthropic)
- Voice scoring
- Batch generation
- Post statistics

Ensure the backend is running before using the generation features.

## Building for Production

```bash
npm run build
npm start
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a pull request

## License

MIT

## Support

For issues and questions, please open an issue on GitHub.

