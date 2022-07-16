CREATE TABLE area
(
    id   integer PRIMARY KEY AUTOINCREMENT,
    name varchar(255) NOT NULL
);

CREATE TABLE area_parent_area
(
    id             integer PRIMARY KEY AUTOINCREMENT,
    area_id        integer NOT NULL,
    parent_area_id integer NOT NULL,
    CONSTRAINT FK_area_id FOREIGN KEY (area_id) REFERENCES area (id),
    CONSTRAINT FK_parent_area_id FOREIGN KEY (parent_area_id) REFERENCES area (id)
);

CREATE TABLE vacancy
(
    id      integer PRIMARY KEY AUTOINCREMENT,
    area_id integer NOT NULL,
    CONSTRAINT FK_vacancy_area FOREIGN KEY (area_id) REFERENCES area (id)
);

CREATE TABLE skill
(
    id   integer PRIMARY KEY AUTOINCREMENT,
    name varchar(255) NOT NULL
);

CREATE TABLE vacancy_skills
(
    id         integer PRIMARY KEY AUTOINCREMENT,
    vacancy_id integer NOT NULL,
    skill_id   integer NOT NULL,
    CONSTRAINT FK_vacancy_skills_skill FOREIGN KEY (skill_id) REFERENCES skill (id),
    CONSTRAINT FK_vacancy_skills_vacancy FOREIGN KEY (vacancy_id) REFERENCES vacancy (id)
);