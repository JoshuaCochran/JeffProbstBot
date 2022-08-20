# -*- coding: utf-8 -*-
'''
Created on Fri Aug 19 10:32:15 2022

@author: Joshua Cochran
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

def load_config():
    try:
        with open('config/config.json', 'rb') as f:
            config = json.load(f)
    except Exception as inst:
        config = {
            'guild_id': None,
            'app_id': None,
            'reporting_channel': None
        }
        print("Loading config/config.json failed. Setting config to defaults.")
        print(inst)
    return config

def save_state(state):
    with open('data/state.pkl', 'wb') as f:
        pickle.dump(state, f)
    
def load_state():
    try:
        with open('data/state.pkl', 'rb') as f:
            state = pickle.load(f)
    except:
        config = load_config()
        state = {
            'current_episode': 1,
            'current_season': 1,
            'season_1_id': None,
            'season_2_id': None,
            'episode_id': None,
            'current_episode_tracker_id': None,
            'current_season_tracker_id': None,
            'current_season_cast_id': None,
            'current_episode_cast_id': None
            }
    return state


async def create_all_slash_commands():
    try:
        f = open('config/slash_commands.json')
    
        command_list = json.load(f)
        token = os.getenv("DISCORD_TOKEN")
    
        command_json = []
        for command in command_list:
            _json = {
                'name': command['name'],
                'type': command['type'],
                'description': command['description'],
                'default_member_permissions': '0'
            }
            if 'options' in command.keys():
                _json['options'] = command['options']
            
            command_json.append(_json)
        
        headers = {
            'Authorization': 'Bot ' + str(token)
        }
        
        config = load_config()
        token = os.getenv('DISCORD_TOKEN')
        url = 'https://discord.com/api/v10/applications/' + str(config['app_id']) + '/guilds/' + str(config['guild_id']) + '/commands'
            
        requests.put(url, headers=headers, json=command_json)
            
    except Exception as inst:
       print('Error while loading slash commands')
       print(inst)