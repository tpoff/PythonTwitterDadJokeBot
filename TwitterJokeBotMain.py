'''
Entry point for the twitter dad bot,
creates an instance of the bot and runs it, that's it.
The bot does the rest
'''
import config
from TwitterDadJokeBot import TwitterDadJokeBot


if __name__ == "__main__":
    joke_bot = TwitterDadJokeBot(
        config.twitter_consumer_api_key,
        config.twitter_consumer_api_secret_key,
        config.twitter_access_token,
        config.twitter_access_token_secret,
        config.gmail_user,
        config.gmail_password,
        config.verify_joke_email
    )
    joke_bot.run()
