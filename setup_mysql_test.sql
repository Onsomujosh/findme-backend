-- A script that prepares a MySQL server for the project
-- create testing database called : hbnb_test_db
CREATE DATABASE IF NOT EXISTS findme_test_db;
-- create new user called : hbnb_test with all privileges on the db hbnb_test_db
-- the password set to : hbnb_test_pwd if it dosen't exist
CREATE USER IF NOT EXISTS 'findme_test'@'localhost' IDENTIFIED BY 'findme_test_pwd';
-- SELECT privilege for the user hbnb_test on the db performance_schema
GRANT SELECT ON performance_schema.* TO 'findme_test'@'localhost';
FLUSH PRIVILEGES;
-- granting all privileges to the new user on hbnb_test_db
GRANT ALL PRIVILEGES ON findme_test_db.* TO 'findme_test'@'localhost';
FLUSH PRIVILEGES;
