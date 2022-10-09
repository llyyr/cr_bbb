#!/usr/bin/env python3

import os
from geopy import Nominatim # pip3 install geopy
import numpy as np
import requests
import re
import pandas as pd # Need pandas version 1.3


pd.options.display.float_format = '{:.2f}'.format
geolocator = Nominatim(user_agent="geoapiExercises")


def helper1(inp):
    f = lambda x: re.findall('to.+', x)[0].split(",")[1].lower()
    try:
        return f(inp)
    except IndexError as e:
        return np.nan

def helper2(inp):
    f = lambda x: re.findall('to.+', x)[0].split(",")[2].split("for")[0].lower()
    try: 
        return f(inp)
    except IndexError as e:
        return np.nan

def helper3(inp):
    f = lambda x: re.findall("\. (.+)", re.findall('to.+', x)[0].split(",")[0])[0].lower()
    try: 
        return f(inp)
    except IndexError as e:
        return np.nan

def get_variation(x):
    variations = ["stock", "googly", "seaming away", "off break", "off cutter", 
                 "quicker", "arm", "in-swinging", "leg spinner", "slower", "out-swinging", "seaming in", "leg cutter"]
    for i in variations:
        if i in x:
            return i
    return "stock"

def get_length(x):
    lengths = ["length ball", "back of a length", "half volley", "full toss", "yorker", "short", "bouncer"]
    for i in lengths:
        if i in x:
            return i
    return np.nan

def get_area(x):
    try:
        areas = ["miss", "cover", "mid wicket", "long off", "mid off", "square leg",
                 "point", "third man", "fine leg", "gully", "third man", "mid on", "long on", "short leg",
                "back to bowler", "left", "slip"]
        for i in areas:
            if i in x:
                return i
        return np.nan
    except TypeError as e:
        return np.nan

def get_control(x):
    try:
        controls = ["under control", "well timed", "mis-timed", "edge", "miss"]
        for i in controls:
            if i in x:
                return i
        return "under control"
    except TypeError as e:
        return np.nan

def get_line(x):
    try:
        lines = ["wide outside off", "outside off", "off", "down leg", "leg", "middle"]
        for i in lines:
            if i in x:
                return i
        return np.nan
    except TypeError as e:
        return np.nan

def get_foot(x):
    feet = ["no foot movement", "front foot", "back foot", "down the track", "backing away", "in front", "deep in crease",
           "ducked"]
    
    try:
        for i in feet:
            if i in x:
                return i
        return np.nan
    except TypeError as e:
        return np.nan

def get_fielder(x):
    try: 
        text = re.findall('fielded.+|caught.+|dropped.+',x)[0].split('by')[-1].strip().replace('.','').replace(',','')
        if len(text.split(' '))>1:
            text = text.split(' ')[0]
        return text
    except IndexError as e:
        return np.nan

def get_fielder_action(inp):
    f1 = lambda x: re.findall('fielded.+|caught.+|dropped.+',x)[0].split('by')[0].strip()
    try: 
        text = f1(inp)
        if len(text.split(' '))>1:
            text = text.split(' ')[0].replace('.','').replace(',','')
        return text
    except IndexError as e:
        return ""

skip = ['Caribbean Premier League', "'A' One-Day Quad-Series", 'England Domestic T20', 'JLT One-Day Cup', 'Sheffield Shield']
country_cache = {'Central Broward Regional Park Stadium Turf Ground': 'United States', 'Sydney': 'Australia', 'Guildford': 'United Kingdom', 'Durban': 'South Africa', 'Cape Town': 'South Africa', 'Pune': 'India', 'Durham': 'United States', 'Moe': 'United States', 'Nelson': 'New Zealand', 'Dublin': 'Ireland', 'Grenada': 'Grenada', 'Hamilton': 'Canada', 'Mumbai': 'India', 'Hyderabad': 'India', 'Christchurch': 'New Zealand', 'Visakhapatnam': 'India', 'Nettleworth': 'United Kingdom', 'Belfast': 'United Kingdom', 'Port of Spain': 'Trinidad and Tobago', 'Karachi': 'Pakistan', 'Brisbane': 'Australia', 'Scarborough': 'United Kingdom', 'Colombo': 'Sri Lanka', 'Dunedin': 'New Zealand', 'Perth': 'Australia', 'Docklands': 'Australia', 'Coffs Harbour': 'Australia', 'Amstelveen': 'Netherlands', 'Basseterre': 'Saint Kitts and Nevis', 'Multan': 'Pakistan', 'Kolkata': 'India', 'Bulawayo': 'Zimbabwe', 'Antigua': 'Antigua and Barbuda', 'Eastbourne': 'United Kingdom', 'Neath': 'United Kingdom', 'Bankstown': 'Australia', 'Dehradun': 'India', 'Thiruvananthapuram': 'India', 'Adelaide': 'Australia', 'Beckenham': 'United Kingdom', 'Chelmsford': 'United Kingdom', 'Southampton': 'United Kingdom', 'Hobart': 'Australia', 'Port Elizabeth': 'South Africa', 'Galle': 'Germany', 'Clontarf Cricket Club': 'Ireland', 'Sylhet Divisional Stadium': 'Bangladesh', 'Bengaluru': 'India', 'Auckland': 'New Zealand', 'Southport': 'United Kingdom', 'Guwahati': 'India', 'Lucknow': 'India', 'Sedbergh': 'United Kingdom', 'Nagpur': 'India', 'Radlett': 'United Kingdom', 'Cheltenham': 'United Kingdom', 'Kanpur': 'India', 'Melbourne': 'Australia', 'Delhi': 'India', 'East London': 'South Africa', 'Lahore': 'Pakistan', 'Sharjah': 'United Arab Emirates', 'Drummoyne': 'Australia', 'Centurion': 'South Africa', 'Abu Dhabi': 'United Arab Emirates', 'Newport': 'United States', 'Ahmedabad': 'India', 'Kandy': 'Sri Lanka', 'Derby': 'United Kingdom', 'The Ageas Bowl': 'United Kingdom', 'Gros Islet': 'Saint Lucia', 'Utrecht': 'Netherlands', 'Gosforth': 'United Kingdom', 'Derry': 'United Kingdom', 'Jamaica': 'Jamaica', 'London': 'United Kingdom', 'Ranchi': 'India', 'York': 'United Kingdom', 'Alice Springs': 'Australia', 'Cuttack': 'India', 'Geelong': 'Australia', 'Birmingham': 'United Kingdom', 'Liverpool ': 'United Kingdom', 'Townsville': 'Australia', 'Indore': 'India', 'Wollongong': 'Australia', 'Taunton': 'United Kingdom', 'Harare': 'Zimbabwe', 'Nottingham': 'United Kingdom', 'Wellington': 'New Zealand', 'Rajkot': 'India', 'Arundel': 'United Kingdom', 'Leeds': 'United Kingdom', 'Mirpur': 'Pakistan', 'Trinidad': 'Trinidad and Tobago', 'Chennai': 'India', 'Worcester': 'United States', 'Canberra': 'Australia', 'Al Amarat': 'Oman', 'Cairns': 'Australia', 'North Sydney': 'Australia', 'Dubai': 'United Arab Emirates', 'Potchefstroom': 'South Africa', 'Paarl': 'South Africa', 'ANZ Stadium': 'Australia', 'Bridgetown': 'Barbados', 'Manchester': 'United Kingdom', 'Bristol': 'United Kingdom', 'The Hague': 'Netherlands', 'Grantham': 'United Kingdom', 'Canterbury': 'United Kingdom', 'St. Kilda': 'United Kingdom', 'Hove': 'United Kingdom', 'Hambantota': 'Sri Lanka', 'Dambulla': 'Sri Lanka', 'Northwood': 'United States', 'Gold Coast': 'Australia', 'Greater Noida': 'India', 'Chesterfield': 'United States', 'Edinburgh': 'United Kingdom', 'Zahur Ahmed Chowdhury Stadium': 'Bangladesh', 'Bay Oval. Mount Maunganui': 'New Zealand', 'Harare Sports Club': 'Zimbabwe', 'Cardiff': 'United Kingdom', 'Launceston': 'Australia', 'Dominica': 'Dominican Republic', 'Jaipur': 'India', 'Johannesburg': 'South Africa', 'Chattogram': 'Bangladesh', 'Rotterdam': 'Netherlands', 'Blackpool': 'United Kingdom', 'Leicester': 'United Kingdom', 'Dharamsala': 'India', 'Guyana': 'Guyana', 'Rawalpindi': 'Pakistan', 'Northampton': 'United Kingdom', 'Bloemfontein': 'South Africa', 'Mohali': 'India', 'Napier': 'New Zealand'}
def get_bbb(fixtureID):
    global country_cache
    scorecard = requests.get("https://apiv2.cricket.com.au/web/views/scorecard?FixtureId=" + str(fixtureID) + "&jsconfig=eccn:true&format=json").json()
    try: 
        if not 'fixture' in scorecard and not 'players' in scorecard:
            print('Invalid match ' + str(fixtureID))
            return
        if scorecard['fixture']['isWomensMatch'] or scorecard['fixture']['competition']['isWomensCompetition']:
            print('Skipping womens match', fixtureID)
            return
        if not scorecard['fixture']['isCompleted']:
            print('Skipping incomplete match', fixtureID)
            return
        for tourney in skip:
            if tourney.lower() in scorecard['fixture']['competition']['name'].lower():
                print('Skipping', tourney)
                return
    except KeyError as e:
        print('KeyError', fixtureID)
        return
    try:
        fixture_id = scorecard['fixture']['id']
        team_1 = scorecard['fixture']['homeTeam']['name'].replace(' Men', '')
        if len(team_1.split()) >= 2 and team_1.split()[-1] == 'A':
            print('Skipping \'A\'', fixtureID)
            return
        if len(team_1.split()) >= 2 and 'U19' in team_1:
            print('Skipping U19', fixtureID)
            return
        _team_1_id = scorecard['fixture']['homeTeam']['id']
        team_2 = scorecard['fixture']['awayTeam']['name'].replace(' Men', '')
        _team_2_id = scorecard['fixture']['awayTeam']['id']
        format = scorecard['fixture']['competition']['formats'][0]['displayName'].split()[0]
        if format not in ['Test', 'ODI', 'T20', 'One-Day', 'First-Class']:
            print('Skipping invalid format', fixtureID)
            return
        ground = scorecard['fixture']['venue']['name']
        country = np.nan
        try:
            if ground != 'TBC':
                if ground not in country_cache:
                    if len(ground.split(', ')) >= 2:
                        ground = ground.split(', ')[-1]
                    country = geolocator.geocode(ground, language='en').raw['display_name'].split(', ')[-1]
                    country_cache[ground] = country
                else:
                    country = country_cache[ground]
        except:
            pass
    except KeyError as e:
        print('KeyError', fixtureID)
        return
    players = scorecard['players']
    bbb = pd.DataFrame()
    num_inns = 4 if format in ['Test', 'First-Class'] else 2
    for inning in np.arange(1, num_inns+1):
        root = requests.get("https://apiv2.cricket.com.au/web/views/comments?FixtureId="+ str(fixtureID)+ "&jsconfig=eccn:true&OverLimit=400&lastOverNumber=&IncludeVideoReplays=false&format=json&inningNumber=" + str(inning)).json()
        if not 'inning' in root:
            print('Skipping', fixtureID)
            return
        print(fixtureID, inning)
        info = []
        try:
            innings = root['inning']['inningNumber']
            batting_team_id = root['inning']['battingTeamId']
            bowling_team_id = root['inning']['bowlingTeamId']
            batting_team = team_1 if batting_team_id == _team_1_id else team_2
            bowling_team = team_2 if bowling_team_id == _team_2_id else team_1
        except KeyError as e:
            print('KeyError', fixtureID)
            return
        for over in root['inning']['overs']:
            over_num = over['overNumber']
            if over_num == 0:
                continue
            ball_num = len(over['balls']) + 1
            for ball in over['balls']:
                ball_num -= 1
                try:
                    match_date = pd.to_datetime(ball['ballDateTime']).date()
                except:
                    match_date = np.nan
                
                is_wicket = ball['isWicket']
                
                try:
                    bowler_id = int(ball['bowlerPlayerId'])
                except KeyError as e:
                    bowler_id = np.nan
                    
                try:    
                    batsman_id = int(ball['battingPlayerId'])
                except KeyError as e:
                    batsman_id = np.nan
                batsman = np.nan
                batsman_hand = np.nan
                bowler = np.nan
                bowler_hand = np.nan
                bowler_type = np.nan
                dismissal_player = np.nan
                
                try:
                    dismissal_type = ball['dismissalTypeId']
                    dismissal_player_id = ball['dismissalPlayerId']
                except KeyError as e:
                    dismissal_type = np.nan
                    dismissal_player_id = np.nan

                for player in players:
                    if player['id'] == bowler_id:
                        bowler = player['displayName']
                        bowler_hand = player['bowlingHand'] if 'bowlingHand' in player else np.nan
                        bowler_type = player['bowlingType'] if 'bowlingType' in player else np.nan
                    elif player['id'] == batsman_id:
                        batsman = player['displayName']
                        batsman_hand = player['battingHand'] if 'battingHand' in player else np.nan
                    if dismissal_player_id == player['id']:
                        dismissal_player = player['displayName']

                try:    
                    shot_angle = ball['shotAngle']
                except KeyError as e:
                    shot_angle = np.nan
                
                try:
                    shot_magnitude = ball['shotMagnitude']
                except KeyError as e:
                    shot_magnitude = np.nan
                
                try:
                    fielding_position = ball['fieldingPosition']
                except KeyError as e:
                    fielding_position = np.nan
                
                try:
                    runs_conceded = ball['runsConceded']
                except KeyError as e:
                    runs_conceded = np.nan
                
                try:
                    extras = ball['extras']
                except KeyError as e:
                    extras = np.nan
                
                runs = ball['runs']
                
                try:
                    runs_scored = ball['runsScored'] 
                except KeyError as e:
                    runs_scored = np.nan
                    
                try:
                    timestamp = ball['ballDateTime'] 
                except KeyError as e:
                    timestamp = np.nan
                
                for comment in ball['comments']:
                    if comment['commentTypeId'] in ['EndOfOver','StartOfInning']:
                        continue
                    else:
                        commentary = comment['message']
                        
                if len(commentary) == 0:
                    break
                    
                if commentary.split()[0] != "jjjj":
                    commentary = commentary.replace("L.B.W.", "LBW").replace("Bowled.", "Bowled").replace("Run out.", "Run Out")
                    commentary = commentary.replace("Caught.", "Caught").replace("Stumped.", "Stumped").replace("REFERRAL.", "")
                    commentary = commentary.replace("NEW BALL.", "").replace("FREE HIT.", "")

                fields = {'fixtureId': fixture_id, 'team1': team_1, 'team2': team_2,
                          'matchDate': match_date, 'format': format, 'ground': ground,
                          'country': country, 'inns': innings, 'battingTeam': batting_team,
                          'bowlingTeam': bowling_team, 'batsman': batsman, 'bowler': bowler,
                          'batsmanHand': batsman_hand, 'bowlerHand': bowler_hand,
                          'bowlerType': bowler_type, 'over': over_num, 'ball': ball_num,
                          'dismissalType': dismissal_type,
                          'dismissedPlayer': dismissal_player, "shot_angle":shot_angle,
                          "shot_magnitude": shot_magnitude,
                          "fielding_position": fielding_position,
                          "runs_conceded":runs_conceded, "runs": runs,
                          "runs_scored":runs_scored, "extras":extras, 
                          "is_wicket":is_wicket,
                          "commentary": commentary, "timestamp": timestamp}
                info.append(fields)
        
        info = pd.DataFrame(info)
        bbb = pd.concat((bbb, info))
        if bbb.empty: return
        try:
            bbb["len/var"] = bbb["commentary"].apply(helper3)
            bbb["shot"] = bbb["commentary"].apply(helper1)
            bbb["zone"] = bbb["commentary"].apply(helper2)
            bbb["shot_type"] = bbb["shot"].apply(lambda x: x.split()[-1] if type(x)!=float else np.nan)
            bbb["variation"] = bbb["len/var"].apply(lambda x: get_variation(x) if type(x)!=float else np.nan)
            bbb["length"] = bbb["len/var"].apply(lambda x: get_length(x) if type(x)!=float else np.nan)
            bbb["area"] = bbb["zone"].apply(get_area)
            bbb["control"] = bbb["zone"].apply(get_control)
            bbb["line"] = bbb["shot"].apply(get_line)
            bbb["foot"] = bbb["shot"].apply(get_foot)
            bbb['fielder_action'] = bbb['commentary'].apply(get_fielder_action)
            bbb['fielder'] = bbb['commentary'].apply(get_fielder)
        except:
            print('Failed to parse commentary for', fixtureID)
    return(bbb)

def main():
    idx = 0
    file = 'full.csv'
    missing_ids = set()
    if os.path.isfile(file):
        with open(file, 'r') as f:
            for line in f:
                id = re.match(r'(^\d+)', line)
                if id:
                    id = int(id.group(0))
                    missing_ids.add(id)
                    idx = id+1
        if missing_ids:
            missing_ids = sorted(set(range(min(missing_ids), max(missing_ids) + 1)).difference(missing_ids)) #[-min(20, len(missing_ids)):]
            missing_ids = list(filter(lambda x: x > 5400, missing_ids))
    while True:
        if missing_ids:
            match = get_bbb(missing_ids.pop(0))
        else:
            match = get_bbb(idx)
            idx += 1
        if type(match) != type(None):
            match.to_csv(file, mode='a', header=not os.path.isfile(file), index=False)

main()
