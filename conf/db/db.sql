create table alembic_version
(
    version_num varchar(32) not null
        primary key
);

create table users
(
    id       int auto_increment
        primary key,
    name     varchar(250) not null,
    email    varchar(250) not null,
    password varchar(100) not null,
    constraint email
        unique (email)
);

create table auctions
(
    id            int auto_increment
        primary key,
    name          varchar(100) not null,
    description   varchar(250) not null,
    first_cost    float        not null,
    step_cost     float        not null,
    start_auction datetime     not null,
    end_auction   datetime     not null,
    is_active     tinyint(1)   null,
    owner_id      int          null,
    constraint auctions_ibfk_1
        foreign key (owner_id) references users (id)
);

create index owner_id
    on auctions (owner_id);

create table bets
(
    id         int auto_increment
        primary key,
    user_id    int   null,
    auction_id int   null,
    cost       float not null,
    constraint bets_ibfk_1
        foreign key (auction_id) references auctions (id),
    constraint bets_ibfk_2
        foreign key (user_id) references users (id)
);

create index auction_id
    on bets (auction_id);

create index user_id
    on bets (user_id);