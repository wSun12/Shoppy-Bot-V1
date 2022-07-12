import os
import discord
import random
import logging
import datetime
import psutil
import time
import platform
from utils.ids import(
    GuildIDs,
    CategoryIDs,
    ChannelIDs,
    UserIDs,
)
from utils.options import Options
from discord.ext import commands, tasks


intents = discord.Intents.all()
bot = commands.Bot(command_prefix='.', intents=intents)
allowed_mentions = discord.AllowedMentions(everyone = True)
bot.version_number = "2.0.1"

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
"""
#these are up top because i need them in both on message and on reaction
storecount = 0
storeincrement = 0
stackstore = []
"""
#self.bot = bot


@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.idle, activity=discord.Game('with their tail'))
    print('Corgibot Ready!')
"""
self.bot = bot
bot.cleanup.start()
print('init successful')
"""
@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

@bot.command()
async def clear(ctx, amount=5):
    await ctx.channel.purge(limit=amount)

@bot.command(aliases=['8ball'])
async def _8ball(ctx, *, question):
    responses = ['It is Certain.',
                'It is decidedly so.',
                'Without a doubt.',
                'Yes definitely.',
                'You may rely on it.',
                'As I see it, yes.',
                'Most likely.',
                'Outlook good.',
                'Yes.',
                'Signs point to yes.',
                'Reply hazy, try again.',
                'Ask again later.',
                'Better not tell you now.',
                'Cannot predict now.',
                'Concentrate and ask again.',
                "Don't count on it.",
                'My reply is no.',
                'My sources say no.',
                'Outlook not so good.',
                'Very doubtful.']
    await ctx.send(f'Question: {question}\nAnswer: {random.choice(responses)}')

#audit command
@bot.command()
async def audit(ctx):
    async with ctx.typing():
        guild = bot.get_guild(GuildIDs.LG_SHOPPING)
        for cat, channels in guild.by_category():
            if cat.id == CategoryIDs.SHOPPING: #shopping
                for channel in channels:
                    print('currently auditing:')
                    print(channel.name)
                    print('-----')
                    async for message in channel.history(limit=200):
                        #only activates these if no embed is found
                        if message.embeds == []:
                            await message.clear_reactions() #clears out all the old reactions
                            await message.add_reaction('✅')
                            if channel.id == ChannelIDs.LATER: #later
                                await message.add_reaction('⏭️')
                                    #prompt to move to other channels
                            else:
                                await message.add_reaction('⏮️')
                                #prompt to move back to later
                        #cleans up embeds so i don't have to do it manually
                        else:
                            await message.delete()

        await ctx.send('Audit of shopping lists complete!')
        print('audit complete')


#list command
@bot.command()
async def list(ctx):
    #space to comment out
    guild = bot.get_guild(GuildIDs.LG_SHOPPING) #our server
    channel = bot.get_channel(ChannelIDs.GROCERY_LIST) #grocery list
    async for message in channel.history(limit=20): #deletes grocery list
        await message.delete()

    for cat, channels in guild.by_category():
        if cat.id == CategoryIDs.SHOPPING: #shopping category
            for channel in channels:
                print('currently listing:')
                print(channel.name)
                stack=[]
                async for message in channel.history(limit=200):
                    content = message.content
                    stack.append(content)
                    stack.append('\n')
                msg = ''.join([str(i) for i in stack])
                print(msg)
                embed = discord.Embed(
                    title=channel,
                    description=msg,
                    color=discord.Color.orange(),
                    )
                channel = bot.get_channel(ChannelIDs.GROCERY_LIST) #grocery list
                await channel.send(
                embed = embed,
                    )


    await ctx.send('Here is your grocery list!')

@bot.command()
async def old(ctx):
    counter = 0
    guild = bot.get_guild(GuildIDs.LG_SHOPPING)
    channel = bot.get_channel(ChannelIDs.PURCHASED)
    today = datetime.date.today()
    #print(today)
    cutoff = datetime.timedelta(days=Options.AUTO_DELETE_AGE)
    async for message in channel.history(limit=200): #reads messages
        msgdate = message.created_at
        msgdate = datetime.datetime.date(msgdate)
        age = today-msgdate
        if age > cutoff:
            await message.delete()
            counter = counter+1
    await ctx.send(str(counter)+' old items deleted from '+channel.mention)

@bot.command()
async def daily(ctx):
    await ctx.invoke(bot.get_command('old'))
    await ctx.invoke(bot.get_command('audit'))
    await ctx.invoke(bot.get_command('list'))

@bot.command(aliases=["botstats"])
async def stats(ctx):
    """
    Statistics and information about this bot.
    """
    proc = psutil.Process(os.getpid())
    uptime_seconds = time.time() - proc.create_time()

    # they return byte values but we want gigabytes
    ram_used = round(psutil.virtual_memory()[3] / (1024 * 1024 * 1024), 2)
    ram_total = round(psutil.virtual_memory()[0] / (1024 * 1024 * 1024), 2)
    ram_percent = round((ram_used / ram_total) * 100, 1)
    """maybe add macros someday
    with open(r"./json/macros.json", "r") as f:
        macros = json.load(f)
        """
    embed = discord.Embed(
        title="Corgibot Stats",
        color=discord.Color.orange(),
        url="https://github.com/Gwoods2/Corgibot",
    )
    embed.add_field(name="Servers:", value=len(bot.guilds), inline=True)
    embed.add_field(
        name="Total Users:", value=len(set(bot.get_all_members())), inline=True
    )
    embed.add_field(
        name="Number of Commands:",
        value=f"{len(bot.commands)} (Events: {len(bot.extra_events)})",
    ) #add "+ len(macros)" after commands when i have some

    embed.add_field(name="Bot Version:", value=bot.version_number, inline=True)
    embed.add_field(
        name="Python Version:", value=platform.python_version(), inline=True
    )
    embed.add_field(
        name="discord.py Version:", value=discord.__version__, inline=True
    )

    embed.add_field(
        name="CPU Usage:",
        value=f"{psutil.cpu_percent(interval=None)}%",
        inline=True,
    )
    embed.add_field(
        name="RAM Usage:",
        value=f"{ram_used}GB/{ram_total}GB ({ram_percent}%)",
        inline=True,
    )
    embed.add_field(
        name="Uptime:",
        value=str(datetime.timedelta(seconds=uptime_seconds)).split(".")[0],
        inline=True,
    )

    embed.set_footer(text="Creator: Scrooge#0562, hosted on: AWS")
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    await ctx.send(embed=embed)

#what to do when a person reacts
@bot.event
async def on_raw_reaction_add(payload):
    userid = payload.user_id
    #print(userid)
    #if user.bot:
    if userid == UserIDs.SELF: #won't do events if corgibot is the one reacting
        return

    id = int(payload.message_id)

    userid = payload.user_id

    channel = bot.get_channel(payload.channel_id)
    message = await channel.fetch_message(id)
    #print(message)
    if message.embeds == []: #only copy whole contents if not an embed
        content = message.content
        #print(content)
    #else:
        #content = embed.title
        #print(content)

    if payload.emoji.name == '✅': #move to purchased
        if payload.channel_id != ChannelIDs.PURCHASED:
            channel = bot.get_channel(ChannelIDs.PURCHASED)
            await channel.send(content)
            #workaround to delete the message, needed after adding forward
            channel = bot.get_channel(payload.channel_id)
            #print(channel.name)
            message = await channel.fetch_message(payload.message_id)
            #print(message.content)
        await message.delete()
        return

    if payload.emoji.name == '⏮️': #move to later
        if payload.channel_id != ChannelIDs.LATER:
            channel = bot.get_channel(ChannelIDs.LATER)
            await channel.send(content)
            channel = bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
        await message.delete()
        return

    if payload.emoji.name == '⏭️': #embed to send places
        stackstore = []
        storecount = 0
        storeincrement = 0
        storenumber = 0
        #stackemoji = []
        #fullstack = []
        #numberstore = ''
        guild = bot.get_guild(GuildIDs.LG_SHOPPING)
        for cat, channels in guild.by_category():
            if cat.id == CategoryIDs.SHOPPING: #shopping category
                for channel in channels:
        #for channel in CategoryIDs.SHOPPING:
                    if channel.id != ChannelIDs.LATER:
                        if channel.id != ChannelIDs.PURCHASED:

                            stackstore.append(channel.name)
                            storecount = storecount + 1
                            #print(storecount)
                            #print(stackstore)
        #sets up the referenced message to refer to later
        referenced = payload.message_id #do  i need this?
        #print(referenced)
        #sets up the embed
        embed = discord.Embed(
            title=content,
            color=discord.Color.orange(),
            #fields= [
            #{ name:name, value:value}
            #]
            )
        #opens the counting digits file
        #with open(r'./files/countingdigits.txt') as f:
            #for line in f:
            #    line = line.replace("\r", "").replace("\n", "")
            #alternates adding numbers and
        for x in stackstore:
            storenumber=storenumber+1
            numberstore = str(storenumber)
            #print(numberstore)
            embed.add_field(name="** **", value=numberstore+". "+x, inline=True)
            #print(x)
            #fullstack.append(f.readline())
            #fullstack.append(x)
            #fullstack.append('\n')
            #fullstack.append(f.readline()+':'+x+'\n')
            #print(fullstack)

        #embed.add_field(name='name', value='value', inline=true)
        #embed.add_field(name="** **", value=fullstack, inline=False)
        #print(fullstack)
        await message.reply(
        embed = embed,
        delete_after = 60
        #message = message
        )
        #routes reactions to the new embed
        #message = await channel.fetch_message(channel.last_message_id)
        #reacts to the embed with the emoji
        #with open(r'./files/countingemoji.txt') as g:
        """
        for x in stackstore:
            #reaction = g.readline()
            print(x)
            storeincrement=storeincrement+1
            if storeincrement == 1:
                await message.add_reaction('1️⃣') #try to add 1
        """

        return
    #sets up the list of store count emoji
    if [
    payload.emoji.name == '1️⃣' or
    payload.emoji.name == '2️⃣' or
    payload.emoji.name == '3️⃣' or
    payload.emoji.name == '4️⃣' or
    payload.emoji.name == '5️⃣' or
    payload.emoji.name == '6️⃣' or
    payload.emoji.name == '7️⃣' or
    payload.emoji.name == '8️⃣' or
    payload.emoji.name == '9️⃣' or
    payload.emoji.name == '0️⃣']:
        #a bunch of checks that can be commented out
        #print('payload emoji was a number') #tests whether the if statement worked
        messageid = payload.message_id
        #print('embed message id is '+str(messageid)) #check
        embedmes = await channel.fetch_message(payload.message_id)
        #print('embed message fetched')
        #print('embed message is '+str(embedmes)) #check
        #print('embed message embed is '+str(embedmes.embeds))
        referencedmes = message.reference
        #print('referencedmes 1: '+str(referencedmes))
        referencedmes = await channel.fetch_message(referencedmes.message_id)
        #print('referenced message is '+str(referencedmes)) #check
        #print('referenced message text is '+str(referencedmes.content)) #check
        #print(content)

        #delivers message content to correct channel
        storecount = 0
        guild = bot.get_guild(GuildIDs.LG_SHOPPING)
        for cat, channels in guild.by_category():
            if cat.id == CategoryIDs.SHOPPING: #shopping category
                for channel in channels:
                    #skips later and purchased
                    if channel.id != ChannelIDs.LATER:
                        if channel.id != ChannelIDs.PURCHASED:
                            #checks for internal mechanisms
                            #print('channel is '+str(channel)) #check
                            storecount = storecount + 1
                            #print('storecount is '+str(storecount))

                            #the logic for which list
                            if payload.emoji.name == '1️⃣':
                                if storecount == 1:
                                    #print('sending to '+str(channel)) #check
                                    #send to new channel
                                    await channel.send(referencedmes.content)
                                    #deletes embed message
                                    #await message.delete()
                                    #change channel back to later?
                                    channel = bot.get_channel(ChannelIDs.LATER)
                                    #print('now on #later')
                                    #print('channel name is '+str(channel.name))
                                    #print('channel id is '+str(channel.id))
                                    #delete both messages
                                    await channel.delete_messages([
                                    embedmes, referencedmes
                                    ])
                                    return
                            if payload.emoji.name == '2️⃣':
                                if storecount == 2:
                                    await channel.send(referencedmes.content)
                                    channel = bot.get_channel(ChannelIDs.LATER)
                                    await channel.delete_messages([
                                    embedmes, referencedmes
                                    ])
                                    return
                            if payload.emoji.name == '3️⃣':
                                if storecount == 3:
                                    await channel.send(referencedmes.content)
                                    channel = bot.get_channel(ChannelIDs.LATER)
                                    await channel.delete_messages([
                                    embedmes, referencedmes
                                    ])
                                    return
                            if payload.emoji.name == '4️⃣':
                                if storecount == 4:
                                    await channel.send(referencedmes.content)
                                    channel = bot.get_channel(ChannelIDs.LATER)
                                    await channel.delete_messages([
                                    embedmes, referencedmes
                                    ])
                                    return
                            if payload.emoji.name == '5️⃣':
                                if storecount == 5:
                                    await channel.send(referencedmes.content)
                                    channel = bot.get_channel(ChannelIDs.LATER)
                                    await channel.delete_messages([
                                    embedmes, referencedmes
                                    ])
                                    return
                            if payload.emoji.name == '6️⃣':
                                if storecount == 6:
                                    await channel.send(referencedmes.content)
                                    channel = bot.get_channel(ChannelIDs.LATER)
                                    await channel.delete_messages([
                                    embedmes, referencedmes
                                    ])
                                    return
                            if payload.emoji.name == '7️⃣':
                                if storecount == 7:
                                    await channel.send(referencedmes.content)
                                    channel = bot.get_channel(ChannelIDs.LATER)
                                    await channel.delete_messages([
                                    embedmes, referencedmes
                                    ])
                                    return
                            if payload.emoji.name == '8️⃣':
                                if storecount == 8:
                                    await channel.send(referencedmes.content)
                                    channel = bot.get_channel(ChannelIDs.LATER)
                                    await channel.delete_messages([
                                    embedmes, referencedmes
                                    ])
                                    return
                            if payload.emoji.name == '9️⃣':
                                if storecount == 9:
                                    await channel.send(referencedmes.content)
                                    channel = bot.get_channel(ChannelIDs.LATER)
                                    await channel.delete_messages([
                                    embedmes, referencedmes
                                    ])
                                    return
                            if payload.emoji.name == '0️⃣':
                                if storecount == 10:
                                    await channel.send(referencedmes.content)
                                    channel = bot.get_channel(ChannelIDs.LATER)
                                    await channel.delete_messages([
                                    embedmes, referencedmes
                                    ])
                                    return




        #return #skips deleting the embed while i test

    #await channel.fetch_message(id)
    #await message.delete()
    #await channel.delete_messages(id)

#add reactions to messages
@bot.event
async def on_message(message):
    category = str(message.channel.category)
    channel = str(message.channel)
    if category == "shopping":
        #only activates these if no embed is found
        if message.embeds == []:
            await message.add_reaction('✅')
            if channel == 'later':
                await message.add_reaction('⏭️') #prompt to embed
            else:
                await message.add_reaction('⏮️') #prompt to later
        #activates this with embeds
        else:
            #print('else') #check
            if channel == 'later':
                #print('later') #check
                #print(stackstore)
                stackstore = []
                storecount = 0
                storeincrement = 0
                #storenumber = 0
                #stackemoji = []
                #fullstack = []
                #numberstore = ''
                #copied from on react, because it wouldn't work without this
                guild = bot.get_guild(GuildIDs.LG_SHOPPING)
                for cat, channels in guild.by_category():
                    if cat.id == CategoryIDs.SHOPPING: #shopping category
                        for channel in channels:
                #for channel in CategoryIDs.SHOPPING:
                            if channel.id != ChannelIDs.LATER:
                                if channel.id != ChannelIDs.PURCHASED:

                                    stackstore.append(channel.name)
                                    storecount = storecount + 1
                for x in stackstore:
                    #reaction = g.readline()
                    #print(x) #check
                    #counter
                    storeincrement=storeincrement+1
                    #print(storeincrement) #check
                    #massive list of emoji
                    if storeincrement == 1:
                        await message.add_reaction('1️⃣')
                    if storeincrement == 2:
                        await message.add_reaction('2️⃣')
                    if storeincrement == 3:
                        await message.add_reaction('3️⃣')
                    if storeincrement == 4:
                        await message.add_reaction('4️⃣')
                    if storeincrement == 5:
                        await message.add_reaction('5️⃣')
                    if storeincrement == 6:
                        await message.add_reaction('6️⃣')
                    if storeincrement == 7:
                        await message.add_reaction('7️⃣')
                    if storeincrement == 8:
                        await message.add_reaction('8️⃣')
                    if storeincrement == 9:
                        await message.add_reaction('9️⃣')
                    if storeincrement == 10:
                        await message.add_reaction('0️⃣')

    await bot.process_commands(message)

cleanup_time = datetime.time(
    Options.DAILY_CLEANUP_HOUR+Options.TIMEZONE-Options.DST,
    Options.DAILY_CLEANUP_MINUTE,
    0,
    0,
)

print('cleanup time is '+str(cleanup_time))
#print(datetime.datetime.today())
print('utc time is '+str(datetime.datetime.utcnow()))
#change to
print('Ping Day is '+str(Options.PING_DAY))
print('Today is '+str(datetime.datetime.now().weekday()))

#the daily cleanup loop
@tasks.loop(time=cleanup_time)
async def cleanup():
    await bot.wait_until_ready()
    #stops it if it is past time
    if datetime.datetime.utcnow().hour <= cleanup_time.hour:
        print("It's cleanup time!")
        commands_channel = bot.get_channel(ChannelIDs.BOT_COMMANDS)
        await commands_channel.send("Now starting scheduled cleanup")

        #copyable part of the old command
        counter = 0
        guild = bot.get_guild(GuildIDs.LG_SHOPPING)
        print('Guild is '+str(guild))
        channel = bot.get_channel(ChannelIDs.PURCHASED)
        print('Channel is '+str(channel))
        today = datetime.date.today()
        #print(today)
        cutoff = datetime.timedelta(days=Options.AUTO_DELETE_AGE)
        async for message in channel.history(limit=200): #reads messages
            msgdate = message.created_at
            msgdate = datetime.datetime.date(msgdate)
            age = today-msgdate
            if age > cutoff:
                await message.delete()
                counter = counter+1
        await commands_channel.send(str(counter)+' old items deleted from '+channel.mention)

        #audit task
        for cat, channels in guild.by_category():
            if cat.id == CategoryIDs.SHOPPING: #shopping
                for channel in channels:
                    print('currently auditing:')
                    print(channel.name)
                    print('-----')
                    async for message in channel.history(limit=200):
                        #only activates these if no embed is found
                        if message.embeds == []:
                            await message.clear_reactions() #clears out all the old reactions
                            await message.add_reaction('✅')
                            if channel.id == ChannelIDs.LATER: #later
                                await message.add_reaction('⏭️')
                                    #prompt to move to other channels
                            else:
                                await message.add_reaction('⏮️')
                                #prompt to move back to later
                        #cleans up embeds so i don't have to do it manually
                        else:
                            await message.delete()

        await commands_channel.send('Audit of shopping lists complete!')
        print('audit complete')

        #list task
        channel = bot.get_channel(ChannelIDs.GROCERY_LIST) #grocery list
        async for message in channel.history(limit=20): #deletes grocery list
            await message.delete()

        for cat, channels in guild.by_category():
            if cat.id == CategoryIDs.SHOPPING: #shopping category
                for channel in channels:
                    print('currently listing:')
                    print(channel.name)
                    stack=[]
                    async for message in channel.history(limit=200):
                        content = message.content
                        stack.append(content)
                        stack.append('\n')
                    msg = ''.join([str(i) for i in stack])
                    print(msg)
                    embed = discord.Embed(
                        title=channel,
                        description=msg,
                        color=discord.Color.orange(),
                        )
                    channel = bot.get_channel(ChannelIDs.GROCERY_LIST) #grocery list
                    await channel.send(
                    embed = embed,
                        )


        await channel.send('Grocery list current as of '+str(datetime.datetime.today()))

        #sends this message only on the right day
        if datetime.datetime.now().weekday() == Options.PING_DAY:
            list_channel = bot.get_channel(ChannelIDs.GROCERY_LIST)
            await list_channel.send("@everyone The weekly grocery list is ready!")
            print('ping sent')
    #old, audit, list, ping

cleanup.start()

#run token, in different file because of security
with open(r'./files/token.txt') as f:
    TOKEN = f.readline()

#this is for the token
bot.run(TOKEN)
