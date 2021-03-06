#!/usr/bin/env python3
# help.py
# cameronshinn

import discord
from discord.ext import commands
import Levenshtein as lev

THUMBNAIL = 'https://i.imgur.com/5v6mLwb.png'
GITHUB = 'github.com/cameronshinn/csgo-queue-bot'


class HelpCog(commands.Cog):
    """ Handles everything related to the help menu. """

    def __init__(self, bot, color):
        """ Set attributes and remove default help command. """
        self.bot = bot
        self.color = color
        self.logo = 'https://raw.githubusercontent.com/cameronshinn/csgo-queue-bot/master/assets/logo/rounded_logo.png'
        self.bot.remove_command('help')

    def help_embed(self, title):
        embed = discord.Embed(title=title, color=self.color)
        prefix = self.bot.command_prefix
        prefix = prefix[0] if prefix is not str else prefix

        for cog in self.bot.cogs:  # Uset bot.cogs instead of bot.commands to control ordering in the help embed
            for cmd in self.bot.get_cog(cog).get_commands():
                if cmd.name == 'remove':
                    embed.add_field(name=f'**{cmd.usage}**', value=f'_{cmd.brief}_', inline=False)
                else:
                    embed.add_field(name=f'**{prefix}{cmd.name}**', value=f'_{cmd.brief}_', inline=False)

        return embed

    @commands.Cog.listener()
    async def on_ready(self):
        """ Set presence to let users know the help command. """
        activity = discord.Activity(type=discord.ActivityType.watching, name="noobs type q!help")
        await self.bot.change_presence(activity=activity)

    async def cog_before_invoke(self, ctx):
        """ Trigger typing at the start of every command. """
        await ctx.trigger_typing()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """ Send help message when a mis-entered command is received. """
        if type(error) is commands.CommandNotFound:
            # Get Levenshtein distance from commands
            in_cmd = ctx.invoked_with
            bot_cmds = list(self.bot.commands)
            lev_dists = [lev.distance(in_cmd, str(cmd)) / max(len(in_cmd), len(str(cmd))) for cmd in bot_cmds]
            lev_min = min(lev_dists)

            # Prep help message title
            embed_title = f'**```{ctx.message.content}```** is not valid!'
            prefix = self.bot.command_prefix
            prefix = prefix[0] if prefix is not str else prefix

            # Make suggestion if lowest Levenshtein distance is under threshold
            if lev_min <= 0.5:
                embed_title += f' Did you mean `{prefix}{bot_cmds[lev_dists.index(lev_min)]}`?'
            else:
                embed_title += f' Use `{prefix}help` for a list of commands'

            embed = discord.Embed(title=embed_title, color=self.color)
            await ctx.send(embed=embed)

    @commands.command(brief='Display the help menu')  # TODO: Add 'or details of the specified command'
    async def help(self, ctx):
        """ Generate and send help embed based on the bot's commands. """
        embed = self.help_embed('__Queue Bot Commands__')
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        """ Send the help embed if the bot is mentioned. """
        if self.bot.user in message.mentions:
            await message.channel.send(embed=self.help_embed('__Queue Bot Commands__'))

    @commands.command(brief='Display basic info about this bot')
    async def info(self, ctx):
        """ Display the info embed. """
        header = '_The definitive bot for setting up 10-man lobbies_'
        support_link = '[Join our support server here](https://discordapp.com/invite/tskeyDA)'
        topgg_link = '[Be sure to upvote the bot on top.gg](https://top.gg/bot/539669626863353868)'
        github_link = '[Source code can be found here on GitHub](https://github.com/cameronshinn/csgo-queue-bot)'
        description = f'{header}\n\n{support_link}\n{topgg_link}\n{github_link}'
        embed = discord.Embed(title='__10-ManQ Queue Bot__', description=description, color=self.color)
        embed.set_thumbnail(url=self.logo)
        await ctx.send(embed=embed)
