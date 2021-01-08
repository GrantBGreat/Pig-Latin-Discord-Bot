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


@bot.command(name = "save", description = "Can be run by admins only.\n\nThis command sets the channel for Pig Latin translation\n\n**Implementation:**\n```\np! save <channel mention>\n```", pass_context=True)
@commands.cooldown(1, 10, commands.BucketType.guild)
@has_permissions(administrator=True)
async def save(ctx, channel: discord.TextChannel=None):
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

    conn.commit()

    # find channel id and check if it's valid
    channel_id = 0
    try:
        if channel is None:
            save_embed = discord.Embed(title="Save", color = 0x7f1085)
            save_embed.add_field(name="ERROR", value="Please specify a channel via mention. For more information about this command:\n```\np! help save\n```")
            await ctx.send(embed=save_embed)
            return
        else:
            channel_id = channel.id
    except Exception as e:
        save_embed = discord.Embed(title="Report this!", color = 0xbd0000, url="https://github.com/GrantBGreat/Pig-Latin-Discord-Bot/issues")
        save_embed.add_field(name="*EXTREME ERROR*\n\nThis error should not normally occur!", value=f"If you are reading this error, I would greatly appretiate it if you report it on my github by clicking the \'Report this!\' at the top of this message, or go to this link:\n```\nhttps://github.com/GrantBGreat/Pig-Latin-Discord-Bot/issues\n```\nWhen you reporting it, please include the error code below:\n{e}")
        await ctx.send(embed=save_embed)
        return

    save_embed = discord.Embed(title="Save", color = 0x7f1085)
    c.execute("UPDATE main SET channel_id = ? WHERE guild_id = ?", (channel_id, gid))
    conn.commit()
    print(channel_id)


@bot.command(name = "Translate", description = "Translates given text to Pig Latin.\nImplementation:\n```\np! translate <text to translate>\n```", pass_context=True)
@commands.cooldown(1, 10, commands.BucketType.guild)
async def translate(ctx, *args):

    if not args:
        translate_embed = discord.Embed(title="Translate", color = 0x7f1085)
        translate_embed.add_field(name='ERROR', value='Please enter text to translate. For more information about this command:\n```\np! help translate\n```')
        await ctx.send(embed=translate_embed)
        return

    ay = 'ay'
    way = 'way'
    consonant = ('B','C','D','F','G','H','J','K','L','M','N','P','Q','R','S','T','Y','V','X','Z')
    vowel = ('A','E','I','O','U')
    pig_latin_string =''

    for user_word in args:
        # getting first letter and making sure its a string and setting it to uppercase
        first_letter = user_word[0]
        first_letter = str(first_letter)
        first_letter=first_letter.upper()

        if first_letter in consonant:
            length_of_word = len(user_word)
            remove_first_letter = user_word[1:length_of_word]
            pig_latin=remove_first_letter+first_letter.lower()+ay
        elif first_letter in vowel:
            pig_latin=user_word+way
        else:
            translate_embed = discord.Embed(title="Report this!", color = 0xbd0000, url="https://github.com/GrantBGreat/Pig-Latin-Discord-Bot/issues")
            translate_embed.add_field(name="*EXTREME ERROR*\n\nThis error should not normally occur!", value=f"If you are reading this error, I would greatly appretiate it if you report it on my github by clicking the \'Report this!\' at the top of this message, or go to this link:\n```\nhttps://github.com/GrantBGreat/Pig-Latin-Discord-Bot/issues\n```\nWhen you reporting it, please include the error code below:\n{e}")
            await ctx.send(embed=translate_embed)
            return

            
            
        pig_latin_string=pig_latin_string+' '+pig_latin


    translate_embed = discord.Embed(title="Translate", color = 0x7f1085)
    translate_embed.add_field(name="English:", value=' '.join(args))
    translate_embed.add_field(name="Pig Latin:", value=pig_latin_string[1:len(pig_latin_string)])
    await ctx.send(embed=translate_embed)


########################################CATCH-ERRORS##################################################################


@save.error
async def save_error(ctx, error):
    if isinstance(error, MissingPermissions):
        error_embed = discord.Embed(title="ERROR", color = 0x7f1085)
        error_embed.add_field(name='No permission', value="Sorry {}, you do not have permissions to do that!".format(ctx.message.author.name))
        await ctx.send(embed=error_embed)
    else:
        error_embed = discord.Embed(title="ERROR", color = 0x7f1085)
        error_embed.add_field(name='Invalid channel', value=f"{error}\nPlease specify a channel via mention. For more information about this command:\n```\np! help save\n```")
        await ctx.send(embed=error_embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        error_embed = discord.Embed(title="ERROR", color = 0x7f1085)
        error_embed.add_field(name='Command on Cooldown:', value="Please retry in %s seconds" % int(error.retry_after))
        await ctx.send(embed=error_embed)

bot.run(TOKEN)