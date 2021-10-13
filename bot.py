__Filename__ = 'bot'
__Creationdate__ = '09/10/2021'

from discord import *
import discord
from discord import File
from discord.ext import commands
from constants import *

# command prefix users will use to make requests.
bot = commands.Bot(command_prefix='!')


# Run when the bot is connected.
@bot.event
async def on_ready():
    print("Bot ready")
    await bot.change_presence(status=discord.Status.online,
                              activity=discord.Game(""))


# get command.
@bot.command(pass_context=True)
async def get(ctx, subject_name, theme, content_type, difficulty=1, year=0):
    """Command to get any exercises or test which is in the database :
    - subject_name must begins by 'm', 'p', 'c' or 'i'.
    - theme must be in the database.
    - content_type must begins by 'e' or 'd'.
    - 1 <= difficulty <= 5.
    - 1 <= year <= 3."""

    # Object related to the author of the request.
    author_object = ctx.message.author
    for author_role in author_object.roles:
        # We found the year role => the user is in the license.
        if author_role.id == YEAR_ROLE_ID:
            # Year's position in the role's name ("L1", "L2," "L3").
            year = int(author_role.name[1])

    # Year is not specified and has not been found in roles.
    if year == 0:
        await ctx.send(f"Error : {author_object.name}"
                       f" you are not anymore in the license so you must specify a year.")

    # Difficulty given > 5.
    if difficulty > 5:
        await ctx.send(f"{author_object.mention} : maximum difficulty is 5.\n"
                       f"We all know you are smart af stop showing off.")
        difficulty = 5

    # Difficulty given < 1.
    elif difficulty < 1:
        await ctx.send(f"{author_object.mention} : minimum difficulty is 1.\n"
                       f"Come on don't underestimate yourself.")
        difficulty = 1

    # subject_name doesn't begin by 'm', 'p', 'c' or 'i'.
    if not subject_name[0].lower() in tuple_subjects:
        await ctx.send("I only know MPCI subjects.")
        return

    else:
        pass


# help command
@bot.command()
async def help_commands(ctx):
    await ctx.send("Available commands :\n"
                   "- !get subject theme content_type(exo, ds) difficulty "
                   "year(only if you are not in the license anymore)\n"
                   "- !html : let him tell you his opinion about it.")


@bot.command()
async def html(ctx):
    await ctx.send("HTML is not a programming language.")


@get.error
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("- !get subject theme content_type(exo, ds) difficulty "
                       "year(only if you are not in the license anymore)")


print("Preparing bot...")

# Bot's token.
jeton = ""

# Run the bot on the server.
bot.run(jeton)
