create table ticket
(
    ticket_id  INTEGER not null
        primary key autoincrement,
    author_id  INTEGER not null,
    staff_id   INTEGER not null,
    channel_id integer
);

