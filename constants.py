# 1) Create an instance of a Discord Application that this bot will run on
# https://discord.com/developers/applications/
# The name/avatar of this application can be anything you want
# This appliation must then be invited to your server
# You can obtaining a link to do so by selecting the application > OAuth2 > Scopes > bot
# Set permissions in the URL to 8

# To connect this bot to the application you just set up, we need its token
# This can be found in: Bot > Click to Reveal Token
TOKEN = "YOUR TOKEN GOES HERE"

# 2) We will need to set up a webhook for our bot to display questions, answers, and the leaderboard too
# Pick the channel that you want all this information to be displayed
# Go to: Edit Channel > Integrations > Webhooks > New Webhook
# One again, the name/avatar of this webhook can be anything you want
# Copy and paste the webhook URL below
CHANNEL_WEBHOOK_URL = "YOUR CHANNEL WEBHOOK URL GOES HERE"

# 3) Create a role that is needed in order to host trivia games.
# Only users with this role will be able to host trivia games.
# This role can be named anything you want. The only thing that must be done is it must be specified below
HOST_ROLE = "YOUR HOST ROLE NAME GOES HERE"