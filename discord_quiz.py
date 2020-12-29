import discord
import random
import time
from discord_hooks import Webhook
from discord.utils import get

client = discord.Client()

players = dict()
active_reg = False
active_game = False
questionNum = 1

host_dict = {
                'insert_host_discord_username': 'insert_quiz_name',
            }
hooks_dict = {
                'insert_quiz_name': 'quiz_channel_webhook'
            }

@client.event
async def on_message(message):

    if message.author == client.user:
        return

    global players
    global db
    global question_cooldown_start
    global results_cooldown_start
    global active_game
    global current_host

    try:
        if active_game:
            pass
    except:
        active_game = False

    try:
        checking_current_host = current_host
    except:
        current_host = str(message.author)
    
    life_count = 1

    try:
        author_roles = list(map(lambda x: str(x), message.author.roles))
    except:
        author_roles = []

    if message.content.startswith('!startgame') and message.channel.is_private and str(message.author) in host_dict.keys():
        if active_game:
            msg = 'Hold on. There is currently a game occuring right now or someone else is setting up a game. Wait until it is finished.'
            await client.send_message(message.channel,msg)
        else:
            if message.content.startswith('!startgame') and message.channel.is_private:
                active_game = True

                print(str(message.author), 'is entering questions now.')
                
                msg = '**Registration started!** Try to enter all the information correctly. If you mess something up, you have to **follow through** and cancel all at the end and restart.'
                await client.send_message(message.channel, msg)

                global discord_webhook_url
                global current_game

                current_game = host_dict[str(message.author)]
                msg = f'Automatically detected game as **{current_game}**! Now please enter how many questions you want.'
                await client.send_message(message.channel,msg)
                discord_webhook_url = hooks_dict[current_game]

                value_entered = False
                global question_count

                while not(value_entered):
                    user_input = await client.wait_for_message(author=message.author, channel=message.channel)
                    try:
                        question_count = int(str(user_input.content[:]))
                        value_entered = True
                        msg = f'Now, enter **{question_count} questions**, one at a time.'
                        await client.send_message(message.channel,msg)
                    except:
                        msg = 'Something went wrong. Make sure to type in an integer and nothing else. Try again.'
                        await client.send_message(message.channel,msg)

                fileIn = open('questions.txt','w')

                for x in range(question_count):
                    question_entered = False
                    msg = f'You are now entering **Question {x+1}.**'
                    await client.send_message(message.channel,msg)

                    while not(question_entered):
                        user_input = await client.wait_for_message(author=message.author, channel=message.channel)
                        try:
                            checking_ans = int(str(user_input.content[:]).split('/')[4])
                            fileIn.write(str(user_input.content[:]) + '\n')
                            question_entered = True
                        except:
                            msg = 'Something went wrong. Make sure to use the syntax: `<question>/<option>/<option>/<option>/<number of answer>` Try again.'
                            await client.send_message(message.channel,msg)                

                fileIn.close()

                ## asks if autowin or not
                msg = f'Please decide if you want the game to be autowin or not. Enter `yes` for autowin or `no` for no autowin.'
                await client.send_message(message.channel,msg)
                global autowin
                autowin_entered = False

                while not(autowin_entered):
                    user_input = await client.wait_for_message(author=message.author, channel=message.channel)
                    if str(user_input.content[:]).lower() == 'yes':
                        autowin = True                        
                        autowin_entered = True
                    elif str(user_input.content[:]).lower() == 'no':
                        autowin = False
                        autowin_entered = True
                    else:
                        msg = 'Something went wrong. Make sure to say `yes` or `no`. Try again.'
                        await client.send_message(message.channel,msg)   

                ## confirms
                msg = 'Questions entered. Type `cancel` at this point if you wish to cancel. Otherwise, type anything that is not `cancel` to finish game registration.'
                await client.send_message(message.channel,msg)
                user_input = await client.wait_for_message(author=message.author, channel=message.channel)
                if str(user_input.content[:]).lower() == 'cancel':
                    active_game = False
                    msg = 'Game set up cancelled! Do **!startgame** to try again.'
                    await client.send_message(message.channel,msg)
                    print(str(message.author), 'has cancelled game registration')
                else:
                    msg = 'Game fully set up! **Now make sure to go and set the pot and timer in the game chat, not here.** :moneybag::timer: This step is very important!!!'
                    await client.send_message(message.channel,msg)
                    print(f'Success! Questions have been entered by {str(message.author)}')

                fileIn = open('questions.txt','r')
                global db
                db = fileIn.readlines()
                fileIn.close()

                current_host = str(message.author)

    if 'Hosts' in author_roles:

        if message.content.startswith('.ticktock'):
            try:
                msg = f'**{current_game} is on the clock!** :clock10:'
                await client.send_message(message.channel, msg)
            except:
                msg = '**No game is on the clock!** :clock10:'
                await client.send_message(message.channel, msg)

        ###
        ### UPDATE LB
        ###
        if message.content.startswith('!updatelb'):
            # get names
            msg = 'Enter the discord tag of each player that won the game. Seperate each winner by a comma e.g. User1#0001, User2#0002.'
            await client.send_message(message.channel,msg)
            user_input = await client.wait_for_message(author=message.author,channel=message.channel)
            winners = str(user_input.content [:]).split(',')
            winners = list(map(lambda x: x.strip(), winners))

            # get amount
            msg = 'Enter the amount each player won with no $ sign e.g. 1.67.'
            await client.send_message(message.channel,msg)
            user_input = await client.wait_for_message(author=message.author,channel=message.channel)
            payout = float(str(user_input.content[:]).strip())

            # confirmation
            msg = 'Information entered. Type `cancel` at this point if you wish to cancel. Otherwise, type anything that is not `cancel` to finish updating leaderboard.'
            await client.send_message(message.channel,msg)
            user_input = await client.wait_for_message(author=message.author, channel=message.channel)
            if str(user_input.content[:]).lower() == 'cancel':
                msg = 'Leaderboard not updated. Do !updatelb to try again'
                await client.send_message(message.channel,msg)
            else:
                try:
                    # update lb
                    ## convert to dict
                    pay_dict = dict()

                    fileIn = open('lb.csv','r')
                    lines = fileIn.readlines()
                    for line in lines:
                        values = line.split(',')
                        pay_dict[values[0]] = float(values[1])
                    fileIn.close()

                    # update dict

                    for winner in winners:
                        if winner in pay_dict.keys():
                            pay_dict[winner] += payout
                        else:
                            pay_dict[winner] = payout

                    unique = list(set(pay_dict.values()))
                    unique.sort()
                    unique = unique[::-1]

                    # update csv
                    fileIn = open('lb.csv','w')
                    for value in unique:
                        for player in pay_dict.keys():
                            if pay_dict[player] == value:
                                fileIn.write(player+','+str(round(pay_dict[player],2))+'\n')

                    fileIn.close()
                    
                    msg = 'Leaderboard updated. Do .lb to post new leadboard in #leaderboard.'
                    await client.send_message(message.channel,msg)
                except:
                    msg = 'Something went wrong. Leaderboard not updated. Do !updatelb to try again'
                    await client.send_message(message.channel,msg)

        ###
        ### EMBED PAYOUT MSG
        ###
        if message.content.startswith('!payout'):
            try:
                await client.delete_message(message)
                # process input
                pay_input = str(message.content[8:]).split(' ')
                prize_pot = float(pay_input[0])
                payout = float(pay_input[1])
                winners_num = int(pay_input[2])
                if len(pay_input) == 4:
                    game_name = pay_input[3]
                elif len(pay_input) == 5:
                    game_name = pay_input[3] + ' ' + pay_input[4]
                elif len(pay_input) == 6:
                    game_name = pay_input[3]+ ' ' + pay_input[4]+ ' ' + pay_input[5]
                avatar = message.author.avatar_url

                # process game name
                if game_name.lower() == 'insert_game_name':
                    thumbnail = 'insert_link_to_thumbnail'
                    game_name = 'insert_game_name'
                else:
                    cause_error = 0/0
                
                # embeds payout
                embed = Webhook('payouts_channel_webhook', color = 250000)
                embed.set_author(name=str(message.author)[:-5], icon=avatar)
                embed.add_field(name=f'{game_name} Payout:',value=f"${payout} / {winners_num} winners",inline = False)
                embed.add_field(name='Prize Pool:',value=f"${prize_pot}",inline = False)
                embed.set_thumbnail(thumbnail)
                embed.set_footer(text='Remember to upvote if you won and downvote if you lost!',ts=True)
                embed.post()

            # error message
            except:
                await client.delete_message(message)
                temp_msg = await client.send_message(message.channel, 'Something went wrong! Make sure to use the syntax: `!payout <pot> <payout> <winners> <game>`.')
                time.sleep(2)
                await client.delete_message(temp_msg)

    ###
    ### WINNINGS LEADERBOARD
    ###
    if 'Moderators' in author_roles and str(message.channel) in 'leaderboard':
        if message.content.startswith('.lb'):
            await client.delete_message(message)

            ## convert to dict
            pay_dict = dict()

            fileIn = open('lb.csv','r')
            lines = fileIn.readlines()
            for line in lines:
                values = line.split(',')
                pay_dict[values[0]] = float(values[1])

            fileIn.close
            unique = list(set(pay_dict.values()))
            unique.sort()
            unique = unique[::-1]

            ## creates msg
            count = 1
            msg = ''
            for value in unique:
                for player in pay_dict.keys():
                    if pay_dict[player] == value:
                        msg += f"**{count}.** {player[:-5]}  ---  **${pay_dict[player]}**\n"
                        count += 1

            embed = Webhook("leaderboard_channel_webhook", color = 520000)
            embed.add_field(name='All Games Leaderboard',value=msg)
            embed.set_footer(ts=True)
            embed.post()

    permitted_channels = []
    if str(message.channel).lower() not in permitted_channels:
        return

    if 'Hosts' in author_roles and (str(message.author) == current_host):

        if message.content.startswith('!pot'):
            try:
                global pot
                pot = float(str(message.content[:])[5:])
                if pot > 0:
                    pass
                else:
                    crash = 0/0
                msg = f'Done! The pot is now **${pot}**'
                print('The pot is: $' + str(pot))
                await client.send_message(message.channel, msg)                
            except:
                msg = 'Something went wrong! Make sure to use the syntax: `!pot <number of dollars>`'
                await client.send_message(message.channel, msg)
                temp_msg = await client.send_message(message.channel, msg)
                time.sleep(2)
                await client.delete_message(temp_msg)

        if message.content.startswith('!settimer'):
            try:
                global timer_length
                timer_length = float(str(message.content[:])[10:])
                if timer_length > 0:
                    pass
                else:
                    crash = 0/0
                print('The new timer length is:', str(timer_length),'seconds')
                msg = f'Done! The timer length is now **{timer_length} seconds**'
                await client.send_message(message.channel, msg)    
            except:
                msg = 'Something went wrong! Make sure to use the syntax: `!pot <number of seconds>`'
                temp_msg = await client.send_message(message.channel, msg)
                time.sleep(2)
                await client.delete_message(temp_msg)


        if message.content.startswith('!q'):
            await client.delete_message(message)

            try:
                checking_time = timer_length
                checking_pot = pot

                if timer_length == 0:
                    create_error = 0/0

                if pot == 0:
                    create_error = 0/0

                question = db[0]
                db.remove(question)
                global questionParts
                questionParts = question.split('/')

                ## SEND Q
                global questionNum
                msg = '\n'.join(questionParts[1:4])
                embed = Webhook(discord_webhook_url, color = 123123)
                embed.add_field(name=str(questionNum) + ". " + questionParts[0],value=msg)
                embed.set_footer(ts=True)
                embed.post()

                ## SET/RESET VARIABLES
                global alreadyAnswered
                alreadyAnswered = []
                global allPlayersLog
                allPlayersLog = []
                global inPlayersLog
                inPlayersLog = []
                global start
                start = time.time()

            except:
                msg = 'Something went wrong! Make sure you already set the pot and timer length!'
                temp_msg = await client.send_message(message.channel, msg)
                time.sleep(2)
                await client.delete_message(temp_msg)

        if message.content.startswith('!startreg'):
            await client.delete_message(message)
            global active_reg
            active_reg = True
            msg = 'Game Registration Started! Type **!join** to join the game. :dollar::money_mouth::smile:'
            await client.send_message(message.channel, msg)

        if message.content.startswith('!endreg'):
            await client.delete_message(message)
            active_reg = False
            msg = 'Game Registration Ended!'
            await client.send_message(message.channel, msg)

        if message.content.startswith('!res'):
            check_time = time.time()
            if check_time - start > timer_length:
                await client.delete_message(message)

                ## PUNISH WRONG ANSWERS
                for player in players.keys():
                    currentScore = int(players[player])
                    if not(autowin) and questionNum == question_count:
                        players[player] = currentScore - 2
                    else:
                        players[player] = currentScore - 1

                questionNum += 1

                ## SEND ANS
                answer = int(questionParts[-1])
                embed = Webhook(discord_webhook_url, color = 320000)
                embed.add_field(name=f"Answer: {answer}",value=questionParts[answer])
                embed.set_footer(ts=True)
                embed.post()

                ## PLAYERS IN
                options = '\n'.join(questionParts[1:-1])

                answer = int(questionParts[-1][0])
                global resultsTally
                if answer == 1:
                    resultsTally = '|' + ':white_check_mark:' * inPlayersLog.count(1) + '\n|' + ':x:' * inPlayersLog.count(2) + '\n|' + ':x:' * inPlayersLog.count(3)
                elif answer == 2:
                    resultsTally = '|' + ':x:' * inPlayersLog.count(1) + '\n|' + ':white_check_mark:' * inPlayersLog.count(2) + '\n|' + ':x:' * inPlayersLog.count(3)
                elif answer == 3:
                    resultsTally = '|' + ':x:' * inPlayersLog.count(1) + '\n|' + ':x:' * inPlayersLog.count(2) + '\n|' + ':white_check_mark:' * inPlayersLog.count(3)

                embed = Webhook(discord_webhook_url, color = 320000)
                embed.add_field(name="Question Results",value=options)
                embed.add_field(name="Votes",value=resultsTally)
                embed.set_footer(text="Players that are in",ts=True)
                embed.post()

                ## ALL PLAYERS
                if answer == 1:
                    resultsTally = '|' + ':white_check_mark:' * allPlayersLog.count(1) + '\n|' + ':x:' * allPlayersLog.count(2) + '\n|' + ':x:' * allPlayersLog.count(3)
                elif answer == 2:
                    resultsTally = '|' + ':x:' * allPlayersLog.count(1) + '\n|' + ':white_check_mark:' * allPlayersLog.count(2) + '\n|' + ':x:' * allPlayersLog.count(3)
                elif answer == 3:
                    resultsTally = '|' + ':x:' * allPlayersLog.count(1) + '\n|' + ':x:' * allPlayersLog.count(2) + '\n|' + ':white_check_mark:' * allPlayersLog.count(3)
                embed = Webhook(discord_webhook_url, color = 320000)
                embed.add_field(name="Question Results",value=options)
                embed.add_field(name="Votes",value=resultsTally)
                embed.set_footer(text="All players",ts=True)
                embed.post()

                ## PLAYERS IN
                lifePlayers = []
                noLifePlayers = []
                for player in players.keys():
                    if players[player] == 1:
                        lifePlayers.append(player[:-5])
                    if players[player] == 0:
                        noLifePlayers.append(player[:-5])
                embed = Webhook(discord_webhook_url, color = 470000)
                    
                if len(lifePlayers) + len(noLifePlayers) > 0:
                    if len(lifePlayers) == 0:
                        msg = '\n'.join(noLifePlayers)
                    if len(lifePlayers) == 1:
                        msg = lifePlayers[0] + ' :heart:\n' + '\n'.join(noLifePlayers)
                    elif len(lifePlayers) > 1:
                        msg = ' :heart:\n'.join(lifePlayers) + ' :heart:\n' + '\n'.join(noLifePlayers)
                    embed.add_field(name="Players in",value=msg)
                else:
                    embed.add_field(name="Players in",value='No one!')
                embed.set_footer(ts=True)
                embed.post()

        if message.content.startswith('!endgame'):
            await client.delete_message(message)
            print('Final player scores:',players)
            winners = []
            for player in players.keys():
                if players[player] >= 0:
                    winners.append(player[:-5])
            if len(winners) > 0:
                prize = round(pot / len(winners),2)
                embed = Webhook(discord_webhook_url, color = 470000)
                embed.add_field(name="Winners :confetti_ball::trophy::moneybag:",value = (' ($' + str(prize) + ')\n').join(winners) + ' ($' + str(prize) + ')\n')
                embed.set_footer(ts=True)
                embed.post()
            else:
                embed = Webhook(discord_webhook_url, color = 123123)
                embed.add_field(name="Winners :confetti_ball::trophy::moneybag:",value = 'No one!')
                embed.set_footer(ts=True)
                embed.post()

            global statsDB
            statsDB = players
            global totalNum
            totalNum = questionNum - 1
            
            players = dict()
            active_reg = False
            questionNum = 1
            active_game = False
            current_game = 'No game'
            timer_length = 0
            pot = 0

        if message.content.startswith('!lb'):
            await client.delete_message(message)
            try:
                msg = ''
                maxScore = totalNum
                currentScore = totalNum
                while currentScore != -1:
                    for player in statsDB.keys():
                        if totalNum - (1 - statsDB[player])  == currentScore:
                            msg += player[:-5] + ' (' + str(currentScore) + '/' + str(maxScore) + ')\n'
                    currentScore -= 1
                embed = Webhook(discord_webhook_url, color = 470000)
                embed.add_field(name="Leaderboard :trophy:",value = msg)
                embed.set_footer(ts=True)
                embed.post()
            except:
                pass

        if message.content.startswith('s!wait1'):
            await client.delete_message(message)
            await client.send_message(message.channel,'.play https://www.youtube.com/watch?v=yVZ7g-EQzY8')

        if message.content.startswith('s!wait2'):
            await client.delete_message(message)
            await client.send_message(message.channel,'.play https://www.youtube.com/watch?v=sXdxe7uYKb8')

        if message.content.startswith('s!win'):
            await client.delete_message(message)
            await client.send_message(message.channel,'.play https://www.youtube.com/watch?v=CnFiJIgh1fE')

        if message.content.startswith('s!sav'):
            await client.delete_message(message)
            await client.send_message(message.channel,'.play https://www.youtube.com/watch?v=IR3kjhhlN-U')

        if message.content.startswith('s!gt'):
            await client.delete_message(message)
            await client.send_message(message.channel,'.play https://www.youtube.com/watch?v=3dSCuAu4ge4')

        if message.content.startswith('s!t'):
            await client.delete_message(message)
            await client.send_message(message.channel,'.play https://www.youtube.com/watch?v=DliUjhJcgs4')

        if message.content.startswith('s!q12'):
            await client.delete_message(message)
            await client.send_message(message.channel,'.play https://www.youtube.com/watch?v=oeVG8U35dAI')

        if message.content.startswith('s!info'):
            await client.delete_message(message)
            await client.send_message(message.channel,'.play https://www.youtube.com/watch?v=y6CuqdNY8PA&t=29s\n.seek 61')
                
    if message.content.startswith('!help'):
        msg = "Check out the #info channel and the #commands channel if you are a host for info and a list of commands."
        temp_msg = await client.send_message(message.channel, msg)
        await client.delete_message(temp_msg)        

    if message.content.startswith('!join'):
        if active_reg:
            players[str(message.author)] = (2 - questionNum)
            print(str(message.author)[:-5],'joined the game. Total count:',len(players.keys()))
            await client.delete_message(message)
            msg = 'Good luck {}, you are now registered for the game. There are currently {} players registered.'.format(str(message.author)[:-5],len(players.keys()))
            temp_msg = await client.send_message(message.channel, msg)
            await client.delete_message(temp_msg)
        else:
            await client.delete_message(message)
            msg = 'Sorry {}, game registration is **closed** right now!'.format(str(message.author)[:-5])
            temp_msg = await client.send_message(message.channel, msg)
            await client.delete_message(temp_msg)

    if message.content.startswith('1') or message.content.startswith('2') or message.content.startswith('3'):
        try:
            end = time.time()
            if end - start < timer_length:
                await client.delete_message(message)
            if (str(message.author) in alreadyAnswered) or (str(message.author) not in players.keys()):
                pass
            else:
                if end - start < timer_length:
                    ## TALLYS RESULTS
                    allPlayersLog.append(int(str(message.content[:])[0]))
                    alreadyAnswered.append(str(message.author))
                    if int(players[str(message.author)]) >= 0:
                        inPlayersLog.append(int(str(message.content[:])[0]))
                    
                    ## PROCESSES ANSWER
                    if int(str(message.content[:])[0]) == int(questionParts[-1]):
                        currentScore = int(players[str(message.author)])
                        print(f'{str(message.author)[:-5]} got it correct.')
                        if not(autowin) and questionNum == question_count:
                            players[str(message.author)] = currentScore + 2
                        else:
                            players[str(message.author)] = currentScore + 1
                    else:
                        print(f'{str(message.author)[:-5]} got it incorrect. They answered: {str(message.content[:])[0]}')

                ## LATE ANSWER
                elif end - start > timer_length:
                    msg = 'Sorry {}, you were late! :clock10:'.format(str(message.author)[:-5])
                    temp_msg = await client.send_message(message.channel, msg)
                    await client.delete_message(temp_msg)
        except:
            pass

    if message.content.startswith('!t'):
        await client.delete_message(message)
        try:
            timerTime = time.time()
            if (timerTime - start) < timer_length:
                testStart = time.time()
                msg = '**{} seconds left!** :clock10:'.format(round(timer_length - (timerTime - start), 1))
                await client.send_message(message.channel, msg)
            if (timerTime - start) > timer_length:
                msg = '**Time is up!** :alarm_clock:'
                await client.send_message(message.channel, msg)
        except:
            pass

    if message.content.startswith('!myscore'):
        try:
            finalScore = statsDB[str(message.author)]
            finalScore = totalNum - (1 - finalScore)
            if finalScore != 1:
                msg = f"{str(message.author)[:-5]}, you answered **{finalScore} questions** correctly!"
            else:
                msg = f"{str(message.author)[:-5]}, you answered **1 question** correctly!"
            await client.send_message(message.channel, msg)
        except:
            pass

@client.event
async def on_ready():
    print('Logged in as:',client.user.name)
    print('-------------------------------')

client.run(input('Enter Discord bot token: '))
