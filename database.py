from json import load
from mysql.connector import connect as database_connect


class Cursor(object):
	def __init__(self, cursor):
		self.cursor = cursor 

	def __call__(self, function, *variables):
		self.cursor.execute(function, variables)

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
		with open(config_filename) as a:
			config = load(a)
		cls.config = config 
		cls.database = database_connect(**config)

	def __enter__(self):
		self.cursor = Cursor(DATABASE.cursor())
		return self.cursor

	def __exit__(self, exc_type, exc_val, exc_tb):
		DATABASE.commit()
		self.cursor.close()
		self.cursor = None




