#!/usr/bin/env python3

import requests
import json
import string
import csv
import os
import re
from datetime import datetime


FULL_MEMBERS = ['Afghanistan', 'Australia', 'Bangladesh', 'England', 'India', 'Ireland',
        'New Zealand', 'Pakistan', 'South Africa', 'Sri Lanka', 'West Indies', 'Zimbabwe']
BASE_URL = 'https://scores.bcci.tv/feeds-international/scoringfeeds/'
error_cnt = []


def fetch_json(id, endpoint):
    global error_cnt
    r = requests.get(BASE_URL + str(id) + '-' + endpoint + '.js')
    ret = None
    if r.status_code == 200:
        start = r.text.find('(')
        end = r.text.rfind(')')
        ret = json.loads(r.text[start+1:end])
    if ret == None:
        if endpoint == "matchsummary":
            error_cnt.append(id)
            print(str(id) + " was not found")
    return ret

def get_match(id):
    match = []
    summary = fetch_json(id, 'matchsummary')
    if summary == None:
        return
    summary = summary['MatchSummary'][0]
    match_id = summary['MatchID']
    team_1 = summary['Team1']
    team_2 = summary['Team2']
    if summary['IsMatchEnd'] == 0:
        print('Skipping live match ' + team_1 + ' v ' + team_2)
        return
    ipl = 0
    if "ipl" in summary['CompetitionName'].lower():
        ipl = 1
    if ipl == 0 and (team_1 not in FULL_MEMBERS and team_2 not in FULL_MEMBERS):
        print('Skipping ' + team_1 + ' v ' + team_2)
        return
    date = datetime.strptime(summary['MatchDate'], '%d %b %Y').strftime('%Y-%m-%d')
    format = summary['MatchType']
    ground = summary['GroundName']
    _first_batting = summary['FirstBattingTeam']
    _second_batting = summary['SecondBattingTeam']
    squad = fetch_json(id, 'squad')
    for i in [1, 2, 3, 4]:
        innings = fetch_json(id, 'Innings' + str(i))
        if innings == None:
            continue
        print("Match: " + str(id) + ", Innings: " + str(i))
        innings = innings['Innings' + str(i)]
        wheel = innings['WagonWheel']
        over_hist = innings['OverHistory']
        ings = i
        batting_team = _first_batting if i == 1 else _second_batting
        bowling_team = _second_batting if i == 1 else _first_batting
        actual_delivery_count = 0
        for delivery in over_hist:
            actual_delivery_count += 1
            _ball_id = delivery['BallID']
            batter   = delivery['BatsManName']
            bowler   = delivery['BowlerName']
            batter_type = None
            bowler_type = None
            __squad = squad['squadA'] if batting_team == team_1 else squad['squadB']
            for player in __squad:
                if delivery['StrikerID'] == player['PlayerID']:
                    batter_type = 'R' if 'right' in player['BattingType'].lower() else 'L'
            __squad = squad['squadB'] if batting_team == team_1 else squad['squadA']
            for player in __squad:
                if delivery['BowlerID'] == player['PlayerID']:
                    table = str.maketrans('', '', string.ascii_lowercase + ' ')
                    bowler_type = player['BowlingProficiency'].translate(table).strip()
            over     = delivery['OverNo']
            ball     = delivery['BallNo']
            dismissal_type = delivery['WicketType']
            runs_scored = delivery['ActualRuns']
            extras = delivery['Extras']
            no_ball = delivery['IsNoBall']
            wide = delivery['IsWide']
            bye = delivery['IsBye']
            leg_bye = delivery['IsLegBye']
            shot_type = delivery['ShotType']
            shot_angle = None
            shot_ratio = None
            xpitch = delivery['Xpitch']
            ypitch = delivery['Ypitch']
            length = None
            line = None
            if 'Commentry' in delivery and delivery['Commentry'] != '':
                commentary = delivery['Commentry'].split(',')
                if len(commentary) >= 4:
                    length = commentary[1].strip()
                    line = commentary[2].strip()
            for obj in wheel:
                _wheel_id = obj['BallID']
                if _wheel_id == _ball_id:
                    shot_angle = obj['FielderAngle']
                    shot_ratio = obj['FielderLengthRatio']
            match.append([match_id, team_1, team_2, date, format, ground, ings,
                batting_team, bowling_team, batter, bowler, batter_type,
                bowler_type, over, ball, dismissal_type, runs_scored, xpitch,
                ypitch, length, line, shot_type, shot_angle, shot_ratio, ipl,
                actual_delivery_count, extras, no_ball, wide, bye, leg_bye,])
    return match

def main():
    global error_cnt
    file = 'out.csv'
    idx = 2
    missing_ids = set()
    fields = ['MatchID', 'Team1', 'Team2', 'Date', 'Format', 'Ground', 'Innings',
            'Batting Team', 'Bowling Team', 'Batter', 'Bowler', 'Batter Type', 
            'Bowler Type', 'Over', 'Ball', 'Dismissal Type', 
            'Runs scored off bat', 'Xpitch', 'Ypitch', 'Length', 'Line', 
            'Shot Type', 'Shot Angle', 'Shot Ratio', 'IPL', 'Real ball count',
            'Extras', 'IsNoBall', 'IsWide', 'IsBye', 'IsLegBye']
    if os.path.isfile(file):
        with open(file, 'r') as f:
            for line in f:
                id = re.match(r'(^\d+)', line)
                if id:
                    id = int(id.group(0))
                    missing_ids.add(id)
                    idx = id+1
        if missing_ids:
            missing_ids = sorted(set(range(min(missing_ids), max(missing_ids) + 1)).difference(missing_ids))[-min(20, len(missing_ids)):]
    else:
        with open(file, 'a') as f:
            f.write(','.join(fields) + '\n')
    while len(error_cnt) < 100:
        if missing_ids:
            match = get_match(missing_ids.pop(0))
        else:
            match = get_match(idx)
            idx += 1
        if match:
            with open(file, 'a') as f:
                w = csv.writer(f)
                w.writerows(match)
        if len(error_cnt) == 99:
            if sorted(error_cnt) == list(range(min(error_cnt), max(error_cnt)+1)):
                error_cnt.clear()


main()
