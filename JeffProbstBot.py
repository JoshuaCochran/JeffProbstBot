# -*- coding: utf-8 -*-
"""
Created on Thu Aug 18 17:25:05 2022

@author: Joshua
"""

import discord
from discord.ext import commands
import csv
import copy
import pandas
import os
import survivor_scraper 

bot = commands.Bot(command_prefix='!')
token = os.getenv("DISCORD_TOKEN")
bot.reportingChannel = 888867719032737835

current_episode = 1
current_season = 1

@bot.command(name='setEpisode', help='Sets the current episode')
async def set_episode(ctx, episode_num):
    if episode_num is None or episode_num.lower() == 'help':
        pass
    elif not survivor_scraper.is_number(episode_num):
        pass
    else:
        global current_episode
        current_episode = episode_num
        
@bot.command(name='setSeason', help='Sets the current season')
async def set_season(ctx, season_num):
    if season_num is None or season_num.lower() == 'help':
        pass
    elif not survivor_scraper.is_number(season_num):
        pass
    else:
        global current_season
        current_season = season_num
        
@bot.command(name='getCurrentSeason', help='returns the current season')
async def get_season(ctx):
    channel = bot.get_channel(bot.reportingChannel)
    await channel.send("The current season is " + str(current_season))

@bot.command(name='getCurrentEpisode', help='returns the current episode')
async def get_episode(ctx):
    channel = bot.get_channel(bot.reportingChannel)
    await channel.send("The current episode is " + str(current_episode))
    
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
        
bot.run(token)