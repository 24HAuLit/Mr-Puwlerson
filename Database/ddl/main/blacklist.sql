create table blacklist
(
    blacklist_id integer not null
        primary key autoincrement,
    user_id      integer not null,
    reason       text
);

