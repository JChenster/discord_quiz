# Discord Quiz

## Top Level Description
A bot written in Python that allows a person to locally host an interactive multi-player timed multiple choice trivia quiz game with custom questions in their Discord server. Each game will be composed of x trivia questions with 3 multiple choice options where players have x seconds to answer by typing 1, 2, or 3 in the channel where the game is being hosted. Players that answer incorrectly without an extra life are eliminated. If they have an extra life, they essentially have another try.

## Background
I wrote this discord bot back in Summer of 2018. I have decided to recently upload the code. The specific usernames and webhooks necessary to run this bot have been removed and replaced with strings indicating the necessity for replacement. The specific version of 

## Usage
Required libraries: discord, discord_hooks (included in repo)
``` 
pip3 install discord 
```

## Commands
### For hosts:
#### While hosting:

!startgame - Initiate the interactive process of starting a game

!pot - Set prize pool

!settimer - Set time allowed per question

!startreg - Start registration for current game

!q - Display next question

!res - Shows results of most recent question

!endgame - End current game and display winners

!lb - Show leaderboard for current game

Various sound commands are also included: s!wait1, s!wait2, s!win, s!sav, s!gt, s!t, s!q12, s!info

#### Administrative:

!updatelb - Initiate the interactive process of updating leaderboard (info is saved to leaderboard.csv)

!payout - Report the payout for a game in a channel (if money is being offered as a prize and split across winners)

.ticktock - See what game is currently happening (if any)

.lb - Display leaderboard

### For players:
!help - Provides some basic info and a list of helpful commands

!join - Join the game (only works when registration is open)

!myscore - Check how many questions you answered correctly (only works after the game)

!t - Displays how much time is left to answer the question

