## This script takes the metadata collected in the metadata scraper and formats it
## both for general use and to be added to the nflscrapR dataset
## The script does this by assigning standardized names to teams and then joining on
## Season, Week, Home, and Away team
## Note that this requires a single CSV of all nflscrapR reg_game files and
## that these files only include regular season games dating to 2009.
## This script will return playoff games and games dating back to 1990, but they
## will not have any associated nflscrapR data

## packages used ##
import pandas as pd
import numpy
import math

data_folder = 'file path to folder where all data will be held...no trailing slash'

df_raw = pd.read_csv('{0}/game_meta_data.csv')
df_divisions = pd.read_csv(' file path to divisions.csv') ## this csv is uploaded to the github
df_scraper_game = pd.read_csv(' file path reg_game_all.csv') ## this csv is uploaded to the github

pfr_to_pbp_dict = {

    'Phoenix Cardinals' : 'ARI',
    'Miami Dolphins' : 'MIA',
    'Indianapolis Colts' : 'IND',
    'Tampa Bay Buccaneers' : 'TB',
    'Seattle Seahawks' : 'SEA',
    'Minnesota Vikings' : 'MIN',
    'Atlanta Falcons' : 'ATL',
    'Denver Broncos' : 'DEN',
    'New York Giants' : 'NYG',
    'Green Bay Packers' : 'GB',
    'San Francisco 49ers' : 'SF',
    'Washington Redskins' : 'WAS',
    'Houston Oilers' : 'TEN',
    'Cleveland Browns' : 'CLE',
    'Detroit Lions' : 'DET',
    'New England Patriots' : 'NE',
    'New Orleans Saints' : 'NO',
    'Pittsburgh Steelers' : 'PIT',
    'Los Angeles Raiders' : 'OAK',
    'Dallas Cowboys' : 'DAL',
    'San Diego Chargers' : 'LAC',
    'New York Jets' : 'NYJ',
    'Cincinnati Bengals' : 'CIN',
    'Buffalo Bills' : 'BUF',
    'Philadelphia Eagles' : 'PHI',
    'Chicago Bears' : 'CHI',
    'Arizona Cardinals' : 'ARI',
    'St. Louis Rams' : 'LAR',
    'Carolina Panthers' : 'CAR',
    'Oakland Raiders' : 'OAK',
    'Kansas City Chiefs' : 'KC',
    'Baltimore Ravens' : 'BAL',
    'Jacksonville Jaguars' : 'JAX',
    'Tennessee Oilers' : 'TEN',
    'Tennessee Titans' : 'TEN',
    'Houston Texans' : 'HOU',
    'Los Angeles Rams' : 'LAR',
    'Los Angeles Chargers' : 'LAC',

}

df_format = df_raw
df_format['Home Team (pfr)'] = df_format['Home Team']
df_format['Away Team (pfr)'] = df_format['Away Team']
df_format['Home Team'] = df_format['Home Team'].replace(pfr_to_pbp_dict)
df_format['Away Team'] = df_format['Away Team'].replace(pfr_to_pbp_dict)

df_divisions_home = df_divisions
df_divisions_away = df_divisions

home_rename_dict = {
    'Teams' : 'Home Team',
    'Conference' : 'Home Conference',
    'Division' : 'Home Division',
}
away_rename_dict = {
    'Teams' : 'Away Team',
    'Conference' : 'Away Conference',
    'Division' : 'Away Division',
}

df_divisions_home = df_divisions_home.rename(columns=home_rename_dict)
df_divisions_away = df_divisions_away.rename(columns=away_rename_dict)

df_format = pd.merge(df_format,df_divisions_home,on=['Home Team'], how='left')
df_format = pd.merge(df_format,df_divisions_away,on=['Away Team'], how='left')
df_format = df_format.drop(columns=['Unnamed: 0', 'Unnamed: 0_y', 'Unnamed: 0_x'])

df_format['Divisional Game'] = numpy.where((df_format['Season'] >= 2002) & (df_format['Home Conference'] == df_format['Away Conference']) & (df_format['Home Division'] == df_format['Away Division']),1,0)


def url_to_id(url_id):
    id = numpy.nan
    try:
        id = url_id.split('/')[-1].split('.htm')[0]
    except:
        pass
    return id


def row_format(row):
    ## pull out degrees and wind ##
    row['Temperature'] = None
    row['Wind'] = None
    if row['Roof'] != 'outdoors':
        row['Temperature'] = 70
        row['Wind'] = 0
    else:
        try:
            row['Temperature'] = int(row['Weather'].split(' degrees')[0])
        except:
            pass
        try:
            if 'no wind' in row['Weather']:
                row['Wind'] = 0
            else:
                row['Wind'] = int(row['Weather'].split(',')[1].split('wind ')[1].split(' mph')[0])
        except:
            pass
    ## translate vegas line to home line ##
    row['Home Spread'] = numpy.nan
    row['Total'] = numpy.nan
    if row['Vegas Line'] == 'Pick':
        row['Home Spread'] = 0
    else:
        line_list = row['Vegas Line'].split(' -')
        fav = line_list[0]
        favored_by = float(line_list[1])
        if fav == row['Home Team (pfr)']:
            row['Home Spread'] = favored_by
        elif fav == row['Away Team (pfr)']:
            row['Home Spread'] = favored_by * -1.0
        else:
            row['Home Spread'] = numpy.nan
    try:
        row['Total'] = float(row['Over/Under'].split(' (')[0])
    except:
        pass
    ## translate attendance ##
    try:
        row['Attendance'] = int(row['Attendance'].replace(',',''))
    except:
        try:
            row['Attendance'] = int(row['Attendance'])
        except:
            row['Attendance'] = numpy.nan
    ## translate tosses ##
    row['Home Won Toss'] = numpy.nan
    row['Deferred'] = numpy.nan
    ## for some reason the toss text is read as a float if it's blank and will throw
    ## an error on the split. This is handled w/ the try / except
    try:
        if row['Won Toss'] == numpy.nan:
            pass
        else:
            home_mascot = row['Home Team (pfr)'].split(' ')[-1]
            away_mascot = row['Away Team (pfr)'].split(' ')[-1]
            winner = row['Won Toss'].split(' (')[0]
            if home_mascot == winner:
                row['Home Won Toss'] = 1
                if len(row['Won Toss'].split(' (')) > 1:
                    row['Deferred'] = 1
                else:
                    row['Deferred'] = 0
            elif away_mascot == winner:
                row['Home Won Toss'] = 0
                if len(row['Won Toss'].split(' (')) > 1:
                    row['Deferred'] = 1
                else:
                    row['Deferred'] = 0
            else:
                pass
    except:
        pass
    ## conevrt urls to ids ##
    row['Stadium ID'] = url_to_id(row['Stadium Link'])
    row['Home Coach ID'] = url_to_id(row['Home Coach Link'])
    row['Away Coach ID'] = url_to_id(row['Away Coach Link'])
    row['Home Starting QB ID'] = url_to_id(row['Home Starting QB Link'])
    row['Away Starting QB ID'] = url_to_id(row['Away Starting QB Link'])
    return row



df_new = df_format.apply(row_format,axis=1)
df_new.to_csv('/Users/robertgreer/Documents/Coding/NFL/pro-football-reference/Data Files/game_meta_data_formatted.csv')

meta_merge_headers = [

    'Season',
    'Week',
    'Game Date',
    'Game Day',
    'Local Start Time',
    'Game Length',
    'Stadium',
    'Stadium ID',
    'Attendance',
    'Roof',
    'Surface',
    'Temperature',
    'Wind',
    'Home Team',
    'Away Team',
    'Home Score',
    'Away Score',
    'Divisional Game',
    'Home Spread',
    'Total',
    'Home Coach',
    'Away Coach',
    'Home Coach ID',
    'Away Coach ID',
    'Home Starting QB',
    'Away Starting QB',
    'Home Starting QB ID',
    'Away Starting QB ID',
    'Home Won Toss',
    'Deferred',
    'Referee',
    'Umpire',
    'Head Linesman / Down Judge',
    'Line Judge',
    'Back Judge',
    'Side Judge',
    'Field Judge'

]

merge_df = df_new[meta_merge_headers]

## convert header formating to match nflscrapR for the join
## note of caution...the original scraper swapped home and away team name and coaches
## those were swapped back with the header rename dict below
## the scraper has been fixed and the dict below has been swapped back, but neither tested

rename_merge_headers = {

    'Season' : 'season',
    'Week' : 'week',
    'Game Date' : 'game_date',
    'Game Day' : 'game_day',
    'Local Start Time' : 'local_start_time',
    'Game Length' : 'game_length',
    'Stadium' : 'stadium',
    'Stadium ID' : 'stadium_id',
    'Attendance' : 'attendance',
    'Roof' : 'roof',
    'Surface' : 'surface',
    'Temperature' : 'temperature',
    'Wind' : 'wind',
    'Home Team' : 'home_team',
    'Away Team' : 'away_team',
    'Home Score' : 'home_score_pfr',
    'Away Score' : 'away_score_pfr',
    'Divisional Game' : 'divisional_game',
    'Home Spread' : 'home_spread',
    'Total' : 'total',
    'Home Coach' : 'home_coach',
    'Away Coach' : 'away_coach',
    'Home Coach ID' : 'home_coach_id',
    'Away Coach ID' : 'away_coach_id',
    'Home Starting QB' : 'home_starting_qb',
    'Away Starting QB' : 'away_starting_qb',
    'Home Starting QB ID' : 'home_starting_qb_id',
    'Away Starting QB ID' : 'away_starting_qb_id',
    'Home Won Toss' : 'home_won_toss',
    'Deferred' : 'winner_deferred',
    'Referee' : 'referee',
    'Umpire' : 'umpire',
    'Head Linesman / Down Judge' : 'down_judge',
    'Line Judge' : 'line_judge',
    'Back Judge' : 'back_judge',
    'Side Judge' : 'side_judge',
    'Field Judge' : 'field_judge',

}

merge_df = merge_df.rename(columns=rename_merge_headers)

## prep scrapeR df ##
pbp_team_standard_dict = {

    'ARI' : 'ARI',
    'ATL' : 'ATL',
    'BAL' : 'BAL',
    'BUF' : 'BUF',
    'CAR' : 'CAR',
    'CHI' : 'CHI',
    'CIN' : 'CIN',
    'CLE' : 'CLE',
    'DAL' : 'DAL',
    'DEN' : 'DEN',
    'DET' : 'DET',
    'GB'  : 'GB',
    'HOU' : 'HOU',
    'IND' : 'IND',
    'JAC' : 'JAX',
    'JAX' : 'JAX',
    'KC'  : 'KC',
    'LA'  : 'LAR',
    'LAC' : 'LAC',
    'MIA' : 'MIA',
    'MIN' : 'MIN',
    'NE'  : 'NE',
    'NO'  : 'NO',
    'NYG' : 'NYG',
    'NYJ' : 'NYJ',
    'OAK' : 'OAK',
    'PHI' : 'PHI',
    'PIT' : 'PIT',
    'SD'  : 'LAC',
    'SEA' : 'SEA',
    'SF'  : 'SF',
    'STL' : 'LAR',
    'TB'  : 'TB',
    'TEN' : 'TEN',
    'WAS' : 'WAS',

}


## standardize team names across data sets ##
df_scraper_game['home_team'] = df_scraper_game['home_team'].replace(pbp_team_standard_dict)
df_scraper_game['away_team'] = df_scraper_game['away_team'].replace(pbp_team_standard_dict)

## create new_df ##
merged_df = pd.merge(merge_df,df_scraper_game,on=['season','week','home_team','away_team'],how='left')

final_headers = [

    'type',
    'game_id',
    'state_of_game',
    'game_url',
    'away_team',
    'home_team',
    'week',
    'season',
    'home_score',
    'away_score',
    'game_date',
    'game_day',
    'local_start_time',
    'game_length',
    'stadium',
    'stadium_id',
    'attendance',
    'roof',
    'surface',
    'temperature',
    'wind',
    'away_score_pfr',
    'home_score_pfr',
    'divisional_game',
    'home_spread',
    'total',
    'away_coach',
    'home_coach',
    'away_coach_id',
    'home_coach_id',
    'away_starting_qb',
    'home_starting_qb',
    'away_starting_qb_id',
    'home_starting_qb_id',
    'away_won_toss',
    'winner_deferred',
    'referee',
    'umpire',
    'down_judge',
    'line_judge',
    'back_judge',
    'side_judge',
    'field_judge'

]

merged_df = merged_df[final_headers]
merged_df.to_csv('{0}/reg_game_w_meta.csv'.format(data_folder))
