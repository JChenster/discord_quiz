import discord
from discord.ext import commands
from dhooks import Webhook, Embed
from string import ascii_uppercase as UPPERCASE_LETTERS
import time
from quizgame import QuizGame
from question import Question
from visuals import optionsVisual, resultsVisual
# This is where the constants for my private instance of running this bot in my server are stored
# To run your own version, use your own constants file as modelled by template
# import privateconstants as constants
import constants

bot = commands.Bot(command_prefix='!')
# Global variable representing the quiz game currently occuring
quiz = QuizGame()
hook = Webhook(constants.CHANNEL_WEBHOOK_URL)

# Colors for embed messages for question/answer/leaderboard can be adjusted here
QUESTION_EMBED_COLOR = 0x5c81f0
ANSWER_EMBED_COLOR = 0x1DF183
LEADERBOARD_EMBED_COLOR = 0xE6F31B

MIN_OPTIONS = 2
MAX_OPTIONS = len(UPPERCASE_LETTERS)

@bot.event
async def on_ready():
    print('-' * 75)
    print(f'Logged in as {bot.user.name} with ID: {bot.user.id}')
    print('-' * 75)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)

    if not quiz.isActiveGame():
        return
    
    channel = message.channel
    answer_range = list(UPPERCASE_LETTERS[:quiz.getNumOptions()].lower())
    input_answer = message.content.strip().lower()
    player = message.author

    # Process answers
    if input_answer in answer_range:
        # Player has no joined the game registration
        if not quiz.checkPlayer(player):
            await channel.send(f"{player}, you have not joined the game yet! Type `!join` to join if registration is still open")
        elif time.time() - quiz.getQuestionStart() > quiz.getQuestionTimer():
            await channel.send(f"Sorry {player}, your answer is not within the response window! :clock10:")
        else:
            quiz.updateAnswerLog(player, input_answer)

# Allows a user to check to see if they have the approprtiate host role or not 
@bot.command()
async def checkhost(ctx):
    host_role = discord.utils.find(lambda r: r.name == constants.HOST_ROLE, ctx.message.guild.roles)
    if host_role in ctx.message.author.roles:
        await ctx.send("You have the appropriate host role!")
    else:
        await ctx.send("You do not have the appropriate host role.")
    
@bot.command()
async def checkgame(ctx):
    await ctx.send("A game is **active!**" if quiz.isActiveGame() else "No game is active!")

@bot.command()
async def checkplayers(ctx):
    if not quiz.isActiveGame():
        await ctx.send("There is no active game")
    else:
        await ctx.send(f"Players playing right now: {', '.join(map(str, quiz.getPlayers().keys()))}")

# Check the timer for how much time is left in a question
@bot.command()
async def t(ctx):
    if not quiz.isActiveGame():
        await ctx.send("There is no active game")
        return
    cur_time = time.time()
    start, timer_length = quiz.getQuestionStart(), quiz.getQuestionTimer()
    if cur_time - start < timer_length:
        await ctx.send(f'**{round(timer_length - (cur_time - start), 1)} seconds left!** :clock10:')
    else:
        await ctx.send('**Time is up!** :alarm_clock:')

@bot.command()
async def join(ctx):
    if not quiz.isActiveGame():
        await ctx.send("There is no active game to join")
    elif not quiz.isActiveRegistration():
        await ctx.send("Sorry but registration isn't active/has ended!")
    elif quiz.addPlayer(ctx.message.author):
        await ctx.send("Join was successful! Happy playing")
    else:
        await ctx.send("You've already joined!")

# Host-specific functions for hosting a quiz game

# Helper function to create Question objects that are then added to QuizGame
async def getQuestionInputs(ctx, num_questions) -> None:
    num_options = quiz.getNumOptions()
    await ctx.send(f'Now, enter **{num_questions} questions** each with **{num_options} options**, one at a time.')
    option_prompt = "/".join([f"<option {l}>" for l in UPPERCASE_LETTERS[:num_options]])
    await ctx.send(f'Types questions in this format: `<question>/{option_prompt}/<correct letter answer choice>`')

    for question_num in range(1, num_questions + 1):
        await ctx.send(f'You are now entering **Question {question_num}**')
        while True:
            question_input = (await bot.wait_for("message", check = lambda m: m.author == ctx.author)).content
            try:
                question = Question(question_input, num_options)
                quiz.addQuestion(question)
                await ctx.send(f'Question {question_num} successfully entered!')
                break
            except:
                await ctx.send("That's an invalid question. Try again! Make sure to follow the syntax and the answer is an appropriate letter choice.")

# Enter quiz questions in a private channel to prevent players from seeing the game and question set up
@bot.command()
@commands.has_role(constants.HOST_ROLE)
async def startgame(ctx):
    if quiz.isActiveGame():
        await ctx.send("Hold on. There is currently a game occuring right now or someone else is setting up a game. Wait until it is finished.")
        return
    quiz.setActiveGame()
    await ctx.send('**Registration started!** Try to enter all the information correctly. If you mess something up, you have to **follow through** and cancel all at the end and restart.')

    while True:
        await ctx.send('Now please enter how many questions you want.')
        num_questions = (await bot.wait_for("message", check = lambda m: m.author == ctx.author)).content
        await ctx.send('Enter how many options you want for each question.')
        num_options = (await bot.wait_for("message", check = lambda m: m.author == ctx.author)).content
        await ctx.send('Enter how many seconds you want the timer for each question to be')
        question_timer = (await bot.wait_for("message", check = lambda m: m.author == ctx.author)).content
        try:
            num_questions = int(num_questions)
            num_options = int(num_options)
            question_timer = float(question_timer)
            if num_questions < 1 or num_options < MIN_OPTIONS or num_options > MAX_OPTIONS or question_timer < 0:
                raise ValueError()
            quiz.setNumQuestions(num_questions)
            quiz.setNumOptions(num_options)
            quiz.setQuestionTimer(question_timer)
            break
        except:
            await ctx.send('Something went wrong. Number of questions and question timer must be greater than 0 and number of options be between 2 and 26. Make sure to type in an integer for each input and nothing else. Try again.')

    await getQuestionInputs(ctx, num_questions)
    await ctx.send('Questions entered. Type `cancel` at this point if you wish to cancel. Otherwise, type anything that is not `cancel` to finish game registration.')
    cancel_flag = (await bot.wait_for("message", check = lambda m: m.author == ctx.author)).content.strip().lower()
    if cancel_flag == "cancel":
        quiz.resetQuizGame()
        await ctx.send('Quiz set up cancelled! Do **!startgame** to try again.')
    else:
        await ctx.send(f"Quiz has been all set up! Thank you {ctx.message.author.name}")

@bot.command()
@commands.has_role(constants.HOST_ROLE)
async def startreg(ctx):
    if not quiz.isActiveGame():
        await ctx.send("Game not active to start registration for.")
        return
    quiz.setActiveRegistration()
    await ctx.send('Game Registration Started! Type **!join** to join the game.')

@bot.command()
@commands.has_role(constants.HOST_ROLE)
async def endreg(ctx):
    if not quiz.isActiveRegistration():
        await ctx.send("No active registration to end.")
        return
    quiz.endActiveRegistration()
    await ctx.send('Game Registration Ended!')

@bot.command()
@commands.has_role(constants.HOST_ROLE)
async def question(ctx):
    # Lots of error handling for bad timing of using this command
    if not quiz.isActiveGame():
        await ctx.send("Can't show question if no game is active")
        return
    if quiz.getCurQuestionNum() != quiz.getCurResultNum():
        await ctx.send("You can't move on to next question until you display results of last question using `!result`")
    cur_question = quiz.getNextQuestion()
    if cur_question is None:
        await ctx.send("All the questions have been shown! Type `!endgame` to end the game")
        return
    # Send the question to webhook
    embed = Embed(color = QUESTION_EMBED_COLOR)
    embed.set_author(name = "Discord Quiz Question")
    embed.add_field(name = f"{quiz.getCurQuestionNum() + 1}. {cur_question.getQuestion()}", value = optionsVisual(quiz))
    hook.send(embed = embed)
    quiz.setQuestionStart()

@bot.command()
@commands.has_role(constants.HOST_ROLE)
async def result(ctx):
    # Lots of error handling for bad timing of using this command
    if not quiz.isActiveGame():
        await ctx.send("Can't show results for a question if no game is active!")
        return
    if time.time() - quiz.getQuestionStart() < quiz.getQuestionTimer():
        await ctx.send("Question period has no ended!")
        return
    if quiz.getCurQuestionNum() != quiz.getCurResultNum() + 1:
        await ctx.send("You must display a question before showing its answer")
        return
    results = quiz.processResults()
    cur_question = quiz.getCurQuestion()
    if results is None:
        await ctx.send("All the answers have been shown! Type `!endgame` to end the game")
        return
    # Send the results to webhook
    embed = Embed(color = ANSWER_EMBED_COLOR)
    embed.set_author(name = "Discord Quiz Answer")
    embed.add_field(name = f"{quiz.getCurQuestionNum() + 1}. {cur_question.getQuestion()}", value = optionsVisual(quiz))
    embed.add_field(name = "Votes", value = resultsVisual(quiz, results))
    hook.send(embed = embed)

@bot.command()
@commands.has_role(constants.HOST_ROLE)
async def endgame(ctx):
    if not quiz.isActiveGame():
        await ctx.send("Can't end a game that is not active")
        return
    # Make sure that the result for every question that has been asked has been shown so far
    if quiz.getCurQuestionNum() != quiz.getCurResultNum():
        await ctx.send("Show the results of this question before ending the game.")
        return
    # Displays a visualization of the results of a game
    # Shows a player and how many questions they answered correctly, sorted by those who answered the most correctly
    leaderboard = dict(sorted(quiz.getPlayers().items(), key = lambda item: item[1], reverse = True))
    embed = Embed(color = LEADERBOARD_EMBED_COLOR)
    embed.set_author(name = "Discord Quiz Game Results")
    embed.add_field(name = "Players", value = "\n".join(map(lambda p: f"{':trophy:' if leaderboard[p] == max(leaderboard.values()) else ''} {p}", leaderboard.keys())))
    embed.add_field(name = "Points", value = "\n".join(map(str, leaderboard.values())))
    hook.send(embed = embed)

bot.run(constants.TOKEN)