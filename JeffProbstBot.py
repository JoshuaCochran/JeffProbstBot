# -*- coding: utf-8 -*-
"""
Created on Thu Aug 18 17:25:05 2022

@author: Joshua Cochran
"""

import discord
from discord.ext import commands
import pandas
import os
import survivor_scraper
import utils

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
token = os.getenv("DISCORD_TOKEN")

config = utils.load_config()
bot.reportingChannel = config["reporting_channel"]
guild_id = config["guild_id"]
guild = discord.Object(id=guild_id, type=discord.abc.Snowflake)

state = utils.load_state()

@bot.command(name='setEpisode', help='Sets the current episode')
async def set_episode(ctx, episode_num):
    if episode_num is None or episode_num.lower() == 'help':
        pass
    elif not survivor_scraper.is_number(episode_num):
        pass
    else:
        global state
        state["current_episode"] = episode_num
        utils.save_state(state)
        
@bot.command(name='setSeason', help='Sets the current season')
async def set_season(ctx, season_num):
    if season_num is None or season_num.lower() == 'help':
        pass
    elif not survivor_scraper.is_number(season_num):
        pass
    else:
        global state
        state["current_season"] = season_num
        utils.save_state(state)
        
@bot.command(name='getCurrentSeason', help='returns the current season')
async def get_season(ctx):
    channel = bot.get_channel(bot.reportingChannel)
    await channel.send("The current season is " + str(state["current_season"]))

@bot.command(name='getCurrentEpisode', help='returns the current episode')
async def get_episode(ctx):
    channel = bot.get_channel(bot.reportingChannel)
    await channel.send("The current episode is " + str(state["current_episode"]))
    
@bot.hybrid_command(name="seasonpoll", help='Creates a poll to control the active season', guild=discord.Object(id=guild_id))
async def create_season_poll(ctx):
    global state
    
    emojis = utils.get_emojis()
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
        
    utils.save_state(state)
        
@bot.hybrid_command(name="episodepoll", help='Creates a poll to control the active episode', guild=discord.Object(id=guild_id))
async def create_episode_poll(ctx):
    global state
    emojis = utils.get_emojis()
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
    utils.save_state(state)
    
@bot.hybrid_command(name="createepisodetracker", help='Creates the episode tracker message', guild=discord.Object(id=guild_id))
async def create_episode_tracker(ctx):
    global state
    title = "Current Episode"
    description = "The currently selected episode. To select a new episode react to the episode poll in the pins!"
    embed=discord.Embed(title=title, description=description)
    
    embed.add_field(name="Current episode:", value=state["current_episode"])
    
    msg = await ctx.send(embed=embed)
    await msg.pin()
    
    if 'current_episode_tracker_id' in state.keys() and state['current_episode_tracker_id']:
        old_msg = await ctx.fetch_message(state["current_episode_tracker_id"])
        await old_msg.unpin()
        await old_msg.delete()
    
    state['current_episode_tracker_id'] = msg.id
    utils.save_state(state)
    
@bot.hybrid_command(name="createseasontracker", help='Creates the season tracker message', guild=discord.Object(id=guild_id))
async def create_season_tracker(ctx):
    global state
    title = "Current Season"
    description = "The currently selected season. To select a new season react to the season poll in the pins!"
    embed=discord.Embed(title=title, description=description)
    
    embed.add_field(name="Current season:", value=state["current_season"])
    
    msg = await ctx.send(embed=embed)
    await msg.pin()
    
    if 'current_season_tracker_id' in state.keys() and state['current_season_tracker_id']:
        old_msg = await ctx.fetch_message(state["current_season_tracker_id"])
        await old_msg.unpin()
        await old_msg.delete()
    
    state['current_season_tracker_id'] = msg.id
    utils.save_state(state)
    
@bot.hybrid_command(name="currentseasoncast", help='Prints the cast of the current season', guild=discord.Object(id=guild_id))
async def get_current_season_cast(ctx):    
    global state
    
    emojis = utils.get_emojis()
    season_dict = survivor_scraper.load_seasons()
    cast = survivor_scraper.load_season_cast(season_dict, state["current_season"])
    title = "Cast of Season " + str(state["current_season"])
    description = "React with a reaction corresponding to the survivor to get more details!"
    embed=discord.Embed(title=title, description=description)
    j = 0
    for cast_member in cast.keys():
        embed.add_field(name=cast_member, value=emojis[j])
        j += 1
    
    msg = await ctx.send(embed=embed)
    await msg.pin()
        
    for i in range(len(cast.keys())):
        await msg.add_reaction(emojis[i])
        
    if 'current_season_cast_id' in state.keys() and state['current_season_cast_id']:
        old_msg = await ctx.fetch_message(state['current_season_cast_id'])
        await old_msg.unpin()
        await old_msg.delete()
        
    state['current_season_cast_id'] = msg.id
    utils.save_state(state)
    
    
@bot.hybrid_command("reloadcommands", help="Reloads the server commands", guild=discord.Object(id=guild_id))
async def reload_commands(ctx):
    utils.create_all_slash_commands()
    await ctx.send("Reloaded commands")
    
@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id:
        return
    
    channel = bot.get_channel(config["reporting_channel"])
    if payload.message_id == state["episode_id"]:
        emojis = utils.get_emojis()
        index = emojis.index(payload.emoji.name)
        state["current_episode"] = index
        utils.save_state(state)
        print("Current episode set to " + str(index))
        
        if 'current_episode_tracker_id' in state.keys() and state['current_episode_tracker_id']:
            msg = await channel.fetch_message(state["current_episode_tracker_id"])
            embed = msg.embeds[0]
            embed.set_field_at(0, name="Current episode:", value=state["current_episode"])
            await msg.edit(embed=embed)
        
    elif payload.message_id == state["season_1_id"]:
        emojis = utils.get_emojis()
        index = emojis.index(payload.emoji.name)
        state["current_season"] = index
        print("Current season set to " + str(index))
        
        utils.save_state(state)
        
        if 'current_season_tracker_id' in state.keys() and state['current_season_tracker_id']:
            msg = await channel.fetch_message(state["current_season_tracker_id"])
            embed = msg.embeds[0]
            embed.set_field_at(0, name="Current season:", value=state["current_season"])
            await msg.edit(embed=embed)
    elif payload.message_id == state["season_2_id"]:
        emojis = utils.get_emojis()
        index = emojis.index(payload.emoji.name)
        state["current_season"] = index
        print("Current season set to " + str(index))
        utils.save_state(state)
        
        if 'current_season_tracker_id' in state.keys() and state['current_season_tracker_id']:
            msg = await channel.fetch_message(state["current_season_tracker_id"])
            embed = msg.embeds[0]
            embed.set_field_at(0, name="Current season:", value=state["current_season"])
            await msg.edit(embed=embed)
    elif payload.message_id == state['current_season_cast_id']:
        emojis = utils.get_emojis()
        index = emojis.index(payload.emoji.name)
        season_dict = survivor_scraper.load_seasons()
        cast = survivor_scraper.load_season_cast(season_dict, state["current_season"])
        cast_member_key = list(cast)[index]
        cast_member = cast[cast_member_key]
        
        title = cast_member['full_name']
        description = "Spoiler-free details about " + cast_member['full_name'] + '!'
        embed=discord.Embed(title=title, description=description)
        
        if 'photo' in cast_member.keys() and cast_member['photo']:
            cast_photo = cast_member['photo']
            embed.set_image(url=cast_photo)
        else:
            try:
                cast_photo = survivor_scraper.fetch_contestant_picture(cast_member['wiki_link'])
                embed.set_image(url=cast_photo)
            except Exception as inst:
                print(inst)
                
        for key in cast_member.keys():
            if key != 'seasons' and key != 'days' and key != 'full_name' and key != 'photo':
                value = cast_member[key]
                name = key.replace('_', ' ')
                embed.add_field(name=name, value=value, inline=False)
        msg = await channel.send(embed=embed)
        
        
        
        
        
@bot.event
async def on_raw_reaction_remove(payload):
    if payload.user_id == bot.user.id:
        return
    
    channel = bot.get_channel(config["reporting_channel"])
    if payload.message_id == state["episode_id"]:
        emojis = utils.get_emojis()
        index = emojis.index(payload.emoji.name)
        state["current_episode"] = index
        utils.save_state(state)
        print("Current episode set to " + str(index))
        
        if 'current_episode_tracker_id' in state.keys() and state['current_episode_tracker_id']:
            msg = await channel.fetch_message(state["current_episode_tracker_id"])
            embed = msg.embeds[0]
            embed.set_field_at(0, name="Current episode:", value=state["current_episode"])
            await msg.edit(embed=embed)
                
    elif payload.message_id == state["season_1_id"]:
        emojis = utils.get_emojis()
        index = emojis.index(payload.emoji.name)
        state["current_season"] = index
        print("Current season set to " + str(index))
        utils.save_state(state)
        
        if 'current_season_tracker_id' in state.keys() and state['current_season_tracker_id']:
            print("season tracker updating")
            msg = await channel.fetch_message(state["current_season_tracker_id"])
            embed = msg.embeds[0]
            embed.set_field_at(0, name="Current season:", value=state["current_season"])
            await msg.edit(embed=embed)
        
    elif payload.message_id == state["season_2_id"]:
        emojis = utils.get_emojis()
        index = emojis.index(payload.emoji.name)
        state["current_season"] = index
        print("Current season set to " + str(index))
        utils.save_state(state)
        
        if 'current_season_tracker_id' in state.keys() and state['current_season_tracker_id']:
            msg = await channel.fetch_message(state["current_season_tracker_id"])
            embed = msg.embeds[0]
            embed.set_field_at(0, name="Current season:", value=state["current_season"])
            await msg.edit(embed=embed)
    elif payload.message_id == state['current_season_cast_id']:
        emojis = utils.get_emojis()
        index = emojis.index(payload.emoji.name)
        season_dict = survivor_scraper.load_seasons()
        cast = survivor_scraper.load_season_cast(season_dict, state["current_season"])
        cast_member_key = list(cast)[index]
        cast_member = cast[cast_member_key]
        
        title = cast_member['full_name']
        description = "Spoiler-free details about " + cast_member['full_name'] + '!'
        embed=discord.Embed(title=title, description=description)
        
        if 'photo' in cast_member.keys() and cast_member['photo']:
            cast_photo = cast_member['photo']
            embed.set_image(url=cast_photo)
        else:
            try:
                cast_photo = survivor_scraper.fetch_contestant_picture(cast_member['wiki_link'])
                embed.set_image(url=cast_photo)
            except Exception as inst:
                print(inst)
                
        for key in cast_member.keys():
            if key != 'seasons' and key != 'days' and key != 'full_name' and key != 'photo':
                value = cast_member[key]
                name = key.replace('_', ' ')
                embed.add_field(name=name, value=value, inline=False)
        msg = await channel.send(embed=embed)
        
    
@bot.event
async def on_ready():
    await bot.tree.sync(guild=guild)
    await utils.create_all_slash_commands()
    print(f'{bot.user} has connected to Discord!')
        
bot.run(token)