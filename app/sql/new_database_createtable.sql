CREATE TABLE level ( 
    levelid   INT  NOT NULL,
    levelname TEXT NOT NULL,
    leveldesc TEXT NOT NULL,
    PRIMARY KEY ( levelid ) 
);

CREATE TABLE levelsection ( 
    levelid           INT     NOT NULL,
    levelsectionid    INT     NOT NULL,
    levelsectionname  TEXT    NOT NULL,
    levelsectionimage VARCHAR,
    PRIMARY KEY ( levelsectionid ),
    FOREIGN KEY ( levelid ) REFERENCES levelsection ( levelid ) 
);

CREATE TABLE quizquestions ( 
    quizid        INT     REFERENCES quizs ( quizid ),
    questionid    INTEGER PRIMARY KEY AUTOINCREMENT,
    question      VARCHAR NOT NULL,
    optiona       VARCHAR,
    optionb       VARCHAR,
    optionc       VARCHAR,
    optiond       VARCHAR,
    correctanswer CHAR 
);

CREATE TABLE quizresults ( 
    resultid INTEGER  PRIMARY KEY AUTOINCREMENT,
    quizid   INT      REFERENCES quizs ( quizid ) MATCH FULL,
    userid   INT      REFERENCES users ( userid ) MATCH FULL,
    mark     INT,
    date     DATETIME 
);

CREATE TABLE quizs ( 
    quizid   INT     PRIMARY KEY,
    quizname VARCHAR 
);

CREATE TABLE topics ( 
    levelsectionid INT     REFERENCES levelsection ( levelsectionid ) MATCH FULL,
    topicid        INTEGER PRIMARY KEY AUTOINCREMENT,
    topicname      TEXT,
    topicpage      TEXT 
);

CREATE TABLE users ( 
    userid      INTEGER  PRIMARY KEY AUTOINCREMENT
                         NOT NULL,
    username    VARCHAR  NOT NULL
                         UNIQUE,
    password    VARCHAR  NOT NULL,
    datecreated DATETIME NOT NULL,
    lastlogin   DATETIME,
    email       VARCHAR 
);

