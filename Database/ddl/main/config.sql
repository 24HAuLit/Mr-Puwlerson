create table config
(
    server_id           integer               not null,
    logs_server         integer               not null,
    locale              TEXT    default EN_US not null,
    suggestion_cooldown integer,
    auto_role           integer default 0,
    ticket_parent       integer,
    ticket_count        integer,
    staff_role          integer,
    default_role        integer,
    owner_role          integer,
    admin_role          integer
);

