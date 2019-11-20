import discord
import sys
from discord.ext import commands
import asyncio
from json import load, dump
import datetime
import os
from raven import Client as sentry_Client
import motor.motor_asyncio
import aiohttp
from cogs.utils import db
import traceback

with open("settings/config.json") as config_file:
    config = load(config_file)
bot = commands.Bot(command_prefix=commands.when_mentioned_or(*config["prefixes"]), description=config["description"])
bot.sentry_client = sentry_Client(config["SENTRY_DSN"])
bot.db_client = motor.motor_asyncio.AsyncIOMotorClient(config["MONGOHQ_URL"])
bot.config = config
bot.remove_command('help')
bot.session = aiohttp.ClientSession(loop=asyncio.get_event_loop())
bot.client_id = config["client_id"]
bot.cog_list = []
bot.categories = {}
bot.session = aiohttp.ClientSession(loop=bot.loop)
for f in os.listdir("cogs"):
    if f.endswith(".py"):
        bot.cog_list.append("cogs."+f[:-3])
for c in bot.cog_list:
    try:
        bot.load_extension(c)
        print("cog '{0}' loaded successfully".format(c))
    except Exception as e:
        bot.sentry_client.captureException()
        print("cog '{0}' load failed".format(c))
        traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)

async def presence():
    await bot.change_presence(activity=discord.Streaming(name="in "+str(len(bot.guilds))+" Guilds | "+config["status"], url="https://www.twitch.tv/the_c0sm0s"))
    bot.game = str(len(bot.guilds))+" Guilds | "+config["status"]

async def get_guild_shutup_settings(bot):
    guild_shutup_settings = {}
    for guild in bot.guilds:
        shutup_channels = await db.get_shutup_channels(guild.id)
        guild_shutup_settings[str(guild.id)] = shutup_channels
    return guild_shutup_settings

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    bot.uptime = datetime.datetime.now()
    bot.command_count = {}
    await presence()
    bot.guild_shutup_settings = await get_guild_shutup_settings(bot)

@bot.event
async def on_guild_join(guild):
    await presence()

@bot.event
async def on_guild_remove(guild):
    await presence()



"""@bot.check
async def shutup_bot(ctx):
    if ctx.message.content not in ["un-shutup", "speak", "unshutup"]:
        await ctx.message.delete()
        try:
            bot.guild_shutup_settings[str(ctx.guild.id)] = bot.guild_shutup_settings[str(ctx.guild.id)].remove(str(ctx.channel.id))
        except:
            pass
        return str(ctx.channel.id) not in bot.guild_shutup_settings[str(ctx.guild.id)]
    elif ctx.message.content not in ["shut-up", "shut up", "shutup"]:
        await ctx.message.delete()
        try:
            bot.guild_shutup_settings[str(ctx.guild.id)] = bot.guild_shutup_settings[str(ctx.guild.id)].append(str(ctx.channel.id))
        except:
            pass
        return str(ctx.channel.id) not in bot.guild_shutup_settings[str(ctx.guild.id)]"""

@bot.check
async def tad_general_check(ctx):
    try:
        if ctx.message.author.guild_permissions.manage_guild:
            return True
    except:
        pass
    if ctx.command.name.lower() == 'spoiler':
        return True
    if ctx.message.channel.id == 244998983112458240:
        await ctx.message.delete()
        return False
    if not ctx.guild:
        return True
    if ctx.author.bot:
        return False
    return True

bot.run(config["TOKEN"])
