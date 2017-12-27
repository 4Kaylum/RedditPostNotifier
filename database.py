from json import load
from mysql.connector import connect as database_connect


class Cursor(object):

	def __init__(self, cursor):
		self.cursor = cursor 


	def __call__(self, function, *variables):
		self.cursor.execute(function, variables)
		return [i for i in self.cursor]


	def close(self):
		self.cursor.close()
		del self


class Database(object):

	CONFIG = None
	DATABASE = None


	def __init__(self):
		self.cursor = None


	@classmethod
	def setup(cls, config_filename:str):
		'''
		Sets up the database connection using a configuration file.

		Parameters:
			config_filename: str
				The (path to a) filename containing the database config.
		'''

		with open(config_filename) as a:
			config = load(a)
		cls.CONFIG = config 
		cls.DATABASE = database_connect(**config)
		return cls


	@classmethod
	def close(cls):
		'''
		Closes the database connection established in the setup method.
		'''

		cls.DATABASE.close()


	def __enter__(self):
		self.cursor = Cursor(self.__class__.DATABASE.cursor())
		return self.cursor


	def __exit__(self, exc_type, exc_val, exc_tb):
		self.__class__.DATABASE.commit()
		self.cursor.close()
		self.cursor = None


	def get_subreddit(self, subreddit:str):
		'''
		Gets a subreddit's users and webhook from the database

		Parameters:
			subreddit: str
				The name of the subreddit you want to get the information of

		Returns:
			dict
				A dictionary of the subreddit's users and webhook
		'''

		# Query the database
		with self as db:
			usernames = db('SELECT username FROM users WHERE subreddit=%s', subreddit)
			webhook = db('SELECT webhook FROM webhooks WHERE subreddit=%s', subreddit)

		# Sort into usable formats
		username_list = []
		for username in usernames:
			username_list.append(username)
		webhook_url = None
		for link in webhook:
			webhook_url = link

		# Return to user
		return {
			'Users': username_list,
			'Discord Webhook': webhook_url
		}
