DROP DATABASE IF EXISTS post_notifier;
CREATE DATABASE post_notifier;
USE post_notifier;


CREATE TABLE users (
	username VARCHAR(20),
	subreddit VARCHAR(20),
	PRIMARY KEY (username, subreddit)
);

