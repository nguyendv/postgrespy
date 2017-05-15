create table students (
    id serial primary key, 
    name text, 
    age integer, 
    is_male boolean);

create table products (
    id serial primary key, 
    name text, owner_id integer references students (id) on delete CASCADE, 
    detail jsonb);
