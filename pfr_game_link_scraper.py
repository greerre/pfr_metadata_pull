## This script goes to week 1 of every season and collects
## the other weeks that are listed there for navigation.
## The script then goes to each week of each season and collects the box score URLs
## The output is a csv with season, week name, and box score URL for every game


import requests
import time
import random
import string
from bs4 import BeautifulSoup
import pandas as pd
import numpy

data_folder = 'file path to folder where all data will be held...no trailing slash'

season_start = 1960
season_end = 2018
current_season = season_start

url_base = 'https://www.pro-football-reference.com'
game_data = []

while current_season <= season_end:
    time.sleep((1.5 + random.random() * 2))
    url = '{0}/years/{1}/week_1.htm'.format(url_base,current_season)
    print('Requesting weeks for the {0} season...'.format(current_season))
    raw = requests.get(url)
    parsed = BeautifulSoup(raw.content, 'html.parser')
    all_anchors = parsed.find_all('a',href=True) ## anchors used b/c commenting makes pulling specific divs hard ##
    week_links = []
    for a in all_anchors:
        if '/years/{0}/week_'.format(current_season) in a.get('href'):
            week_info = {
                'Week Name' : None,
                'Week Link' : None,
            }
            week_info['Week Name'] = str(a.text)
            week_info['Week Link'] = '{0}{1}'.format(url_base,str(a.get('href')))
            week_links.append(week_info)
    ## remove duplicates from week_links ##:
    ## from https://stackoverflow.com/questions/9427163/remove-duplicate-dict-in-list-in-python ##
    seen_links = []
    new_link_list = []
    for d in week_links:
        t = d['Week Link']
        if t not in seen_links:
            seen_links.append(t)
            new_link_list.append(d)
    week_links = new_link_list
    print('   * Found {0} weeks...'.format(len(week_links)))
    for week in week_links:
        print('      * Pulling {0} game links'.format(week['Week Name']))
        time.sleep((.75 + random.random() * 1.5))
        url = week['Week Link']
        raw_week = requests.get(url)
        parsed_week = BeautifulSoup(raw_week.content, 'html.parser')
        week_anchors = parsed_week.find_all('a',href=True)
        for a in week_anchors:
            if '/boxscores/{0}'.format(current_season) in a.get('href') or '/boxscores/{0}'.format(current_season + 1) in a.get('href'):
                box_info = {
                    'Season' : None,
                    'Week' : None,
                    'Week Number' : None,
                    'Box Score Link' : None,
                }
                box_info['Season'] = int(current_season)
                box_info['Week'] = week['Week Name']
                box_info['Week Number'] = int(week.split('/week_')[1].split('.htm')[0])
                box_info['Box Score Link'] = '{0}{1}'.format(url_base,str(a.get('href')))
                game_data.append(box_info)
    current_season += 1

df = pd.DataFrame(game_data)
df = df[['Season', 'Week', 'Week Number', 'Box Score Link']]
df.to_csv('{0}/game_links_{1}_to_{2}.csv'.format(data_folder,season_start,season_end))
