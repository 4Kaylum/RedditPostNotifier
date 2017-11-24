# Reddit PostNotifier

PostNotifier is a reddit bot that's built to help subreddit moderators communicate with their users. Users can sign up to the bot's mailing list for any given subreddit, and then the moderators of that subreddit can bulk send messages to all of the signed up users. This is useful for subreddits that may not get frequent updates, but are still interesting to read through.

## How to use

Because you can interact with the bot either as a moderator or as a user, there are two ways to use the bot.

### Users

To sign up for the bot's mailing list, send it a message with the subject `ADD::{}`, where `{}` is the name of the subreddit. This isn't case sensitive. That's all you need to do to be signed up for posts. There's nothing complicated about that, really. 

To be removed, send it a message with the subject `REMOVE::{}`, with `{}` as the subreddit name. Again, not case sensitive.

That's about all you need to know, as a user!

### Moderators

You don't need to do anything special to set the bot up on your subreddit - just tell your users to sign up, as detailed above, and then when you want to send out messages, send the bot a message with the subject `POST::{0} {1}`, where `{0}` is the name of the subreddit, and `{1}` is the title of the message you want to send. All of the body text you put in the message will be copied over to the messages that are sent out to your users.

When users sign up or remove themselves from the mailing list, and when messages are sent out, the bot can send a POST request to a webhook, which is known to work with Discord. To send the bot a message that triggers a Discord webhook, send it a message with the subject `DISCORD::{}`, where `{}` is the name of the subreddit, and the body text of the message is the link to the webhook.

And there ya go! That's all you need to know! c:

## I think this is really cool!

Woah! Me too! If you **really** like it, you can go follow me on [Twitter], or hit me up on [Patreon] or even just send me a one-off donation on [PayPal]! Anything's good, even nothing. Thank you for using my project ♥

[Twitter]: https://twitter.com/4Kaylum
[Patreon]: https://patreon.com/CallumBartlett
[PayPal]: https://paypal.me/CalebBartlett
