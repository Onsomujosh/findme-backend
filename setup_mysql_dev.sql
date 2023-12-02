-- A script that prepares a MySQL server for the project
-- create project developement database with the name : hbnb_dev_db
CREATE DATABASE IF NOT EXISTS findme;
-- creating new user named : hbnb_dev with all privileges on the database
-- with the password : hbnb_dev_pwd if it dosen't exist
CREATE USER IF NOT EXISTS 'findme'@'localhost' IDENTIFIED BY 'findme';
-- granting all privileges to the new user
GRANT ALL PRIVILEGES ON findme.* TO 'findme'@'localhost';
FLUSH PRIVILEGES;
-- SELECT privilege for the user hbnb_dev in the db performance_schema
GRANT SELECT ON performance_schema.* TO 'findme'@'localhost';
FLUSH PRIVILEGES;
