# -*- coding: utf-8 -*-
"""
Created on Thu Aug 18 21:51:17 2022

@author: Joshua
"""

import requests
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
print(emojis)
                
 