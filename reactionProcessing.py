# -*- coding: utf-8 -*-
"""
Created on Sat Aug 20 09:59:47 2022

@author: Joshua
"""
import discord
import utils
import survivorScraper

async def process_reactions(bot, payload):
    if payload.user_id == bot.user.id:
        return
    
    state = utils.load_state(payload.guild_id)
        
    channel = bot.get_channel(payload.channel_id)
    if payload.message_id == state["episode_id"]:
        await update_episode_tracker(channel, payload)
        
    elif payload.message_id == state["season_1_id"] or payload.message_id == state["season_2_id"]:
        await update_season_tracker(channel, payload)
        
    elif payload.message_id == state['current_season_cast_id']:
       await update_season_cast(channel, payload)
    elif 'current_episode_cast_id' in state.keys() and payload.message_id == state['current_episode_cast_id']:
        await update_episode_cast(channel, payload)

async def update_episode_tracker(channel, payload):
    state = utils.load_state(payload.guild_id)
    emojis = utils.get_emojis()
        
    index = emojis.index(payload.emoji.name)
    state["current_episode"] = index
    utils.save_state(state, payload.guild_id)
    
    print("Current episode set to " + str(index))
        
    if 'current_episode_tracker_id' in state.keys() and state['current_episode_tracker_id']:
        amazon_watch_urls = utils.load_amazon_watch_urls()
        episode_urls = amazon_watch_urls[state['current_season']-1]['episode_urls']
        episode_url = ""
        if episode_urls and state['current_episode'] in episode_urls.keys():
            episode_url = episode_urls[state['current_episode']]
            
            
        msg = await channel.fetch_message(state["current_episode_tracker_id"])
        embed = msg.embeds[0]
            
        if episode_url:
            embed_dict = embed.to_dict()
            embed_dict['url'] = episode_url
            embed = discord.Embed.from_dict(embed_dict)
            embed.set_field_at(1, name="Watch party link:", value=episode_url)
        else:
            embed.set_field_at(1, name="Watch party link:", value="Watch party link not found")
        embed.set_field_at(0, name="Current episode:", value=state["current_episode"])
        await msg.edit(embed=embed)
        
async def update_season_tracker(channel, payload):
    state = utils.load_state(payload.guild_id)
    emojis = utils.get_emojis()
    
    index = emojis.index(payload.emoji.name)
    state["current_season"] = index
    utils.save_state(state, payload.guild_id)
    
    print("Current season set to " + str(index))
    
    if 'current_season_tracker_id' in state.keys() and state['current_season_tracker_id']:
        amazon_watch_urls = utils.load_amazon_watch_urls()
        season_url = amazon_watch_urls[state['current_season']-1]['season_url']
        
        msg = await channel.fetch_message(state["current_season_tracker_id"])
        embed = msg.embeds[0]
        embed_dict = embed.to_dict()
        embed_dict["url"] = season_url
        embed = discord.Embed.from_dict(embed_dict)
        embed.set_field_at(0, name="Current season:", value=state["current_season"])
        embed.set_field_at(1, name="Amazon season link:", value=season_url)
        await msg.edit(embed=embed)
        
async def update_season_cast(channel, payload):
    state = utils.load_state(payload.guild_id)
    emojis = utils.get_emojis()
    season_dict = survivorScraper.load_seasons()

    cast = survivorScraper.load_season_cast(season_dict, state["current_season"])
    
    index = emojis.index(payload.emoji.name)
    
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
            cast_photo = survivorScraper.fetch_contestant_picture(cast_member['wiki_link'])
            embed.set_image(url=cast_photo)
        except Exception as inst:
            print(inst)
            
    for key in cast_member.keys():
        if key != 'seasons' and key != 'days' and key != 'full_name' and key != 'photo':
            value = cast_member[key]
            name = key.replace('_', ' ')
            embed.add_field(name=name, value=value, inline=False)
    await channel.send(embed=embed)
    await channel.send('The tribe has spoken')
    
async def update_episode_cast(channel, payload):
    state = utils.load_state(payload.guild_id)
    emojis = utils.get_emojis()

    episode_cast = survivorScraper.load_episode_cast(state['current_season'], state['current_episode'])
    
    index = emojis.index(payload.emoji.name)
    
    cast_member_key = list(episode_cast)[index]
    cast_member = episode_cast[cast_member_key]
    
    title = cast_member['full_name']
    description = "Spoiler-free details about " + cast_member['full_name'] + '!'
    embed=discord.Embed(title=title, description=description)
    
    if 'photo' in cast_member.keys() and cast_member['photo']:
        cast_photo = cast_member['photo']
        embed.set_image(url=cast_photo)
    else:
        try:
            cast_photo = survivorScraper.fetch_contestant_picture(cast_member['wiki_link'])
            embed.set_image(url=cast_photo)
        except Exception as inst:
            print(inst)
            
    for key in cast_member.keys():
        if key != 'seasons' and key != 'days' and key != 'full_name' and key != 'photo':
            value = cast_member[key]
            name = key.replace('_', ' ')
            embed.add_field(name=name, value=value, inline=False)
    await channel.send(embed=embed)
    await channel.send('The tribe has spoken')