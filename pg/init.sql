create table students (
    id serial primary key, 
    name text, 
    age integer, 
    is_male boolean);

create table products (
    id serial primary key, 
    name text, owner_id integer references students (id) on delete CASCADE, 
    detail jsonb);

create table cars (
    id serial primary key,
    name text,
    owner_id integer references students (id) on delete CASCADE
);

create table movies (
    id serial primary key,
    name text,
    casts text[],
    earning JSONB[]-- earning = [{country, amount}]
);

create table entries (
    id serial primary key,
    body text,
    updated timestamp
);
