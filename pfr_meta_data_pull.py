## This script uses the box score URLs from the game linke scraper
## and collects meta data on that page

import requests
import time
import random
from bs4 import BeautifulSoup
import pandas as pd
import numpy

data_folder = 'file path to folder where all data will be held...no trailing slash'

## Pull in URLs by turning data fram into list ##
url_file = '{0}/game_links_1960_to_2018.csv'.format(data_folder)
url_df = pd.read_csv(url_file)
filtered_df = url_df[url_df['Season'] >= 1990] ## hasn't been tested before 1990, but would work in theory ##
urls = filtered_df['Box Score Link'].tolist()


## helper data structures ##
month_translation = {
    'Jan' : 1,
    'Feb' : 2,
    'Mar' : 3,
    'Apr' : 4,
    'May' : 5,
    'Jun' : 6,
    'Jul' : 7,
    'Jul' : 8,
    'Aug' : 8,
    'Sep' : 9,
    'Oct' : 10,
    'Nov' : 11,
    'Dec' : 12,
}


## helper functions for scraping ##
## These are seperate mainly for read-ability ##
def get_meta_data_points (score_box_div):
    sub_divs = score_box_div.find_all('div', recursive=False)
    del sub_divs[-1] ## last div is a citation ##
    game_day = sub_divs[0].text.split(' ')[0]
    game_year = sub_divs[0].text.split(' ')[3]
    game_month = month_translation[sub_divs[0].text.split(' ')[1]]
    game_day_num = sub_divs[0].text.split(' ')[2].split(',')[0]
    if len(str(game_month)) == 1:
        game_month = '0{0}'.format(game_month)
    else:
        game_month = str(game_month)
    if len(str(game_day_num)) == 1:
        game_day_num = '0{0}'.format(game_day_num)
    else:
        game_day_num = str(game_day_num)
    game_date = '{0}-{1}-{2}'.format(game_year,game_month,game_day_num)
    local_start_time = sub_divs[1].text.split(': ')[1]
    stadium = sub_divs[2].text.split(': ')[1].strip()
    stadium_link = sub_divs[2].find('a').get('href')
    if len(sub_divs) < 4:
        game_length = numpy.nan
        attendance = numpy.nan
    elif len(sub_divs) < 5:
        game_length = numpy.nan
        attendance = sub_divs[3].text.split(': ')[1]
    else:
        game_length_unformat = sub_divs[4].text.split(': ')[1]
        game_length = int(game_length_unformat.split(':')[0]) * 60 + int(game_length_unformat.split(':')[1])
        attendance = sub_divs[3].text.split(': ')[1]
    return game_day, game_date, local_start_time, game_length, stadium, stadium_link, attendance


def get_game_info (game_info_div):
    won_toss = numpy.nan
    won_toss_ot = numpy.nan
    roof = numpy.nan
    surface = numpy.nan
    weather = numpy.nan
    vegas_line = numpy.nan
    over_under = numpy.nan
    if game_info_div == None:
        pass
    else:
        for row in game_info_div.find_all('tr'):
            try:
                stat_name = row.find('th').text
                stat_value = row.find('td').text
            except:
                stat_name = None
                stat_value = None
            if stat_name == 'Won Toss':
                won_toss = stat_value
            elif stat_name == 'Roof':
                roof = stat_value
            elif stat_name == 'Surface':
                surface = stat_value
            elif stat_name == 'Weather':
                weather = stat_value
            elif stat_name == 'Vegas Line':
                vegas_line = stat_value
            elif stat_name == 'Over/Under':
                over_under = stat_value
    return won_toss, won_toss_ot, roof, surface, weather, vegas_line, over_under


def get_qb_info (starter_div):
    qb = numpy.nan
    qb_link = numpy.nan
    if starter_div == None:
        pass
    else:
        for row in starter_div.find_all('tr'):
            try:
                player_name = row.find('th').find('a')
                player_position = row.find('td').text
            except:
                player_name = None
                player_position = None
            if player_position == 'QB':
                qb = player_name.text
                qb_link = player_name.get('href')
            else:
                pass
    return qb, qb_link


def get_officials_info(officials_div):
    referee = numpy.nan
    umpire = numpy.nan
    down_judge = numpy.nan
    line_judge = numpy.nan
    back_judge = numpy.nan
    side_judge = numpy.nan
    field_judge = numpy.nan
    if(officials_div) == None:
        pass
    else:
        for row in officials_div.find_all('tr'):
            try:
                official_pos = row.find('th').text
                official_name = row.find('td').find('a').text
            except:
                official_pos = None
                official_name = None
            if official_pos == 'Referee':
                referee = official_name
            elif official_pos == 'Umpire':
                umpire = official_name
            elif official_pos == 'Down Judge' or official_pos == 'Head Linesman':
                down_judge = official_name
            elif official_pos == 'Line Judge':
                line_judge = official_name
            elif official_pos == 'Back Judge':
                back_judge = official_name
            elif official_pos == 'Side Judge':
                side_judge = official_name
            elif official_pos == 'Field Judge':
                field_judge = official_name
    return referee, umpire, down_judge, line_judge, back_judge, side_judge, field_judge


game_data_rows = []
broken_box_list = []

for url in urls:
    time.sleep((.75 + random.random() * .5))
    try:
        game_data_points = {
            'Game Link' : None,
            'Game Date' : None,
            'Game Day' : None,
            'Local Start Time' : None,
            'Game Length' : None,
            'Stadium' : None,
            'Stadium Link' : None,
            'Attendance' : None,
            'Season': None,
            'Week' : None,
            'Home Team' : None,
            'Away Team' : None,
            'Home Record' : None,
            'Away Record' : None,
            'Home Score' : None,
            'Away Score' : None,
            'Home Coach' : None,
            'Away Coach' : None,
            'Home Coach Link' : None,
            'Away Coach Link' : None,
            'Home Starting QB' : None,
            'Away Starting QB' : None,
            'Home Starting QB Link' : None,
            'Away Starting QB Link' : None,
            'Won Toss' : None,
            'Won Toss (OT)' : None,
            'Roof' : None,
            'Surface' : None,
            'Weather' : None,
            'Vegas Line' : None,
            'Over/Under' : None,
            'Referee' : None,
            'Umpire' : None,
            'Head Linesman / Down Judge' : None,
            'Line Judge' : None,
            'Back Judge' : None,
            'Side Judge' : None,
            'Field Judge' : None,
        }
        raw = requests.get(url)
        parsed = BeautifulSoup(raw.content, 'html.parser')
        score_board_divs = parsed.find('div', {'class' : 'scorebox'}).find_all('div', recursive=False)
        home_div = score_board_divs[0]
        away_div = score_board_divs[1]
        meta_div = score_board_divs[2]
        away_div_divs = away_div.find_all('div', recursive=False)
        away_team = away_div_divs[0].find('a', {'itemprop' : 'name'}).text
        try:
            away_score = int(away_div_divs[1].find('div').text)
        except:
            away_score = int(away_div_divs[1].text)
        away_record = away_div_divs[2].text
        away_coach = away_div_divs[4].find('a').text
        away_coach_link = away_div_divs[4].find('a').get('href')
        home_div_divs = home_div.find_all('div', recursive=False)
        home_team = home_div_divs[0].find('a', {'itemprop' : 'name'}).text
        try:
            home_score = int(home_div_divs[1].find('div').text)
        except:
            home_score = int(home_div_divs[1].text)
        home_record = home_div_divs[2].text
        home_coach = home_div_divs[4].find('a').text
        home_coach_link = home_div_divs[4].find('a').get('href')
        try: ## pfr's commenting messes up bs4s parsing, so the specific part has to get pulled as text and re-parsed ##
            game_info_div_effed = str(parsed.find('div', {'id': 'all_game_info'}))
            game_info_div = BeautifulSoup(game_info_div_effed.split('<!--')[1].split('-->')[0], 'html.parser')
        except:
            game_info_div = None
        try:
            home_starter_div_effed = str(parsed.find('div', {'id' : 'all_home_starters'}))
            home_starter_div = BeautifulSoup(home_starter_div_effed.split('<!--')[1].split('-->')[0], 'html.parser')
        except:
            home_starter_div = None
        try:
            away_starter_div_effed = str(parsed.find('div', {'id' : 'all_vis_starters'}))
            away_starter_div = BeautifulSoup(away_starter_div_effed.split('<!--')[1].split('-->')[0], 'html.parser')
        except:
            away_starter_div = None
        try:
            officials_div_effed = str(parsed.find('div', {'id' : 'all_officials'}))
            officials_div = BeautifulSoup(officials_div_effed.split('<!--')[1].split('-->')[0], 'html.parser')
        except:
            officials_div = None
        game_day, game_date, local_start_time, game_length, stadium, stadium_link, attendance = get_meta_data_points(meta_div)
        won_toss, won_toss_ot, roof, surface, weather, vegas_line, over_under = get_game_info(game_info_div)
        home_qb, home_qb_link = get_qb_info(home_starter_div)
        away_qb, away_qb_link = get_qb_info(away_starter_div)
        referee, umpire, down_judge, line_judge, back_judge, side_judge, field_judge = get_officials_info(officials_div)
        game_data_points['Game Link'] = url
        game_data_points['Game Date'] = game_date
        game_data_points['Game Day'] = game_day
        game_data_points['Local Start Time'] = local_start_time
        game_data_points['Game Length'] = game_length
        game_data_points['Stadium'] = stadium
        game_data_points['Stadium Link'] = stadium_link
        game_data_points['Attendance'] = attendance
        game_data_points['Season'] = filtered_df[filtered_df['Box Score Link'] == url].iloc[0]['Season']
        game_data_points['Week'] = filtered_df[filtered_df['Box Score Link'] == url].iloc[0]['Week Number']
        game_data_points['Home Team'] = home_team
        game_data_points['Away Team'] = away_team
        game_data_points['Home Record'] = home_record
        game_data_points['Away Record'] = away_record
        game_data_points['Home Score'] = home_score
        game_data_points['Away Score'] = away_score
        game_data_points['Home Coach'] = home_coach
        game_data_points['Away Coach'] = away_coach
        game_data_points['Home Coach Link'] = home_coach_link
        game_data_points['Away Coach Link'] = away_coach_link
        game_data_points['Home Starting QB'] = home_qb
        game_data_points['Away Starting QB'] = away_qb
        game_data_points['Home Starting QB Link'] = home_qb_link
        game_data_points['Away Starting QB Link'] = away_qb_link
        game_data_points['Won Toss'] = won_toss
        game_data_points['Won Toss (OT)'] = won_toss_ot
        game_data_points['Roof'] = roof
        game_data_points['Surface'] = surface
        game_data_points['Weather'] = weather
        game_data_points['Vegas Line'] = vegas_line
        game_data_points['Over/Under'] = over_under
        game_data_points['Referee'] = referee
        game_data_points['Umpire'] = umpire
        game_data_points['Head Linesman / Down Judge'] = down_judge
        game_data_points['Line Judge'] = line_judge
        game_data_points['Back Judge'] = back_judge
        game_data_points['Side Judge'] = side_judge
        game_data_points['Field Judge'] = field_judge
        game_data_rows.append(game_data_points)
    except:
        broken_row = {
            'Season' : None,
            'Week' : None,
            'URL' : None,
        }
        broken_row['Season'] = filtered_df[filtered_df['Box Score Link'] == url].iloc[0]['Season']
        broken_row['Week'] = filtered_df[filtered_df['Box Score Link'] == url].iloc[0]['Week']
        broken_row['URL'] = url
        broken_box_list.append(broken_row)
        print('ROW BROKEN {0}'.format(broken_row))


df = pd.DataFrame(game_data_rows)
df_two = pd.DataFrame(broken_box_list)


headers = [
    'Game Link',
    'Game Date',
    'Game Day',
    'Local Start Time',
    'Game Length',
    'Stadium',
    'Stadium Link',
    'Attendance',
    'Season',
    'Week',
    'Home Team',
    'Away Team',
    'Home Record',
    'Away Record',
    'Home Score',
    'Away Score',
    'Home Coach',
    'Away Coach',
    'Home Coach Link',
    'Away Coach Link',
    'Home Starting QB',
    'Away Starting QB',
    'Home Starting QB Link',
    'Away Starting QB Link',
    'Won Toss',
    'Won Toss (OT)',
    'Roof',
    'Surface',
    'Weather',
    'Vegas Line',
    'Over/Under',
    'Referee',
    'Umpire',
    'Head Linesman / Down Judge',
    'Line Judge',
    'Back Judge',
    'Side Judge',
    'Field Judge'
]

df = df[headers]
df.to_csv('{0}/game_meta_data.csv'.format(data_folder))
