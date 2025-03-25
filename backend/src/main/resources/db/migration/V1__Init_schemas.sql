create table employees
(
    id       integer primary key not null,
    user_id  integer,
    emp_code varchar,
    name     varchar,
    office   varchar,
    location varchar
);

create table skills
(
    id         integer primary key not null,
    skill_id   varchar,
    skill_name varchar
);

create table proficiencies
(
    id   integer primary key not null,
    name varchar
);

create table employees_skills
(
    id             integer primary key not null,
    user_id        integer             not null,
    skill_id       integer             not null,
    proficiency_id integer             not null,
    is_primary     boolean             not null,
    note           varchar,
    constraint fk_employees_skills_on_users foreign key (user_id) references employees (id),
    constraint fk_employees_skills_on_skills foreign key (skill_id) references skills (id),
    constraint fk_employees_skills_on_proficiencies foreign key (proficiency_id) references proficiencies (id)
);

create table additional_skills
(
    id                    integer primary key not null,
    additional_skill_id   integer             not null,
    additional_skill_name varchar             not null
);

create table employees_additional_skills
(
    id                  integer primary key not null,
    user_id             integer             not null,
    additional_skill_id integer             not null,
    proficiency_id      integer             not null,
    note                varchar,
    constraint fk_employees_additional_skills_employees foreign key (user_id) references employees (id),
    constraint fk_employees_additional_skills_additional_skills foreign key (additional_skill_id) references additional_skills (id),
    constraint fk_employees_additional_skills_proficiencies foreign key (proficiency_id) references proficiencies (id)
);

create table business_domains
(
    id                   integer primary key not null,
    business_domain_id   integer             not null,
    business_domain_name varchar             not null
);

create table employees_business_domains
(
    id                 integer primary key not null,
    user_id            integer             not null,
    business_domain_id integer             not null,
    note               varchar             not null,
    constraint fk_employees_business_domains_employees foreign key (user_id) references employees (id),
    constraint fk_employees_business_domains_business_domains foreign key (business_domain_id) references business_domains (id)
);

--------------------------------------------Insider--------------------------------------------
create table work_plans
(
    id               integer primary key not null,
    project_id       integer             not null,
    project_type     integer             not null,
    project_model    integer             not null,
    employee_id      integer             not null,
    emp_code         varchar             not null,
    start_date       date,
    end_date         date,
    daily_hour       integer,
    created_emp_code varchar
);

CREATE TABLE log_times
(
    id                     integer PRIMARY KEY not null,
    user_id                integer             NOT NULL,
    emp_code               varchar             NOT NULL,
    full_name              varchar             NOT NULL,
    log_date               TIMESTAMPTZ         NOT NULL,
    creation_time          TIMESTAMPTZ,
    last_modification_time TIMESTAMPTZ,
    project_id             integer,
    project_name           varchar,
    pc_name                varchar,
    hours                  integer,
    hour_rate              integer,
    activity               varchar,
    comment                varchar,
    logged_by              varchar             NOT NULL
);
