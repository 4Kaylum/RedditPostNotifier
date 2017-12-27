DROP DATABASE IF EXISTS post_notifier;
CREATE DATABASE post_notifier;
USE post_notifier;


-- CREATE TABLE webhooks (
-- 	name VARCHAR(20),
-- 	webhook VARCHAR(500),
-- 	PRIMARY KEY (name),
-- );


CREATE TABLE users (
	username VARCHAR(20),
	subreddit VARCHAR(20),
	PRIMARY KEY (username, subreddit)
);

