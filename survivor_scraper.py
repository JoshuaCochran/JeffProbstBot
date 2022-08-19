# -*- coding: utf-8 -*-
"""
Created on Thu Aug 18 08:34:14 2022

@author: Joshua
"""

import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import math
import pickle

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def round_episodes(df):
    new_columns = {}
    for col in df.columns:
        if col != 'Episode':
            if is_number(col):
                new_columns[col] = math.floor(float(col))
        else:
            new_columns[col] = col
    return df.rename(columns=new_columns)

def drop_superscripts_on_vote_counts(df):
    new_votes = []
    for vote in df.iloc[1]:
        if vote != 'Tiebreaker':
            new_votes.append(vote[0:3])
        else:
            new_votes.append(vote)
    df.iloc[1] = new_votes
    return df

def process_voting_table(df):
    df = df.drop(df.columns[[0]], axis=1)
    df = df.drop(df.index[[-1]])
    #df = df.drop(df.index[[0]])
    df = df.replace('—', 'DNV')
    df.fillna('OOTG', inplace=True)
    df.columns = df.columns.droplevel()
    
    df = round_episodes(df)

    df.index = [df.index, df['Episode']]
    df = df.drop(df.columns[[0]], axis=1)
    
    df = drop_superscripts_on_vote_counts(df)
    return df

def extract_voting_table_as_df(link):
    cara = requests.get(link)
    soup = BeautifulSoup(cara.content, 'lxml')
    
    voting_table = soup.select('table.wikitable')[-2]
    df = pd.read_html(str(voting_table))[0]
    df = process_voting_table(df)
    return df

def get_cast_voted_out_so_far(df, episode_num): 
    return df.loc[0][[i for i in range(1,episode_num)]].values[0]
    #return df.loc[df.index.get_level_values(0) == 0].values[0][1:episode_num]
    
def get_cast_in_episode(df, episode_num):
    all_contestants = df.loc[0].values[0][1:]
    if episode_num == 1:
        return all_contestants
    else:
        contestants_voted_out_so_far = get_cast_voted_out_so_far(df, episode_num)
        contestants_left = [contestants for contestants in all_contestants if contestants not in contestants_voted_out_so_far]
        np.random.shuffle(contestants_left)
        return contestants_left
    
def extract_season_cast(season_dict, season_num):
    link = convert_season_to_url(season_dict, season_num)
    cara = requests.get(link)
    soup = BeautifulSoup(cara.content, 'lxml')
        
    voting_table = soup.select('table.wikitable')[0]
    df = pd.read_html(str(voting_table))[0]
    if 'Contestant' in df.columns:
        contestants = df['Contestant']['Contestant.1']
    else:
        contestants = []
    contestant_full_names = []
    for row in contestants:
        if isinstance(row, str):
            contestant = row.split(',')[0][0:-2]
            contestant_full_names.append(contestant)
    return contestant_full_names
    
def get_season_cast(df):
    return df.loc[0].values[0][1:]

def get_season_cast_fullnames(df, season_dict, season_num):
    season_cast = get_season_cast(df)
    contestant_full_names = extract_season_cast(season_dict, season_num)

    season_cast_names = {}
    for name in season_cast:
        for full_name in contestant_full_names:
            if name in full_name:
                season_cast_names[name] = full_name
    return season_cast_names

def extract_seasons(link):
    cara = requests.get(link)
    soup = BeautifulSoup(cara.content, 'lxml')
    
    voting_table = soup.select('table.wikitable')[-1]
    df = pd.read_html(str(voting_table))[0]
    unprocessed_seasons = df['Survivor (US) Seasons'][0]
    
    season_array = unprocessed_seasons.split(' • ')
    season_dict = dict(enumerate(map(str, season_array)))
    return season_dict

def convert_season_to_url(season_dict, season_num):
    base_url = 'https://survivor.fandom.com/wiki/Survivor:_'
    season_name = season_dict[season_num-1]
    season_name = season_name.replace(' ', '_')
    url = base_url + season_name
    return url

def convert_contestant_to_url(contestant_name):
    base_url = 'https://survivor.fandom.com/wiki/'
    return base_url + contestant_name.replace(' ', '_')

def fetch_contestant_seasons(link):
    cara = requests.get(link)
    soup = BeautifulSoup(cara.content, 'lxml')
    
    seasons = []
    season_data = soup.findAll("nav", {"class": "pi-navigation pi-item-spacing pi-secondary-font"})
    for item in season_data:
        if item.i and item.i.a and item.i.a["title"]:
            if "Survivor: " in item.i.a["title"]:
                seasons.append(item.i.a["title"])
    return seasons
    
def fetch_seasons():
    link = 'https://survivor.fandom.com/wiki/Survivor:_Gabon'
    season_dict = extract_seasons(link)
    return season_dict

def fetch_contestant_info(link):
    cara = requests.get(link)
    soup = BeautifulSoup(cara.content, 'lxml')
    
    contestant_info = {}
    season_data = soup.findAll("div", {"class": "pi-item pi-data pi-item-spacing pi-border-color"})
    for item in season_data:
        if item["data-source"]:
            if item["data-source"] == "occupation":
                contestant_info["job"] = item.div.get_text()
            elif item["data-source"] == "hometown":
                contestant_info["hometown"] = item.div.get_text()
            elif item["data-source"] == "birthdate":
                birthdate = item.div.get_text().split(")")[0] + ")"
                contestant_info["birthdate"] = birthdate
            elif item["data-source"] == "days":
                contestant_info["days"] = item.div.get_text()
    return contestant_info
            
def fetch_all_contestant_info(season_cast):
    for cast_member in season_cast.keys():
        season_cast_link = convert_contestant_to_url(season_cast[cast_member])
        seasons = fetch_contestant_seasons(season_cast_link)
        season_cast[cast_member] = { 
            "full_name": season_cast[cast_member], 
            "wiki_link": season_cast_link,
            "seasons": seasons,
            "number_of_seasons": len(seasons)
            }
        season_cast[cast_member] = {**season_cast[cast_member], **fetch_contestant_info(season_cast_link)}
    return season_cast

def process_all_season_data(season_dict):
    for season in season_dict.keys():
        # These seasons are skipped because the wiki has a different formating for them
        if season_dict[season] != "Pearl Islands" and season < 40:
            print(season_dict[season])
            link = convert_season_to_url(season_dict, season+1)
            df = extract_voting_table_as_df(link)
            df.to_csv("data/" + season_dict[season]+'.csv')
        else:
            print("Skipped " + season_dict[season])
            
def read_in_season_data(season_dict, season_num):
    df = pd.read_csv("data/" + season_dict[season_num-1] + ".csv")
    df.index = [df.index, df['Episode']]
    df = df.drop(df.columns[[0]], axis=1)
    df = round_episodes(df)
    return df

def save_seasons(seasons_dict):
    with open('data/seasons_dictionary.pkl', 'wb') as f:
        pickle.dump(seasons_dict, f)
        
def load_seasons():
    with open('data/seasons_dictionary.pkl', 'rb') as f:
        seasons_dict = pickle.load(f)
    return seasons_dict

def save_cast(season_dict, season_num, season_cast_dict):
    with open("data/" + season_dict[season_num-1] + '_cast.pkl', 'wb') as f:
        pickle.dump(season_cast_dict, f)
        
def load_season_cast(season_dict, season_num):
    with open("data/" + season_dict[season_num-1] + '_cast.pkl', 'rb') as f:
        seasons_cast_dict = pickle.load(f)
    return seasons_cast_dict

def fetch_all_contestant_data(first_season, last_season):
    for i in range(first_season,last_season):
        season_num = i
        season_dict = load_seasons()
        print(str(i) + ": " + season_dict[season_num-1])
        if season_dict[season_num-1] != "Pearl Islands":
            df = read_in_season_data(season_dict, season_num)
            
            season_cast = get_season_cast_fullnames(df, season_dict, season_num)
            season_cast_dict = fetch_all_contestant_info(season_cast)
                
            save_cast(season_dict, season_num, season_cast_dict)
