"""
Contains a wrapper class for twython for ease of use,
in case I want to expand it at a later date,
"""
from twython import Twython


class TwitterWrapper:
    def __init__(self,
                 consumer_api_key,
                 consumer_api_secret_key,
                 access_token,
                 access_token_secret):
        self.twitter = Twython(
            consumer_api_key,
            consumer_api_secret_key,
            access_token,
            access_token_secret
        )

    def update_status(self, message):
        self.twitter.update_status(status=message)
