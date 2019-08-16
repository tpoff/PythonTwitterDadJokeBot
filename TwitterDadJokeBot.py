"""
Contains the class and functions needed to run the Twitter Dad Joke Bot, the bot will
get a joke from the icanhazdadjoke api, send an email to confirm the joke is safe to post, and post
the joke to twitter
"""
from GmailWrapper import GmailWrapper
from TwitterWrapper import TwitterWrapper
import random
import time
import requests


# helper function that will hit the icanhazdadjoke api and return whatever joke it gets from it
def get_dad_joke():
    url = "https://icanhazdadjoke.com"
    headers = {
        "Accept": "application/json"
    }
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        return None
    return resp.json()['joke']


class TwitterDadJokeBot:
    def __init__(self,
                 consumer_api_key,
                 consumer_api_secret_key,
                 access_token,
                 access_token_secret,
                 gmail_user,
                 gmail_password,
                 verify_email,
                 verify_joke=True,
                 verify_timeframe=3600,
                 verify_sleep_interval_time=10):
        self.verify_sleep_interval_time = verify_sleep_interval_time
        self.consumer_api_key = consumer_api_key
        self.consumer_api_secret_key = consumer_api_secret_key
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.gmail_user = gmail_user
        self.gmail_password = gmail_password
        self.twitter = TwitterWrapper(
            consumer_api_key,
            consumer_api_secret_key,
            access_token,
            access_token_secret
        )
        self.gmail = GmailWrapper(gmail_user, gmail_password)
        self.verify_joke = verify_joke
        self.verify_email = verify_email
        self.verify_timeframe = verify_timeframe
        self.joke_preamble = " #PythonDailyJokeBot"

    def format_joke_email_message(self, joke):
        message = '''
        <div>Hi,</div><br>

        <div>This is your dad joke twitter bot. I have a new joke I want you to verify:</div><br>
        <div>Here's the joke: %s</div><br>

        <div>To reject this joke reply "NO_JOKE"</div>
        <div>To suggest a new joke reply "NEW_JOKE"</div>
        <div>To publish this joke right away reply "PUBLISH_JOKE"</div>
        <div>If I don't hear from you I'll publish this joke to your twitter account automatically!</div>''' % joke
        return message

    def format_joke_for_twitter(self, joke):
        """
        :param joke: joke to format for twitter
        :return: twitter ready joke, adds the preamble whatever that may be (in our case it's the hash tag only)
        """
        new_joke = "%s %s" % (joke, self.joke_preamble)
        return new_joke

    def get_joke(self):
        """
        This function will return a joke that is formatted for twitter and meets the 255 character limit
        :return: str of twitter ready joke
        """
        joke = get_dad_joke()
        joke = self.format_joke_for_twitter(joke)
        while len(joke) > 255:
            joke = get_dad_joke()
            joke = self.format_joke_for_twitter(joke)
        return joke

    def get_verified_joke(self):
        """
        This function gets a joke, sends an email asking if the joke is ok to post, and will return it
        if it is, otherwise it will return null,

        I can probably design this function better, definitely break it into smaller functions, but that's
        a task for another day
        :return: str of twitter ready joke
        """
        joke = None
        while joke is None:
            # get a joke
            print("getting joke")
            joke = self.get_joke()

            # get a random id for this joke, this is to tag the email we will send so we can check if we
            # receive a response
            joke_id = random.randint(1000, 9999)

            # send our email with our joke, if we can't send return None indicating no joke
            email_subject = "Twitter Dad Joke Bot Verification id %s" % joke_id
            email_message = self.format_joke_email_message(joke)
            success = self.gmail.send_email([self.verify_email], email_subject, email_message)
            if success is False:
                print("could not send email")
                print(self.gmail.error_message)
                return None

            # now we start a loop, basically every verify_sleep_interval_time we will wake up, check gmail
            # to see if an email response came back matching our random id, if it is we check it's response,
            # otherwise we continue to sleep
            # if verify_time frame time elapses then we exit this loop and post the joke anyway,
            start_wait = time.time()
            print("waiting for joke verification from users")
            while start_wait + self.verify_timeframe >= time.time():
                print("checking email for user response")
                time.sleep(self.verify_sleep_interval_time)
                recent_email = self.gmail.get_emails(num_emails=1)[0]
                subject = recent_email['Subject']
                payload = recent_email['Payload']
                index = subject.find(email_subject)
                if index != -1:
                    # if this is true, then the most recent email has the same subject as the one we sent
                    # so now we need to figure out what his response is,
                    # as it turns out, this is trickier than we expect, because the email will have our
                    # original mail on top of the response, so what we do is we search for all 3 of our terms,
                    # and act on whichever has the highest count in the email, we default to no_joke just to be safe
                    action = "NO_JOKE"
                    count = payload.count("NO_JOKE")
                    if count < payload.count("PUBLISH_JOKE"):
                        action = "PUBLISH_JOKE"
                        count = payload.count("PUBLISH_JOKE")
                    if count < payload.count("NEW_JOKE"):
                        action = "NEW_JOKE"

                    print("response found: ", action)

                    if action == "NO_JOKE":  # return none if they responded no joke
                        return None
                    elif action == "PUBLISH_JOKE":  # return the joke
                        return joke
                    else:  # last but not least, new_joke, set joke to none and break our current loop
                        joke = None
                        break

        return joke

    def tweet_joke(self, joke):
        """
        tweets the joke
        :param joke:
        :return:
        """
        self.twitter.update_status(joke)

    def run(self):
        """
        run the bot,
        :return:
        """
        print("Twitter Joke Bot Running.")
        if self.verify_joke:
            joke = self.get_verified_joke()
        else:
            print("getting Joke")
            joke = self.get_joke()
        if joke is not None:
            print("tweeting joke: ", joke)
            self.tweet_joke(joke)
        else:
            print("Not tweeting joke today, goodbye")
