

CREATE TABLE score ( 
team_name varchar(100) NOT NULL,
task_type varchar(50)
NOT NULL,
cost integer NOT NULL,
date DATETIME);
INSERT INTO "score" VALUES('MSU','web',100,'2014-05-11 15:45:09');
COMMIT;
