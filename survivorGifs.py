# -*- coding: utf-8 -*-
"""
Created on Sat Aug 20 12:22:20 2022

@author: Joshua
"""

import os
import numpy as np
import requests
from bs4 import BeautifulSoup
import pickle
import io
import aiohttp
import discord

def fetch_all_survivor_gifs():
    available_seasons = ['the-australian-outback', 'guatemala']
    
    gifs = []
    for season in available_seasons:
        link = 'https://www.survivorgif.com/' + season + '/'
        webpage = requests.get(link)
        soup = BeautifulSoup(webpage.content, 'lxml')
                
        episode_links = []
        anchor_tags = soup.findAll("a", href=True)
        for anchor_tag in anchor_tags:
            if link + 'episode-' in anchor_tag['href']:
                episode_links.append(anchor_tag['href'])
        
        if len(episode_links) > 0:
            for episode_link in episode_links:
                webpage = requests.get(episode_link)
                soup = BeautifulSoup(webpage.content, 'lxml')
                
                article = soup.findAll('article')[0]
                images = article.findAll('img')
                for image in images:
                    gifs.append(image['src'])
        else:
            article = soup.findAll('article')[0]
            images = article.findAll('img')
            for image in images:
                gifs.append(image['src'])
                
    with open('data/gifs.pkl', 'wb') as f:
        pickle.dump(gifs, f)
        
def load_gifs():
    with open('data/gifs.pkl', 'rb') as f:
        gifs = pickle.load(f)
    return gifs

def download_gifs():
    gifs = load_gifs()
    for gif in gifs:
        with open('data/gifs/' + gif.split('/')[-1], 'wb') as f:
            f.write(requests.get(gif).content)

def get_random_gif():
    base_path = './data/gifs/'
    gifs = [f for f in os.listdir(base_path)]
    random_gif = np.random.choice(gifs, 1)[0]
    return base_path + random_gif

async def download_random_gif(ctx):
    gifs = load_gifs()
    gif_url = np.random.choice(gifs, 1)[0]
    async with aiohttp.ClientSession() as session:
        async with session.get(gif_url) as resp:
            if resp.status != 200:
                return await ctx.send('Does Not Count. (Error getting gif)')
            data = io.BytesIO(await resp.read())
            await ctx.send(file=discord.File(data, 'survivor_gif.gif'))
            await ctx.send('The tribe has spoken.')