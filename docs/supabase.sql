create table if not exists public.annotations (
    item_id integer not null,
    annotator_id text not null,
    correctness integer not null check (correctness between 0 and 2),
    completeness integer not null check (completeness between 0 and 2),
    policy_compliance integer not null check (policy_compliance between 0 and 2),
    politeness integer not null check (politeness between 0 and 2),
    clarity integer not null check (clarity between 0 and 2),
    total_score integer not null check (total_score between 0 and 10),
    reason text,
    updated_at timestamptz not null default now(),
    primary key (item_id, annotator_id)
);

-- For a class project, the simplest setup is to use the anon key.
-- Review your Row Level Security configuration before sharing publicly.
