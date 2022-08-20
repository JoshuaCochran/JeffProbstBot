# -*- coding: utf-8 -*-
"""
Created on Thu Aug 18 17:25:05 2022

@author: Joshua Cochran
"""

import discord
from discord.ext import commands
import os
import survivorScraper
import utils
import reactionProcessing

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
token = os.getenv("DISCORD_TOKEN")

config = utils.load_config()
guild_id = config['guild_id']
guild = discord.Object(id=guild_id, type=discord.abc.Snowflake)

@bot.command(name="savestate", help='Forces a state save')
def command_save_state(ctx):
    state = utils.load_state()
    utils.save_state(state, ctx.guild.id)
    
@bot.hybrid_command("reloadcommands", help="Reloads the server commands", guild=discord.Object(id=guild_id))
async def reload_commands(ctx):    
    utils.create_all_slash_commands()
    await ctx.send("Reloaded commands")
    
@bot.hybrid_command(name="seasonpoll", help='Creates a poll to control the active season', guild=discord.Object(id=guild_id))
async def create_season_poll(ctx):
    state = utils.load_state(ctx.guild.id)
    
    emojis = utils.get_emojis()
    seasons = survivorScraper.load_seasons()
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
        try:
            old_msg = await ctx.fetch_message(state["season_1_id"])
            await old_msg.unpin()
            await old_msg.delete()
        except:
            pass
        
    state["season_1_id"] = msg.id
    
    title = "Season Selection (21-40)"
    embed=discord.Embed(title=title, description=description)
    for i in range(21, 41):
        embed.add_field(name=str(i) + ": " + seasons[i-1], value=emojis[i])
        
    msg = await ctx.send(embed=embed)
    await msg.pin()
            
    for i in range(21, 41):
        await msg.add_reaction(emojis[i])
        
    if state["season_2_id"]:
        try:
            old_msg = await ctx.fetch_message(state["season_2_id"])
            await old_msg.unpin()
            await old_msg.delete()
        except:
            pass
        
    state["season_2_id"] = msg.id
        
    utils.save_state(state, ctx.guild.id)
        
@bot.hybrid_command(name="episodepoll", help='Creates a poll to control the active episode', guild=discord.Object(id=guild_id))
async def create_episode_poll(ctx):
    state = utils.load_state(ctx.guild.id)
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
        try:
            old_msg = await ctx.fetch_message(state["episode_id"])
            await old_msg.unpin()
            await old_msg.delete()
        except:
            pass
        
    state["episode_id"] = msg.id
    utils.save_state(state, ctx.guild.id)
    
@bot.hybrid_command(name="createepisodetracker", help='Creates the episode tracker message', guild=discord.Object(id=guild_id))
async def create_episode_tracker(ctx):
    state = utils.load_state(ctx.guild.id)
    title = "Current Episode"
    description = "The currently selected episode. To select a new episode react to the episode poll in the pins!"
    embed=discord.Embed(title=title, description=description)
    
    embed.add_field(name="Current episode:", value=state["current_episode"])
    
    amazon_watch_urls = utils.load_amazon_watch_urls()
    episode_urls = amazon_watch_urls[state['current_season']-1]['episode_urls']
    episode_url = ""
    if episode_urls and state['current_episode'] in episode_urls.keys():
        episode_url = episode_urls[state['current_episode']]
    
    if episode_url:
        embed.add_field(name="Watch party link:", value=episode_url)
    else:
        embed.add_field(name="Watch party link:", value="Watch party link not found")
    
    msg = await ctx.send(embed=embed)
    await msg.pin()
    
    if 'current_episode_tracker_id' in state.keys() and state['current_episode_tracker_id']:
        old_msg = await ctx.fetch_message(state["current_episode_tracker_id"])
        await old_msg.unpin()
        await old_msg.delete()
    
    state['current_episode_tracker_id'] = msg.id
    utils.save_state(state, ctx.guild.id)
    
    
@bot.hybrid_command(name="createseasontracker", help='Creates the season tracker message', guild=discord.Object(id=guild_id))
async def create_season_tracker(ctx):
    state = utils.load_state(ctx.guild.id)
    title = "Current Season"
    description = "The currently selected season. To select a new season react to the season poll in the pins!"
    embed=discord.Embed(title=title, description=description)
    
    embed.add_field(name="Current season:", value=state["current_season"])
    
    amazon_watch_urls = utils.load_amazon_watch_urls()
    season_url = amazon_watch_urls[state['current_season']-1]['season_url']
    embed.add_field(name="Amazon season link:", value=season_url, inline=False)
    
    msg = await ctx.send(embed=embed)
    await msg.pin()
    
    if 'current_season_tracker_id' in state.keys() and state['current_season_tracker_id']:
        try:
            old_msg = await ctx.fetch_message(state["current_season_tracker_id"])
            await old_msg.unpin()
            await old_msg.delete()
        except:
            pass
    
    state['current_season_tracker_id'] = msg.id
    utils.save_state(state, ctx.guild.id)
    
@bot.hybrid_command(name="currentseasoncast", help='Prints the cast of the current season', guild=discord.Object(id=guild_id))
async def get_current_season_cast(ctx):       
    state = utils.load_state(ctx.guild.id)
    
    emojis = utils.get_emojis()
    season_dict = survivorScraper.load_seasons()
    cast = survivorScraper.load_season_cast(season_dict, state["current_season"])
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
    utils.save_state(state, ctx.guild.id)
    
    
@bot.event
async def on_raw_reaction_add(payload):
    await reactionProcessing.process_reactions(bot, payload)
        
        
@bot.event
async def on_raw_reaction_remove(payload):
    await reactionProcessing.process_reactions(bot, payload)
        
    
@bot.event
async def on_ready():
    await bot.tree.sync(guild=guild)
    await utils.create_all_slash_commands()
    print(f'{bot.user} has connected to Discord!')
        
bot.run(token)