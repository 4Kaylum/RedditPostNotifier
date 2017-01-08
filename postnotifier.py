import praw
from json import loads, dumps
from requests import post
from os import remove
from time import sleep
import responses
from requests.exceptions import ConnectionError

class PostNotifier:
	'''
	Handles the whole postnotifier thingimawatsit
	'''

	def __init__(self, reddit:praw.Reddit, userDirectory:str):
		'''
		The input args for this are the praw reddit feature.

		Parameters :: 
			reddit : praw.Reddit
				The Praw reddit object used to send messages
			userDirectory : str
				The directory for which all of the user data and webhook are going to be stored
		'''

		self.reddit = reddit
		self.w = userDirectory
		self.locate = lambda x: self.w + '/' + x + '.json'
		self.ownerNames = ['SatanistSnowflake']
		self.iteration = 0

				
		# Set up which actions can be run
		self.runActions = {
			'ADD': self.addToMailingList,
			'REMOVE': self.removeFromMailingList,
			'DELETE': self.removeFromMailingList,
			'DEL': self.removeFromMailingList,
			'REM': self.removeFromMailingList,
			'SEND': self.sendToMailingList,
			'COMMENT': self.postAComment
		}

	def run(self, *, delay:int=30, timeoutDelay:int=120):
		'''
		Call this to run all the featres of the bot on a loop

		Parameters :: 
			delay : int = 30
				The delay at which all of the bot features will be run
			timeoutDelay : int = 120
				The sleeping time for when the bot recieves a connection error from the server
		'''

		# Start a loop so you'll run forever
		while True:

			self.iteration += 1

			# Put in a try so you can catch timeouts
			try:

				# Check the inbox
				print('{} Checking inbox...'.format(str(hex(self.iteration))[2:]))
				self.justActed = False
				self.checkInbox()

				# Sleep
				print('Sleeping for {}'.format(delay))
				sleep(delay)

			# Catch timeouts
			except ConnectionError:

				# Just sleep for longer I guess
				print('Sleeping for {} due to timeout'.format(timeoutDelay))
				sleep(timeoutDelay)


	def checkInbox(self):
		'''
		Checks the inbox of the user logged in and refers each post to a
		respective handling function

		Parameters :: N/A
		'''

		# Get the messages into a list
		inboxMessages = self.reddit.inbox.unread(mark_read=True)
		inboxList = [i for i in inboxMessages if type(i) == praw.models.Message]

		# Iterate through all of the messages
		for msg in inboxList:

			# Print out to console
			print('New message ->\n\tAuthor :: {0.author}\n\tSubject :: {0.subject}'.format(msg))
			print('\tMarking as read...')
			msg.mark_read()

			# Check that the message is valid
			actionForSub = msg.subject.replace(' ','').upper().split('::')
			if len(actionForSub) == 1 or '' in actionForSub:

				# The message is not valid, abort
				print('\tInvalid action :: Replying to user and aborting thread\n')
				msg.reply(responses.INVALIDMESSAGETOBOT)
				return

			else:

				# Try and run an action on the given message
				try:

					# Split the sub name from the rest of the subject...
					sub = msg.subject.split('::')[1].split(' ')
					subRun = None
					for i in sub:
						if subRun == None and i != '':
							subRun = i

					# Run the action
					self.runActions[actionForSub[0]](subRun.upper(), msg)
					return
					
				except KeyError:

					# If you get here, the user tried to do something that the bot wasn't set up for
					# Thus, tell them the response was invalid
					print('\tInvalid action :: Replying to user and aborting thread')
					msg.reply(responses.INVALIDMESSAGETOBOT)
					return

		# We have now gone through all of the messages in the inbox
		# Huzzah

	def addToMailingList(self, subreddit:str, msg:praw.models.Message):
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

		# Load a file
		try:
			print('\t\tReading file...')
			with open(self.locate(subreddit)) as a:
				data = loads(a.read())
				print('\t\tFile read successfully')
		except:
			print('\t\tFile not found - inventing values')
			data = {'Users':[],'Discord Webhook':''}

		# Add the user to the list
		print('\t\tAdding user to list')
		if msg.author not in data['Users']:
			data['Users'].append(msg.author)
		else:
			print('\t\tUser already signed up - passing')

		# Save it back to data
		with open(self.locate(subreddit), 'w') as a:
			print('\t\tSaving data')
			a.write(dumps(data, indent=4))

		# Respond to user
		print('\t\tResponding to user')
		msg.reply(responses.ADDEDTOMAILINGLIST.format(subreddit))

	def removeFromMailingList(self, subreddit:str, msg:praw.models.Message):
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

		# Load a file
		try:
			print('\t\tReading file...')
			with open(self.locate(subreddit)) as a:
				data = loads(a.read())
				print('\t\tFile read successfully')
		except:
			print('\t\tFile not found - inventing values')
			data = {'Users':[msg.author],'Discord Webhook':''}

		# Remove the user to the list
		print('\t\tRemoving user from list')
		try:
			data['Users'].remove(msg.author)
		except ValueError: 
			print('\t\tUser not signed up - passing')

		# Check if it's empty
		if data['Users'] == []:

			# It's empty - delete
			try:
				print('\t\tMessaging list now empty - deleting')
				remove(self.locate(subreddit))
			except FileNotFoundError:
				pass

		else:

			# Everything still exists - let's save it to storage
			with open(self.locate(subreddit), 'w') as a:
				print('\t\tWriting messaging list back to storage')
				a.write(dumps(data, indent=4))

		# Respond to user
		print('\t\tResponding to user')
		msg.reply(responses.REMOVEDFROMMAILINGLIST.format(subreddit))

	def sendToMailingList(self, subreddit:str, msg:praw.models.Message):
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
		subredditObj = self.reddit.subreddit(subreddit)
		subredditModObj = subredditObj.moderator
		moderatorList = list(subredditModObj)
		moderatorNames = [i.name for i in moderatorList]

		# See if the user is in the moderator list
		if author not in moderatorNames:

			# They are not a moderator
			print('\t\tUser not a moderator - responding and aborting')
			msg.reply(responses.NOTALLOWEDTOSEND.format(subreddit))
			return

		# They are a moderator - tell the user that the messages will be sent out now
		print('\t\tUser is a moderator - responding')
		msg.reply(responses.ABOUTTOBESENT.format(subreddit))

		# Get the messages to be sent to the user
		try:
			print('\t\tReading file...')
			with open(self.locate(subreddit)) as a:
				data = loads(a.read())
				print('\t\tFile read successfully')
		except:
			print('\t\tFile not found - inventing values')
			data = {'Users':[],'Discord Webhook':''}

		# Make sure that the message author is in them
		if author not in data['Users']:
			print('\t\tAdding author to user list')
			data['Users'] = [author] + data['Users']
			with open(self.locate(subreddit), 'w') as a: a.write(dumps(data, indent=4))

		# Get the format ready for the messages - get subject
		subjectMsg = msg.subject[len(msg.subject.split('::')[0]) + len(subreddit) + 2:]
		while True:
			if subjectMsg[0] == ' ':
				subjectMsg = subjectMsg[1:]
			else:
				break
		subject = 'UPDATE FROM {} :: {}'.format(subreddit.upper(), subjectMsg)

		# Get body text
		body = msg.body

		# Send the messages
		counter = 0
		print('\t\tSending out to users now ->')
		for person in data['Users']:
			counter += 1
			print('\t\t\t:: {}'.format(person))
			self.reddit.redditor(person).message(subject, body + responses.BOTDISCLAIMERMESSAGE + ' ^^:: ^^[Messenger](/u/{})'.format(author))

		print('\t\tFinished sending out messages to {} user(s)'.format(counter))


	def postAComment(self, parentComment, msg):
		pass
