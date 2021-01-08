import os
import random
import sqlite3
import discord

from discord.ext import commands
from dotenv import load_dotenv
from discord import Member
from discord.ext.commands import has_permissions, MissingPermissions

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix=commands.when_mentioned_or("p! "), description="The ultimate bored person bot", help_command = None, case_insensitive = True)

print("Bot is starting...")

conn = sqlite3.connect("main.db")
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS main (
        guild_id integer,
        channel_id integer
    )''')

conn.commit()

@bot.event
async def on_ready():

    # Set bot status:
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="for Pig Latin"))

    print('\n\nLogged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('-------------------\n')

#########################################COMMANDS#####################################################################

@bot.command(name="help", description = "Learn what each command does.", pass_context=True) #help command
@commands.cooldown(1, 5, commands.BucketType.guild)
async def help(ctx, args=None):
    help_embed = discord.Embed(title="Help", color = 0x7f1085)
    command_names_list = [i.name for i in bot.commands]

    # If there are no arguments, just list the commands:
    if not args:
        help_embed.add_field(
            name="List of supported commands:",
            value="\n".join([i.name for i in bot.commands]),
            inline=False
        )
        help_embed.add_field(
            name="Details",
            value="The prefix for this bot is \"`p! `\" -- Remember the space between the prefix and command!\n\nType `!help <command name>` for more details about a command.",
            inline=False
        )

    # If is a valid command:
    elif args in command_names_list:
        help_embed.add_field(
            name=args,
            value=bot.get_command(args).description
        )

    # If else:
    else:
        help_embed.add_field(
            name="ERROR",
            value="That is not a valid command!"
        )

    await ctx.send(embed=help_embed)


@bot.command(name = "save", description = "Can be run by admins only.\n\nThis command sets the channel for Pig Latin translation\n\n**Impemetation:**\n`p! save <channel mention>", pass_context=True)
@commands.cooldown(1, 10, commands.BucketType.guild)
@has_permissions(administrator=True)
async def save(ctx, channel: discord.TextChannel=None):
    save_embed = discord.Embed(title="Save", color = 0x7f1085)

    # get guild in db
    gid = ctx.message.guild.id
    print(f"contacting database for guild {gid}...")
    c.execute("SELECT * FROM main WHERE guild_id=?", (gid,))
    if c.fetchone() is None:
        c.execute("INSERT INTO main (guild_id) VALUES (?)", (gid,))
        c.execute("SELECT * FROM main WHERE guild_id=?", (gid,))
        print(f"added guild {gid} to database")
    else:
        print(f"guild {gid} was found in db")

    # find channel id and check if it's valid
    try:
        if channel is None:
            print("None")
        else:
            channel_id = channel.id
    except Exception as e:
        print(e)

    print(channel_id)




########################################CATCH-ERRORS##################################################################


@save.error
async def save_error(ctx, error):
    if isinstance(error, MissingPermissions):
        error_embed = discord.Embed(title="ERROR", color = 0x7f1085)
        error_embed.add_field(name='No permission', value="Sorry {}, you do not have permissions to do that!".format(ctx.message.author.name))
        await ctx.send(embed=error_embed)
    else:
        error_embed = discord.Embed(title="ERROR", color = 0x7f1085)
        error_embed.add_field(name='Invalid channel', value=error)
        await ctx.send(embed=error_embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        error_embed = discord.Embed(title="ERROR", color = 0x7f1085)
        error_embed.add_field(name='Command on Cooldown:', value="Please retry in %s seconds" % int(error.retry_after))
        await ctx.send(embed=error_embed)

bot.run(TOKEN)