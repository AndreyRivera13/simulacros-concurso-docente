-- Proyecto Supabase: simulacros-concurso-docente (ref ggcgbjonlxxcmegknfxi, región sa-east-1)
-- Migración aplicada: create_quiz_attempts (14-nov-2026). El sitio usa solo la clave PÚBLICA (publishable/anon).
create table public.quiz_attempts (
  id uuid primary key,                       -- generado en el navegador (crypto.randomUUID)
  owner_token uuid not null,                 -- secreto del navegador; NO es legible por anon; autoriza actualizar el intento
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  quiz_date date not null check (quiz_date between date '2026-11-01' and date '2027-12-31'),
  version text not null check (version in ('A','B')),
  person text not null,
  topic_scores jsonb not null check (jsonb_typeof(topic_scores) = 'array' and jsonb_array_length(topic_scores) between 1 and 5),
                                             -- [{id, title, correct, total, answered}]
  answered integer not null,
  total_correct integer not null,
  total_questions integer not null check (total_questions between 1 and 200),
  percentage numeric(5,2) not null,          -- recalculado en el servidor
  completed boolean not null default false,  -- recalculado en el servidor (answered = total_questions)
  constraint person_matches_version check ((version = 'A' and person = 'Yazmín') or (version = 'B' and person = 'Andrey')),
  constraint answered_range check (answered between 0 and total_questions),
  constraint correct_range check (total_correct between 0 and answered)
);
create index quiz_attempts_version_date_idx on public.quiz_attempts (version, quiz_date);

create or replace function public.quiz_attempts_guard() returns trigger language plpgsql set search_path = '' as $$
begin
  if tg_op = 'INSERT' then
    new.created_at := now();
  else
    if new.id <> old.id or new.owner_token <> old.owner_token or new.version <> old.version or new.person <> old.person or new.quiz_date <> old.quiz_date then
      raise exception 'immutable attempt fields cannot change';
    end if;
    if old.created_at < now() - interval '60 days' then
      raise exception 'attempt too old to update';
    end if;
    new.created_at := old.created_at;
  end if;
  new.updated_at := now();
  new.completed := new.answered = new.total_questions;
  new.percentage := round(new.total_correct * 100.0 / new.total_questions, 2);
  return new;
end $$;
create trigger quiz_attempts_guard before insert or update on public.quiz_attempts for each row execute function public.quiz_attempts_guard();

alter table public.quiz_attempts enable row level security;
revoke all on table public.quiz_attempts from anon, authenticated;   -- sin DELETE
grant select (id, created_at, updated_at, quiz_date, version, person, topic_scores, answered, total_correct, total_questions, percentage, completed) on public.quiz_attempts to anon, authenticated;
grant insert (id, owner_token, quiz_date, version, person, topic_scores, answered, total_correct, total_questions, percentage, completed) on public.quiz_attempts to anon, authenticated;
grant update (id, owner_token, quiz_date, version, person, topic_scores, answered, total_correct, total_questions, percentage, completed) on public.quiz_attempts to anon, authenticated;

create policy "public can read attempts" on public.quiz_attempts for select to anon, authenticated using (true);
create policy "anyone can create an attempt" on public.quiz_attempts for insert to anon, authenticated with check (true);
create policy "owner token can update its attempt" on public.quiz_attempts for update to anon, authenticated
  using (owner_token::text = coalesce((current_setting('request.headers', true)::json ->> 'x-owner-token'), ''))
  with check (owner_token::text = coalesce((current_setting('request.headers', true)::json ->> 'x-owner-token'), ''));

-- Limpiar filas de prueba E2E (las imprime tests/e2e.py como TEST_ATTEMPT_IDS):
-- delete from public.quiz_attempts where id in ('<id1>','<id2>', ...);
