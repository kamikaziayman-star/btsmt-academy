create table if not exists student_accounts (
  email text primary key,
  payload jsonb not null,
  updated_at text not null
);

create table if not exists prof_accounts (
  email text primary key,
  payload jsonb not null,
  updated_at text not null
);

create table if not exists messages (
  id text primary key,
  kind text not null default 'public',
  payload jsonb not null,
  updated_at text not null
);

create table if not exists courses (
  id text primary key,
  subject text not null,
  payload jsonb not null,
  updated_at text not null
);

create table if not exists exams (
  id text primary key,
  payload jsonb not null,
  updated_at text not null
);

create table if not exists shared_files (
  id text primary key,
  payload jsonb not null,
  updated_at text not null
);

create table if not exists planning (
  id text primary key,
  payload jsonb not null,
  updated_at text not null
);

create table if not exists view_receipts (
  view_id text primary key,
  payload jsonb not null,
  updated_at text not null
);

create table if not exists support_tickets (
  id text primary key,
  payload jsonb not null,
  updated_at text not null
);

alter table student_accounts enable row level security;
alter table prof_accounts enable row level security;
alter table messages enable row level security;
alter table courses enable row level security;
alter table exams enable row level security;
alter table shared_files enable row level security;
alter table planning enable row level security;
alter table view_receipts enable row level security;
alter table support_tickets enable row level security;
