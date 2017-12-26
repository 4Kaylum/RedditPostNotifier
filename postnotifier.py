import praw
from json import loads, dumps
from requests import post
from os import remove
from time import sleep
import responses

class PostNotifier:
	'''
	Handles the whole postnotifier thingimawatsit
	'''

	def __init__(self, reddit:praw.Reddit, user_directory:str):
		'''
		The input args for this are the praw reddit feature.

		Parameters :: 
			reddit : praw.Reddit
				The Praw reddit object used to send messages
			user_directory : str
				The directory for which all of the user data and webhook are going to be stored
		'''

		self.reddit = reddit
		self.w = user_directory
		self.locate = lambda x: self.w + '/Subreddits/' + x + '.json'
		self.owner_names = ['SatanistSnowflake']
		self.iteration = 0
		self.user_doesnt_exist = praw.exceptions.APIException

				
		# Set up which actions can be run
		self.run_actions = {
			'ADD': self.add_to_mailing_list,
			'REMOVE': self.remove_from_mailing_list,
			'DELETE': self.remove_from_mailing_list,
			'DEL': self.remove_from_mailing_list,
			'REM': self.remove_from_mailing_list,
			'SEND': self.send_to_mailing_list,
			'COMMENT': self.post_a_comment,
			'DISCORD': self.set_webhook_for_subreddit,
			'WEBHOOK': self.set_webhook_for_subreddit
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

			# Put in a try so you can catch timeouts
			try:

				# Check the inbox
				print('{} Checking inbox...'.format(str(hex(self.iteration))[2:].upper()))
				self.just_acted = False
				self.check_inbox()

				# Sleep
				print('Sleeping for {}'.format(delay))
				sleep(delay)

			# Catch timeouts
			except Exception as e:

				# Just sleep for longer I guess
				print('Sleeping for {} due to timeout'.format(timeout_delay))
				print('\t{}'.format(e))
				sleep(timeout_delay)
			except KeyboardInterrupt as e:
				print('Shutting down...')
				return

	def check_inbox(self):
		'''
		Checks the inbox of the user logged in and refers each post to a
		respective handling function.
		'''

		# Get the messages into a list
		inbox_messages = self.reddit.inbox.unread(mark_read=True)
		inbox_list = [i for i in inbox_messages if type(i) == praw.models.Message]

		# Iterate through all of the messages
		for msg in inbox_list:

			# Print out to console
			print('New message ->\n\tAuthor :: {0.author}\n\tSubject :: {0.subject}'.format(msg))
			print('\tMarking as read...')
			msg.mark_read()

			# Check that the message is valid
			action_for_subreddit = msg.subject.replace(' ','').upper().split('::')
			if len(action_for_subreddit) == 1 or '' in action_for_subreddit:

				# The message is not valid, abort
				print('\tInvalid action :: Replying to user and aborting thread\n')
				try:
					msg.reply(responses.INVALIDMESSAGETOBOT)
				except self.user_doesnt_exist as e:
					pass

			else:

				# Try and run an action on the given message
				try:

					# Split the sub name from the rest of the subject...
					sub = msg.subject.split('::')[1].split(' ')
					sub_run = None
					for i in sub:
						if sub_run == None and i != '':
							sub_run = i

					# Run the action
					self.run_actions[action_for_subreddit[0]](sub_run.upper(), msg)
					
				except KeyError:

					# If you get here, the user tried to do something that the bot wasn't set up for
					# Thus, tell them the response was invalid
					print('\tInvalid action :: Replying to user and aborting thread')
					try:
						msg.reply(responses.INVALIDMESSAGETOBOT)
					except self.user_doesnt_exist as e:
						pass

		# We have now gone through all of the messages in the inbox
		# Huzzah

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

		# Load a file
		try:
			print('\t\tReading file...')
			with open(self.locate(subreddit)) as a:
				data = loads(a.read())
				print('\t\tFile read successfully')
		except FileNotFoundError:
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
		try:
			msg.reply(responses.ADDEDTOMAILINGLIST.format(subreddit))
		except self.user_doesnt_exist as e:
			pass

		z = self.post_to_webhook(subreddit, embeds=[{'fields':[
				{
					'name': 'User Added To {}'.format(subreddit),
					'value': msg.author.name,
					'inline': False
				}
			]}])

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

		# Load a file
		try:
			print('\t\tReading file...')
			with open(self.locate(subreddit)) as a:
				data = loads(a.read())
				print('\t\tFile read successfully')
		except FileNotFoundError:
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
		try:
			msg.reply(responses.REMOVEDFROMMAILINGLIST.format(subreddit))
		except self.user_doesnt_exist as e:
			pass

		z = self.post_to_webhook(subreddit, embeds=[{'fields':[
				{
					'name': 'User Removed From {}'.format(subreddit),
					'value': msg.author.name,
					'inline': False
				}
			]}])

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
		moderator_names = self.getModerators(subreddit)

		# See if the user is in the moderator list
		if author not in moderator_names:

			# They are not a moderator
			print('\t\tUser not a moderator - responding and aborting')
			try:
				msg.reply(responses.NOTALLOWEDTOSEND.format(subreddit))
			except self.user_doesnt_exist as e:
				pass
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
		subject_message = msg.subject[len(msg.subject.split('::')[0]) + len(subreddit) + 2:]
		while True:
			try:
				if subject_message[0] == ' ':
					subject_message = subject_message[1:]
				else:
					break
			except IndexError:
				subject_message = 'None'
		subject = 'UPDATE FROM {} :: {}'.format(subreddit.upper(), subject_message)

		# Get body text
		body = msg.body

		# Send the messages
		counter = {'Success':0,'Deleted User':0,'Tries':0}
		user_removals = []
		print('\t\tSending out to users now ->')
		for person in data['Users']:
			counter['Tries'] += 1
			print('\t\t\t:: {}'.format(person))
			try:
				self.reddit.redditor(person).message(subject, body + responses.BOTDISCLAIMERMESSAGE + ' ^^:: ^^[Messenger](/u/{})'.format(author))
				counter['Success'] += 1
			except self.user_doesnt_exist as e:
				user_removals.append(person)
				counter['Deleted User'] += 1

		# Users have ceased to exist - remove them from the list
		if user_removals:
			x = data['Users']
			for i in user_removals:
				x.remove(i)
			data['Users'] = x
			with open(self.locate(subreddit), 'w') as a: a.write(dumps(data, indent=4))

		print('\t\tFinished sending out messages to {} user(s)'.format(counter))

		z = self.post_to_webhook(subreddit, embeds=[{'title':'Message Sent From {}'.format(subreddit), 'fields':[
				{
					'name': 'Successful Message Sends', 
					'value': counter['Success'],
					'inline': True
				}, {
					'name': 'Unsuccessful Message Sends', 
					'value': '{} (these are usually due to deleted accounts)'.format(counter['Deleted User']),
					'inline': False
				}, {
					'name': 'Total Message Tries', 
					'value': counter['Tries'],
					'inline': False
				}, {
					'name': 'Author of Message', 
					'value': author.name,
					'inline': False
				}
			]}, {'fields':[
				{
					'name': subject,
					'value': body,
					'inline': False
				}]}]
			)

	def set_webhook_for_subreddit(self, subreddit:str, msg:praw.models.Message):
		'''
		The bot will check if the message was sent by a moderator of the mentioned subreddit, 
		and if it was it will store a given webhook from the body.

		Messages should be sent with a subject of 'DISCORD::SUBREDDIT', and the body text is
		the webhook from the channel.

		Parameters :: 
			subreddit : str
				The name for the subreddit that is going to be worked on for this user
			msg : praw.models.Message
				The original message that was sent by the user
		'''

		print('\tValid action -> \n\t\tSetting up a Discord webhook for {}'.format(subreddit))

		author = msg.author

		# Get the server moderators
		print('\t\tGenerating list of moderators for the subreddit')
		moderator_names = self.getModerators(subreddit)

		# See if the user is in the moderator list
		if author not in moderator_names:

			# They are not a moderator
			print('\t\tUser not a moderator - responding and aborting')
			try:
				msg.reply(responses.NOTALLOWEDTOSEND.format(subreddit))
			except self.user_doesnt_exist as e:
				pass
			return

		# They are a moderator - tell the user that the messages will be sent out now
		print('\t\tUser is a moderator - continuing')

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

		# Change the given Discord link
		print('\t\tChanging the saved webhook link')
		hook = msg.body
		data['Discord Webhook'] = hook
		with open(self.locate(subreddit), 'w') as a: a.write(dumps(data, indent=4))

		# Ping the webhook
		z = self.post_to_webhook(subreddit, embeds=[{'fields':[
				{
					'name':'Webhook Setup Ping for {}'.format(subreddit), 
					'value':'This is the ping to make sure that the given webhook works properly.', 
					'inline':False
				}
			]}])

		# Reply to the user
		print('\t\tReply back to the user')
		msg.reply(responses.DISCORDWEBHOOKMESSAGE.format(subreddit))

	def getModerators(self, subreddit:str):
		subreddit_object = self.reddit.subreddit(subreddit)
		subreddit_moderators = subreddit_object.moderator
		moderator_list = list(subreddit_moderators)
		moderator_names = [i.name for i in moderator_list] + self.owner_names
		return moderator_names

	def post_to_webhook(self, subreddit:str, **kwargs):
		'''
		Posts a webhook to a subreddit, from a given link inside the stored data
		Formats all inputs into an embed and posts it to the link

		Parameters :: 
			subreddit : str
				The name of the subreddit being sent to
			content
			username
			footer
		'''

		print('\t\tGenerating webhook to be sent')

		# Get the arguments
		content = kwargs.get('content', None)
		username = kwargs.get('username', 'PostNotifier')
		footer = kwargs.get('footer', 'PostNotifier on /u/magicSquib created by /u/SatanistSnowflake')
		embeds = kwargs.get('embeds', None)

		# Determine the username on the webhook
		try:
			out = {'username': username.name}
		except Exception:
			out = {'username': str(username)}

		# Determine the webhook's content
		if content == None:
			pass
		else:
			out['content'] = content

		# Determine the embeds
		if embeds == None:
			pass
		else:
			for i in embeds:
				i['footer'] = {'text':footer}
			out['embeds'] = embeds

		print('\t\tWebhook generated - reading link from file')

		# Read the webhook from file
		try:
			print('\t\tReading file...')
			with open(self.locate(subreddit)) as a:
				data = loads(a.read())
				print('\t\tFile read successfully')
		except:
			print('\t\tFile not found - inventing values')
			data = {'Users':[],'Discord Webhook':''}

		hook = data['Discord Webhook']
		if hook == '':
			print('\t\tNo webhook defined - aborting')
			return

		print('\t\tSending out webhook ping')
		z = post(hook, json=out)

		# Check the status code
		if z.status_code in [200, 201, 204]:
			print('\t\tSent out webhook successfully')
		else:
			print('\t\tWebhook ping failed')
			print('\t\t{}'.format(z.text))
		return z

	def post_a_comment(self, parentComment:str, msg:praw.models.Message):
		pass
