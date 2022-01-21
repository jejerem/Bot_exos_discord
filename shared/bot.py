__Creationdate__ = '09/10/2021'

# External libraries
import asyncio

import discord
from discord.ext import commands
import firebase_admin
from firebase_admin import firestore, credentials
import pyrebase
# Built-in
# Project files
from shared.db_related.firebase_storage_db import FirestoreStorage
from private_files.private_constants import *
from shared.discord_related.context_actions import ContextActions
from shared.discord_related.user_arguments import UserArguments

# command prefix users will use to make requests.
bot = commands.Bot(command_prefix='!', help_command=None)


# Run when the bot is connected.
@bot.event
async def on_ready():
    print("Bot ready")
    await bot.change_presence(status=discord.Status.online,
                              activity=discord.Game("Giving exercises"))

    # We first initialize the Cloud.
    cred = credentials.Certificate("private_files/serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

    # Then we initialize the storage part.

    firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
    db = firestore.client()
    storage = firebase.storage()
    global firestore_storage
    firestore_storage = FirestoreStorage(storage, db)


# get command.
@bot.command()
async def get(ctx, *infos):
    """Command to get any exercises or test which is in the database :
    - infos (tuple):
        - ("user_path(user_subject/user_topic/user_content_type/difficulty/name)"
        - subject name should be in the subjects of the dictionary associated with the year.
        - theme must be in the database.
        - content_type must begin by 'e'(exercise) or ('d'(ds) or 't'(test)).
        - 0 <= difficulty <= 5. (0 is when we want to not consider it in the queries).
        - 0 <= year <= 3. (if specified must be first information)
    """

    ContextActions.set_ctx(ctx)
    user_arguments = UserArguments()
    await user_arguments.store_year(infos[0])

    for info in infos:
        await user_arguments.store_arguments(info)

        # We make our path according to the arguments we stored.
        firestore_path = user_arguments.get_firestore_path()
        difficulty = user_arguments.dic_arguments["difficulty"]
        topic = user_arguments.dic_arguments["topic"]
        filename = ""
        if "filename" in user_arguments.dic_arguments:
            filename = user_arguments.dic_arguments["filename"]
        data, filename = await firestore_storage.choose_get_file(firestore_path, topic, difficulty, filename)
        await ctx.send(file=discord.File(data, filename))

        """await ContextActions.send_message(f"Year : {user_arguments.dic_arguments['year']}"
                                          f"\nnearest subject : {user_arguments.dic_arguments['subject']}."
                                          f"\nnearest topic : {user_arguments.dic_arguments['topic']}."
                                          f"\nnearest content type : {user_arguments.dic_arguments['content_type']}.")"""


# test command.
@bot.command()
async def test(ctx):
    """ref = firestore_storage.db.collection("degrees/l1/maths/files/exercises").where("storage_path", ">", "").get()[0]
    filename = ref.to_dict()["storage_path"].split("/")[-1]
    url = firestore_storage.storage.child(ref.to_dict()['storage_path']).get_url(None)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return await ctx.send('Could not download file...')
            data = io.BytesIO(await resp.read())
            await ctx.send(file=discord.File(data, filename))"""
    # print(ctx.message.attachments[0].size)


# add command.
@bot.command()
async def add(ctx, *infos):
    """add documents with discord's attachments feature
    if path is empty [first argument]:
     - infos (tuple):
        path (if all attachments don't go to same path) :
        for each attachment : "path(ex : maths/topic/exercises/difficulty)"
    - is_path_specified : if both attachments list and infos tuple have the same length => False
                          if there is one more info element than attachments => True
    - rules :
        - document must be a pdf 'application/pdf' (with 'attachment.content_type').
        - size must not exceed 1Mo. (with 'attachment.size').
    """

    ContextActions.set_ctx(ctx)
    user_arguments = UserArguments()
    await user_arguments.store_year(infos[0])

    list_attachments = ctx.message.attachments
    is_general_path_specified = False
    general_path = ""

    if len(infos) == 1:
        # We consider general path is specified
        is_general_path_specified = True
        general_path = infos[0]

    if len(list_attachments) > len(list_attachments):
        await ContextActions.send_mention_message("you need to specify information for each attachment.")

    if is_general_path_specified:
        await user_arguments.store_arguments(general_path)
        firestore_path = user_arguments.get_firestore_path()
        for attachment in ctx.message.attachments:
            difficulty = user_arguments.dic_arguments["difficulty"]
            topic = user_arguments.dic_arguments["topic"]
            await firestore_storage.add_attachment_storage_db(firestore_path, attachment,
                                                              difficulty=difficulty, topic=topic)
    else:
        # Iterate both attachments and information related to these last ones.
        for attachment, info in zip(ctx.message.attachments, infos):
            await user_arguments.store_arguments(info)
            firestore_path = user_arguments.get_firestore_path()

            if "difficulty" not in user_arguments.dic_arguments or "topic" not in user_arguments.dic_arguments:
                return

            difficulty = user_arguments.dic_arguments["difficulty"]
            topic = user_arguments.dic_arguments["topic"]
            asyncio.create_task(firestore_storage.add_attachment_storage_db(firestore_path, attachment,
                                                              difficulty=difficulty, topic=topic))


@bot.command()
async def remove(ctx, *infos):
    """remove documents from database.
        path : subject/topic/content_type/filename
        """
    ContextActions.set_ctx(ctx)
    user_arguments = UserArguments()
    for info in infos:
        await user_arguments.store_arguments(info)
        firestore_path = user_arguments.get_firestore_path()
        filename = user_arguments.dic_arguments["filename"]
        firestore_storage.del_file_storage_db(firestore_path)



# help command.
@bot.command()
async def help(ctx):
    await ctx.send(f"""```Available commands :
                   - !get content_type(exo, ds/test) subject topic difficulty
                   year(by default it's ur degree(role))
                   
                   - !html : let him tell you his opinion about it.```""")


@bot.command()
async def html(ctx):
    await ctx.send("__**HTML**__ is **not** a **programming language**.")


@get.error
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("""- !get subject theme content_type(exo, ds) difficulty "
                       "year(only if you are not in the license anymore)""")


print("Preparing bot...")

# Run the bot on the server.
bot.run(BOT_TOKEN)
