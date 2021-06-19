import discord
from discord.ext import commands
from quizgame import QuizGame
from question import Question
from dhooks import Webhook, Embed
from string import ascii_uppercase as UPPERCASE_LETTERS
# This is where the constants for my private instance of running this bot in my server are stored
# To run your own version, use your own constants file as modelled by template
import privateconstants as constants

bot = commands.Bot(command_prefix='!')
# Global variable representing the quiz game currently occuring
quiz = QuizGame()

hook = Webhook(constants.CHANNEL_WEBHOOK_URL)
QUESTION_EMBED_COLOR = 0x5c81f0

@bot.event
async def on_ready():
    print('-' * 75)
    print(f'Logged in as {bot.user.name} with ID: {bot.user.id}')
    print('-' * 75)

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
        await ctx.send('Enter the prize you want for this quiz')
        prize = (await bot.wait_for("message", check = lambda m: m.author == ctx.author)).content
        await ctx.send('Enter how long you want the timer for each question to be')
        question_timer = (await bot.wait_for("message", check = lambda m: m.author == ctx.author)).content
        try:
            num_questions = int(num_questions)
            num_options = int(num_options)
            prize = float(prize)
            question_timer = float(question_timer)
            if num_questions < 1 or num_options < 2 or num_options > 26 or prize < 0 or question_timer < 0:
                raise ValueError()
            quiz.setNumQuestions(num_questions)
            quiz.setNumOptions(num_options)
            quiz.setPrize(prize)
            quiz.setQuestionTimer(question_timer)
            await ctx.send(f'The prize for this game was set as **${prize}** and the timer for each question as **{question_timer} seconds**')
            break
        except:
            await ctx.send('Something went wrong. Number of questions, prize, and question timer must be greater than 0 and number of options be between 2 and 26. Make sure to type in an integer for each input and nothing else. Try again.')

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
    await ctx.send('Game Registration Started! Type **!join** to join the game. :dollar::money_mouth::smile:')

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
        await ctx.send("All the questions have been shown! Type `!endgame` to end the game and show the results")
        return
    else:
        # Send the question to webhook
        embed = Embed(color = QUESTION_EMBED_COLOR)
        embed.set_author(name = "Discord Quiz")
        options = "\n".join([f"{l}) {o}" for l, o in zip(UPPERCASE_LETTERS[:quiz.getNumOptions()], cur_question.getOptions())])
        embed.add_field(name = f"{quiz.getCurQuestionNum() + 1}. {cur_question.getQuestion()}", value = options)
        hook.send(embed = embed)
        quiz.setQuestionStart()

bot.run(constants.TOKEN)