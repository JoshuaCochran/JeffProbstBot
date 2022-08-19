# -*- coding: utf-8 -*-
'''
Created on Fri Aug 19 10:32:15 2022

@author: Joshua
'''

import requests
import pickle
import os
import json

def get_emojis():
    response = requests.get('https://unicode.org/Public/emoji/13.0/emoji-sequences.txt')

    emojis = []
    for line in response.content.decode('utf8').split('\n'):
        if line.strip() and not line.startswith('#'):
            line = line.replace(' ', '')
            hexas = line.split(';')[0]
            hexas = hexas.split('..')
            for hexa in hexas:
                try:
                    hexa = chr(int(hexa, 16))
                except:
                    pass
                emojis.append(hexa)
    return(emojis)

def save_state(state):
    with open('data/state.pkl', 'wb') as f:
        pickle.dump(state, f)
    
def load_state():
    try:
        with open('data/state.pkl', 'rb') as f:
            state = pickle.load(f)
    except:
        state = {
            'current_episode': 1,
            'current_season': 1,
            'season_1_id': None,
            'season_2_id': None,
            'episode_id': None,
            'current_episode_tracker_id': None,
            'current_season_tracker_id': None
            }
    return state

def load_config():
    try:
        with open('config/config.json', 'rb') as f:
            config = json.load(f)
    except:
        config = {
            'guild_id': None,
            'app_id': None,
            'reporting_channel': None
        }
    return config

def create_slash_command(name, command_type, description, options=None):
    config = load_config()
    token = os.getenv("DISCORD_TOKEN")
    url = 'https://discord.com/api/v10/applications/' + str(config['app_id']) + '/guilds/' + str(config['guild_id']) + '/commands'
    
    json = {
        'name': name,
        'type': command_type,
        'description': description,
        'default_member_permisions': '0'
    }
    
    if options:
        json['options'] = options
    
    headers = {
        'Authorization': 'Bot ' + str(token)
    }
    
    requests.post(url, headers=headers, json=json)

def create_all_slash_commands():
    try:
        f = open('config/slash_commands.json')
    
        command_list = json.load(f)
    
        for command in command_list:
            create_slash_command(command['name'], command['type'], command['description'], command['options'] if 'options' in command.keys() else None)
    except:
       print('Error while loading slash commands')