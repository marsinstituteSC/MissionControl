/* Creates the Rover DB */

/* For MySQL */

DROP DATABASE IF EXISTS rover;
CREATE DATABASE rover;
USE rover;

CREATE TABLE `event` (
    `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
    `message` VARCHAR(128) NOT NULL,
    `severity` TINYINT UNSIGNED NOT NULL,
    `type` TINYINT UNSIGNED NOT NULL, 
    `time` TIMESTAMP
);

SELECT * FROM `event`;

/* For PostgreSQL */
CREATE DATABASE rover;

/* Re-connect to the new DB fist! */
DROP SCHEMA IF EXISTS sensor CASCADE;
CREATE SCHEMA sensor;

CREATE TABLE sensor.event (
    "id" BIGSERIAL PRIMARY KEY,
    "message" VARCHAR(128) NOT NULL,
    "severity" SMALLINT NOT NULL,
    "type" SMALLINT NOT NULL, 
    "time" TIMESTAMP
);

/* TEST DATA */

/*
INSERT INTO sensor.event (message, severity, type, time) VALUES ('speed - 0', '0', '0', '2019-02-05 00:30:06.109770');
select * from sensor.event;
*/