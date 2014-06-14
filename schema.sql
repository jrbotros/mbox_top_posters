drop table if exists posters;
create table posters (
  id integer primary key autoincrement,
  name text not null,
  count integer not null
);