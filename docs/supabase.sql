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

-- The app performs its own PIN login, so Supabase sees every request as anon.
alter table public.annotations enable row level security;

grant select, insert, update on table public.annotations to anon, authenticated;

drop policy if exists "Allow annotation reads" on public.annotations;
create policy "Allow annotation reads"
on public.annotations for select
to anon, authenticated
using (true);

drop policy if exists "Allow annotation inserts" on public.annotations;
create policy "Allow annotation inserts"
on public.annotations for insert
to anon, authenticated
with check (true);

drop policy if exists "Allow annotation updates" on public.annotations;
create policy "Allow annotation updates"
on public.annotations for update
to anon, authenticated
using (true)
with check (true);
