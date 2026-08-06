-- Plataforma permanente del Diplomado en Acústica en la Edificación
-- Ejecutar una sola vez en Supabase > SQL Editor > New query.

create extension if not exists pgcrypto;

create table if not exists public.courses (
  id text primary key,
  title text not null,
  description text,
  active boolean not null default true,
  created_at timestamptz not null default now()
);

create table if not exists public.classes (
  id text primary key,
  course_id text not null references public.courses(id) on delete restrict,
  class_number integer not null,
  title text not null,
  description text,
  status text not null default 'published'
    check (status in ('draft','published','archived')),
  opens_at timestamptz,
  due_at timestamptz,
  content_version integer not null default 1,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(course_id,class_number)
);

create table if not exists public.users (
  user_key text primary key,
  role text not null check (role in ('Alumno','Docente')),
  display_name text not null,
  rut text,
  email text,
  created_at timestamptz not null default now(),
  last_login_at timestamptz not null default now()
);

create table if not exists public.enrollments (
  course_id text not null references public.courses(id) on delete cascade,
  user_key text not null references public.users(user_key) on delete cascade,
  active boolean not null default true,
  enrolled_at timestamptz not null default now(),
  primary key(course_id,user_key)
);

create table if not exists public.questions (
  id text primary key,
  class_id text not null references public.classes(id) on delete restrict,
  stage integer not null,
  question_key text not null,
  question_text text not null,
  correct_answer text,
  max_score numeric(8,2) not null default 0,
  content_version integer not null default 1,
  active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(class_id,question_key,content_version)
);

create table if not exists public.responses (
  id uuid primary key default gen_random_uuid(),
  course_id text not null references public.courses(id) on delete restrict,
  class_id text not null references public.classes(id) on delete restrict,
  user_key text not null references public.users(user_key) on delete restrict,
  stage integer not null,
  question_key text not null,
  question_text text not null,
  correct_answer text,
  answer jsonb not null default '{}'::jsonb,
  auto_level text,
  feedback text,
  auto_score numeric(8,2) not null default 0,
  max_score numeric(8,2) not null default 0,
  teacher_level text,
  teacher_score numeric(8,2),
  teacher_note text,
  status text not null default 'draft'
    check (status in ('draft','submitted','reviewed')),
  first_saved_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  submitted_at timestamptz,
  unique(class_id,user_key,question_key)
);

create table if not exists public.user_progress (
  course_id text not null references public.courses(id) on delete restrict,
  class_id text not null references public.classes(id) on delete restrict,
  user_key text not null references public.users(user_key) on delete cascade,
  role text not null,
  display_name text not null,
  state_json jsonb not null default '{}'::jsonb,
  progress_percent numeric(5,2) not null default 0,
  updated_at timestamptz not null default now(),
  primary key(class_id,user_key)
);

create table if not exists public.submissions (
  id uuid primary key default gen_random_uuid(),
  course_id text not null references public.courses(id) on delete restrict,
  class_id text not null references public.classes(id) on delete restrict,
  user_key text not null references public.users(user_key) on delete restrict,
  stage integer,
  score numeric(8,2),
  max_score numeric(8,2),
  status text not null default 'submitted',
  submitted_at timestamptz not null default now()
);

create table if not exists public.notebook_entries (
  id uuid primary key default gen_random_uuid(),
  course_id text not null references public.courses(id) on delete restrict,
  class_id text not null references public.classes(id) on delete restrict,
  user_key text not null references public.users(user_key) on delete cascade,
  question_key text,
  title text not null default 'Desarrollo',
  known_data text,
  unit_conversions text,
  selected_formula text,
  substitution text,
  result text,
  interpretation text,
  updated_at timestamptz not null default now()
);

create table if not exists public.projection_state (
  course_id text not null,
  class_id text not null,
  stage integer,
  question text,
  answer text,
  solution text,
  show_answer boolean not null default false,
  show_solution boolean not null default false,
  updated_at timestamptz not null default now(),
  primary key(course_id,class_id)
);

insert into public.courses(id,title,description)
values ('diplomado-acustica-edificacion','Diplomado en Acústica en la Edificación',
        'Plataforma permanente de clases, actividades y evaluaciones')
on conflict (id) do update set title=excluded.title, description=excluded.description;

insert into public.classes(id,course_id,class_number,title,description,status)
values ('clase-01-aislamiento-ruido-aereo','diplomado-acustica-edificacion',1,
        'Aislamiento a ruido aéreo','Laboratorio interactivo de 4 horas','published')
on conflict (id) do update set title=excluded.title, description=excluded.description;

insert into public.projection_state(course_id,class_id)
values ('diplomado-acustica-edificacion','clase-01-aislamiento-ruido-aereo')
on conflict (course_id,class_id) do nothing;

-- La aplicación usa la service_role key guardada únicamente en Streamlit Secrets.
-- Se bloquea el acceso directo mediante la anon key.
alter table public.courses enable row level security;
alter table public.classes enable row level security;
alter table public.users enable row level security;
alter table public.enrollments enable row level security;
alter table public.questions enable row level security;
alter table public.responses enable row level security;
alter table public.user_progress enable row level security;
alter table public.submissions enable row level security;
alter table public.notebook_entries enable row level security;
alter table public.projection_state enable row level security;
