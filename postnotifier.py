from json import loads, dumps
from os import remove
from time import sleep
from requests import post
import praw
from responses import*
from database import Database

class PostNotifier:
	'''
	Handles the whole postnotifier thingimawatsit
	'''

	def __init__(self, reddit:praw.Reddit, database_config_filename:str):
		'''
		The input args for this are the praw reddit feature.

		Parameters :: 
			reddit : praw.Reddit
				The Praw reddit object used to send messages
			database_config_filename : str
				The filename for the file which stores the information of the database
		'''

		self.reddit = reddit
		Database.setup(database_config_filename)
		self.database = Database()
		self.owner_names = ['SatanistSnowflake']
		self.iteration = 0
		self.user_doesnt_exist = praw.exceptions.APIException

				
		# Set up which actions can be run
		self.run_actions = {
			'ADD':     self.add_to_mailing_list,
			'REMOVE':  self.remove_from_mailing_list,
			'DELETE':  self.remove_from_mailing_list,
			'DEL':     self.remove_from_mailing_list,
			'REM':     self.remove_from_mailing_list,
			'SEND':    self.send_to_mailing_list,
			'COMMENT': self.post_a_comment,
			# 'DISCORD': self.set_webhook_for_subreddit,
			# 'WEBHOOK': self.set_webhook_for_subreddit
		}


	def run(self, *, delay:int=30, timeout_delay:int=120):
		'''
		Call this to run all the featres of the bot on a loop

		Parameters :: 
			delay : int = 30
				The delay at which all of the bot features will be run
			timeout_delay : int = 120
				The sleeping time for when the bot recieves a connection error from the server
		'''

		# Start a loop so you'll run forever
		while True:

			self.iteration += 1
			this_delay = delay

			# Put in a try so you can catch timeouts
			try:

				# Check the inbox
				print('{:X} Checking inbox...'.format(self.iteration))
				self.check_inbox()

				# Sleep
				print('Sleeping for {}'.format(delay))

			# Catch timeouts
			except Exception as e:

				# Just sleep for longer I guess
				print('Sleeping for {} due to timeout'.format(timeout_delay))
				print('\t{}'.format(e))
				self.database.close()
				raise e
				this_delay = delay

			# [DERREN BROWN VOICE] Annnndddddd... sleep
			try:
				sleep(this_delay)
			except KeyboardInterrupt as e:
				print('Shutting down...')
				self.database.close()
				return


	def check_inbox(self):
		'''
		Checks the inbox of the user logged in and refers each post to a
		respective handling function.
		'''

		# Get the messages into a list
		inbox_messages = self.reddit.inbox.unread(mark_read=True)
		inbox_list = [i for i in inbox_messages if type(i) == praw.models.Message]  # Filter out mentions

		# Iterate through all of the messages
		for msg in inbox_list:

			# Print out to console
			print('New message ->\n\tAuthor :: {0.author}\n\tSubject :: {0.subject}'.format(msg))

			# Check that the message is in a valid format
			# post::askreddit asda -> [post, askredditasda]
			action_for_subreddit = msg.subject.replace(' ','').upper().split('::') 

			# len==1 means that there was no "::"
			# '' in action means that there was no command or no subreddit
			if len(action_for_subreddit) == 1 or '' in action_for_subreddit:

				# The message doesn't contain an action
				print('\tInvalid action :: Replying to user and aborting thread\n')
				try: msg.reply(INVALIDMESSAGETOBOT)
				except self.user_doesnt_exist as e: pass

			else:

				# Try and run an action on the given message
				try:

					# Split the sub name from the rest of the subject...
					# post::askreddit asda -> [askreddit, asda]
					sub_list = msg.subject.split('::', 1)[1].strip().split(' ')
					sub_list = [i for i in sub_list if i]  # Filter out blank elements
					subreddit = sub_list[0]

					# Run the action
					self.run_actions[action_for_subreddit[0]](subreddit.upper(), msg)
					
				except KeyError:

					# If you get here, the user tried to do something that the bot wasn't set up for
					# Thus, tell them the response was invalid
					print('\tInvalid action :: Replying to user and aborting thread')
					try:
						msg.reply(INVALIDMESSAGETOBOT)
					except self.user_doesnt_exist as e:
						pass

			print('\tMarking as read\n')
			msg.mark_read()


	def add_to_mailing_list(self, subreddit:str, msg:praw.models.Message):
		'''
		Adds a user to a mailing list for any given subreddit
		This shouldn't require authentication nor checking if a subreddit exists, so that's nice

		Messages should be sent with a subject of 'ADD::SUBREDDIT', and the body text is disregarded

		Parameters :: 
			subreddit : str
				The name for the subreddit that is going to be worked on for this user
			msg : praw.models.Message
				The original message that was sent by the user
		'''

		print('\tValid action -> \n\t\tAdding user to mailing list of {}'.format(subreddit))

		# Add the user to the database
		print('\t\tQuerying database')
		with self.database as db:
			result = db('SELECT * FROM users WHERE subreddit=%s AND username=%s', subreddit, msg.author.name)
			if result:
				print('\t\tUser already signed up - passing')
			else:
				db('INSERT INTO users (subreddit, username) VALUES (%s, %s)', subreddit, msg.author.name)

		# Respond to user
		print('\t\tResponding to user')
		try:
			msg.reply(ADDEDTOMAILINGLIST.format(subreddit))
		except self.user_doesnt_exist as e:
			pass


	def remove_from_mailing_list(self, subreddit:str, msg:praw.models.Message):
		'''
		Removes a user to a mailing list for any given subreddit
		This should check if the file is there so it doesn't run into any errors
		It should also delete the file if that file becomes empty

		Messages should be sent with a subject of 'REMOVE::SUBREDDIT', and the body text is disregarded

		Parameters :: 
			subreddit : str
				The name for the subreddit that is going to be worked on for this user
			msg : praw.models.Message
				The original message that was sent by the user
		'''

		print('\tValid action -> \n\t\tRemoving user from mailing list of {}'.format(subreddit))

		with self.database as db:
			results = db('SELECT * FROM users WHERE subreddit=%s AND username=%s', subreddit, msg.author.name)
			if results:
				db('DELETE FROM users WHERE subreddit=%s AND username=%s)', subreddit, msg.author.name)
			else:
				print('\t\tUser not signed up - passing')

		# Respond to user
		print('\t\tResponding to user')
		try:
			msg.reply(REMOVEDFROMMAILINGLIST.format(subreddit))
		except self.user_doesnt_exist as e:
			pass


	def send_to_mailing_list(self, subreddit:str, msg:praw.models.Message):
		'''
		This is the first command that requires authentication
		The bot will check if the message was sent by a moderator of the mentioned subreddit, 
		and if it was it will continue on to send out a message to everyone who signed up to
		do so

		Messages should be sent with a subject of 'SEND::SUBREDDIT SUBJECT', and the body text is
		sent by the bot with the message. The subject line can be varying in case

		Parameters :: 
			subreddit : str
				The name for the subreddit that is going to be worked on for this user
			msg : praw.models.Message
				The original message that was sent by the user
		'''

		print('\tValid action -> \n\t\tSending out messages to people signed up for {}'.format(subreddit))
		author = msg.author

		# Get the server moderators
		print('\t\tGenerating list of moderators for the subreddit')
		moderator_names = self.get_moderators(subreddit)

		# See if the user is in the moderator list
		if author not in moderator_names:

			# They are not a moderator
			print('\t\tUser not a moderator - responding and aborting')
			try:
				msg.reply(NOTALLOWEDTOSEND.format(subreddit))
			except self.user_doesnt_exist as e:
				pass
			return

		# They are a moderator - tell the user that the messages will be sent out now
		print('\t\tUser is a moderator - responding')
		msg.reply(ABOUTTOBESENT.format(subreddit))

		# Get the users to send the message to
		data = self.database.get_subreddit(subreddit)

		# Make sure that the message author is in them
		if author not in data['Users']:
			print('\t\tAdding author to user list')
			data['Users'] = [author] + data['Users']
			with self.database as db:
				db('INSERT INTO users (subreddit, username) VALUES (%s, %s)', subreddit, author.name)

		# Get the format ready for the messages - get subject
		subject_message = msg.subject.split('::', 1)[1].strip().split(' ')[1:]
		if subject_message:
			subject = 'Update from {} :: {}'.format(subreddit.upper(), subject_message)
		else:
			subject = 'Update from {}'.format(subreddit.upper())

		# Get body text
		body = msg.body + BOTDISCLAIMERMESSAGE + ' ^^:: ^^[Messenger](/u/{})'.format(author)

		# Setup some coutners
		counter = {'Success':0, 'Deleted User':0, 'Tries':0}
		users_to_remove = []

		# Send out the messages
		print('\t\tSending out to users now ->')
		for person in data['Users']:
			counter['Tries'] += 1
			print('\t\t\t:: {}'.format(person))
			try:
				reddit_user = self.reddit.redditor(person)
				reddit_user.message(subject, body)
				counter['Success'] += 1
			except self.user_doesnt_exist as e:
				users_to_remove.append(person)
				counter['Deleted User'] += 1

		# Users that have been deleted
		print('\t\tRemoving users that couldn\'t be sent to')
		with self.database as db:
			for i in users_to_remove:
				db('DELETE FROM users WHERE username=%s', i)
		print('\t\tFinished sending out messages to {} user(s)'.format(counter))


	def get_moderators(self, subreddit:str) -> list:
		'''
		Returns a list of moderators for a given subreddit

		Parameters:
			subreddit: str
				The name of the subreddit you want to get the moderators of

		Returns:
			list
				A list of usernames of the moderators
		'''

		subreddit_object = self.reddit.subreddit(subreddit)
		subreddit_moderators = subreddit_object.moderator
		moderator_list = list(subreddit_moderators)
		moderator_names = [i.name for i in moderator_list] + self.owner_names
		return moderator_names


	def post_a_comment(self, parentComment:str, msg:praw.models.Message):
		pass

