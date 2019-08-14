# Python Twitter Joke Bot
This project is a twitter bot written in python that will get a joke from the icanhazdadjoke api, formats it for twitter,
sends a verification email to the owner ensuring the joke is approved, and then finally posts the joke to twitter.

# Requirements
You will need python 3.x to run the bot, a requirements.txt file is provided with the needed packages.

You will also need a twitter developer account to get the needed api keys and access tokens to interface with the twitter api.
More information on getting a setting up a twitter developer account can be found <a href="https://developer.twitter.com/en/apply-for-access.html">Here</a>

Optionally you can also setup a gmail account to send an email to approve the joke. You can find more information on how to setup a gmail account to allow python to interact with it <a href="https://stackabuse.com/how-to-send-emails-with-gmail-using-python/">here</a>

Note: the above link will have more information in general on how to access and use gmail through python. As a cliff notes version, you will need to <a href='https://support.google.com/accounts/answer/6010255'>Allow Less Secure Apps</a> on your account. This process may be a bit more complicated to setup just because of how google handles their developer accounts, which is why this is an optional step. The gmail configuration is not needed to run the bot. I would not recommend using your main gmail account if you intend to setup this part of the bot.

# Usage
To run the bot simply run the TwitterJokeBotMain.py script in python after adding the relevant information to the config.py file.
>python TwitterJokeBotMain.py