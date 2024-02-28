CREATE TABLE players (id BIGSERIAL PRIMARY KEY, name VARCHAR, url VARCHAR);

CREATE TABLE games (id BIGSERIAL PRIMARY KEY, start TIMESTAMP, finish TIMESTAMP, player_1 INTEGER, player_2 INTEGER, player_3 INTEGER, player_4 INTEGER, points_1 INTEGER, points_2 INTEGER, points_3 INTEGER, points_4 INTEGER, position_1 INTEGER, position_2 INTEGER, position_3 INTEGER, position_4 INTEGER);

CREATE TABLE passing (id BIGSERIAL PRIMARY KEY, dealt CHAR(26), direction INTEGER, passed CHAR(6), points INTEGER);
CREATE INDEX passing_idx ON passing (dealt,direction);

CREATE TABLE hands (id BIGSERIAL PRIMARY KEY, playing CHAR(26), turns CHAR(142), points INTEGER);
CREATE UNIQUE INDEX hands_idx ON hands (playing,turns);
