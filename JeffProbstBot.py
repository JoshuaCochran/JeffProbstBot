# -*- coding: utf-8 -*-
"""
Created on Thu Aug 18 17:25:05 2022

@author: Joshua
"""

import discord
from discord.ext import commands
import pandas
import os
import survivor_scraper 

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
token = os.getenv("DISCORD_TOKEN")
bot.reportingChannel = 888867719032737835

state = survivor_scraper.load_state()

@bot.command(name='setEpisode', help='Sets the current episode')
async def set_episode(ctx, episode_num):
    if episode_num is None or episode_num.lower() == 'help':
        pass
    elif not survivor_scraper.is_number(episode_num):
        pass
    else:
        global state
        state["current_episode"] = episode_num
        survivor_scraper.save_state(state)
        
@bot.command(name='setSeason', help='Sets the current season')
async def set_season(ctx, season_num):
    if season_num is None or season_num.lower() == 'help':
        pass
    elif not survivor_scraper.is_number(season_num):
        pass
    else:
        global state
        state["current_season"] = season_num
        survivor_scraper.save_state(state)
        
@bot.command(name='getCurrentSeason', help='returns the current season')
async def get_season(ctx):
    channel = bot.get_channel(bot.reportingChannel)
    await channel.send("The current season is " + str(state["current_season"]))

@bot.command(name='getCurrentEpisode', help='returns the current episode')
async def get_episode(ctx):
    channel = bot.get_channel(bot.reportingChannel)
    await channel.send("The current episode is " + str(state["current_episode"]))
    
@bot.command(name="SeasonPoll", help='Creates a poll to control the active season')
async def create_season_poll(ctx):
    global state
    
    emojis = survivor_scraper.get_emojis()
    seasons = survivor_scraper.load_seasons()
    title = "Season Selection (1-20)"
    description = "React with a reaction corresponding to the season you want to select!"
    embed=discord.Embed(title=title, description=description)
    for i in range(1, 21):
        embed.add_field(name=str(i) + ": " + seasons[i-1], value=emojis[i])
    
    msg = await ctx.send(embed=embed)
    await msg.pin()
        
    for i in range(1, 21):
        await msg.add_reaction(emojis[i])
        
    if state["season_1_id"]:
        old_msg = await ctx.fetch_message(state["season_1_id"])
        await old_msg.unpin()
        await old_msg.delete()
        
    state["season_1_id"] = msg.id
    
    title = "Season Selection (21-40)"
    embed=discord.Embed(title=title, description=description)
    for i in range(21, 41):
        embed.add_field(name=str(i) + ": " + seasons[i-1], value=emojis[i])
        
    msg = await ctx.send(embed=embed)
    await msg.pin()
            
    for i in range(21, 41):
        await msg.add_reaction(emojis[i])
        
    if state["season_1_id"]:
        old_msg = await ctx.fetch_message(state["season_2_id"])
        await old_msg.unpin()
        await old_msg.delete()
        
    state["season_2_id"] = msg.id
        
    survivor_scraper.save_state(state)
        
@bot.command(name="EpisodePoll", help='Creates a poll to control the active episode')
async def create_episode_poll(ctx):
    global state
    emojis = survivor_scraper.get_emojis()
    title = "Episode Selection (1-16)"
    description = "React with a reaction corresponding to the episode you want to select!"
    embed=discord.Embed(title=title, description=description)
    for i in range(1, 17):
        embed.add_field(name=str(i), value=emojis[i])
    
    msg = await ctx.send(embed=embed)
    await msg.pin()
    
    for i in range(1, 17):
        await msg.add_reaction(emojis[i])

    if state["episode_id"]:
        old_msg = await ctx.fetch_message(state["episode_id"])
        await old_msg.unpin()
        await old_msg.delete()
        
    state["episode_id"] = msg.id
    survivor_scraper.save_state(state)
    
@bot.command(name="CurrentSeasonCast", help='Prints the cast of the current season')
async def get_current_season_cast(ctx):
    season_dict = survivor_scraper.load_seasons()
    print(survivor_scraper.load_season_cast(season_dict, state["current_season"]).keys())
    
@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id:
        return
    
    if payload.message_id == state["episode_id"]:
        emojis = survivor_scraper.get_emojis()
        index = emojis.index(payload.emoji.name)
        state["current_episode"] = index
        survivor_scraper.save_state(state)
        print("Current episode set to " + str(index))
        
    elif payload.message_id == state["season_1_id"]:
        emojis = survivor_scraper.get_emojis()
        index = emojis.index(payload.emoji.name)
        state["current_season"] = index
        print("Current season set to " + str(index))
        
        survivor_scraper.save_state(state)
    elif payload.message_id == state["season_2_id"]:
        emojis = survivor_scraper.get_emojis()
        index = emojis.index(payload.emoji.name)
        state["current_season"] = index
        print("Current season set to " + str(index))
        survivor_scraper.save_state(state)
        
@bot.event
async def on_raw_reaction_remove(payload):
    if payload.user_id == bot.user.id:
        return
    
    if payload.message_id == state["episode_id"]:
        emojis = survivor_scraper.get_emojis()
        index = emojis.index(payload.emoji.name)
        state["current_episode"] = index
        survivor_scraper.save_state(state)
        print("Current episode set to " + str(index))
        
    elif payload.message_id == state["season_1_id"]:
        emojis = survivor_scraper.get_emojis()
        index = emojis.index(payload.emoji.name)
        state["current_season"] = index
        print("Current season set to " + str(index))
        survivor_scraper.save_state(state)
        
    elif payload.message_id == state["season_2_id"]:
        emojis = survivor_scraper.get_emojis()
        index = emojis.index(payload.emoji.name)
        state["current_season"] = index
        print("Current season set to " + str(index))
        survivor_scraper.save_state(state)
        
    
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
        
bot.run(token)