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

/* For PostgreSQL */
CREATE DATABASE rover;

/* Re-connect to the new DB fist! */
DROP TABLE IF EXISTS event CASCADE;
CREATE TABLE event (
    "id" BIGSERIAL PRIMARY KEY,
    "message" VARCHAR(128) NOT NULL,
    "severity" SMALLINT NOT NULL,
    "type" SMALLINT NOT NULL, 
    "time" TIMESTAMP
);

SELECT * FROM event;
SELECT * FROM `event`;
