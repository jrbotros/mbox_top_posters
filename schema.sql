drop table if exists month;
drop table if exists semester;
drop table if exists year;
drop table if exists all_time;
create table month (
  id integer primary key autoincrement,
  name text not null,
  count integer not null
);
create table semester (
  id integer primary key autoincrement,
  name text not null,
  count integer not null
);
create table year (
  id integer primary key autoincrement,
  name text not null,
  count integer not null
);
create table all_time (
  id integer primary key autoincrement,
  name text not null,
  count integer not null
);
