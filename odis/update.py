#!/usr/bin/env python3.11

from __future__ import print_function
from datetime import date, datetime, timedelta
import os
import requests as req
import pandas as pd
import numpy as np
import bs4
import re


current_year = date.today().year
fields = ['p_match','inns','bat','p_bat','team_bat','bowl','p_bowl','team_bowl',
          'ball','ball_id','outcome','score','out','dismissal','p_out','over','ball','noball','wide','byes','legbyes',
          'cur_bat_runs','cur_bat_bf','cur_bowl_ovr','cur_bowl_wkts','cur_bowl_runs',
          'inns_runs','inns_wkts','inns_balls','inns_runs_rem','inns_balls_rem','inns_rr','inns_rrr','target','max_balls']

def get_livegames():
    url = 'http://static.cricinfo.com/rss/livescores.xml'
    regex = re.findall('(\d+).*guid', req.get(url).text)
    return list(map(int, regex))

def get_matids(min=current_year, max=current_year):
    matids = {}
    url = 'https://stats.espncricinfo.com/indian-domestic-2011/engine/records/team/match_results.html?class=2;id={};type=year'
    for y in range(min, max+1):
        print('Fetching results from', y)
        r = req.get(url.format(y)).text
        d = bs4.BeautifulSoup(r, 'html.parser').select('table')[0].select('tbody')[0].select('tr')
        for ele in d:
            match_id = int(ele.select('td')[-1].select('a')[0].attrs['href'].split('/')[-2].split('-')[-1])
            date = ele.select('td')[-2].text
            if '-' in date: # for date formats: Dec 10-11, 2017
                month_day, year = date.split(', ')
                month_day, _ = month_day.split('-')
                date = month_day + ', ' + year
            date = datetime.strptime(date, '%b %d, %Y')
            matids[match_id] = date
    return matids

def get_match_data(match_id):
    data = {}
    url = 'http://site.web.api.espn.com/apis/site/v2/sports/cricket/8098/playbyplay?contentorigin=espn&event={}&page={}&period={}&section=cricinfo'
    for inn in [1, 2]:
        items = []
        page_count = 20
        for i in range(1, page_count+1):
            while True:
                r = req.get(url.format(match_id, i, inn)).json()
                if 'commentary' in r: 
                    page_count = r['commentary']['pageCount']
                    if i > page_count:
                        return
                    items += r['commentary']['items']
                    if items == []:
                        return
                    break
                else:
                    print('Comms not found')
                    return
        data[inn] = items
    if len(data[1] + data[2]) == 0:
        return
    return data

def sanitize(matdata, match_id):
    data = pd.DataFrame(columns=fields)
    dataind = 0
    for inn in matdata.keys():
        for b in matdata[inn]:
            try:
                r1 = [
                        match_id, 
                        inn,
                        b['batsman']['athlete']['displayName'],
                        b['batsman']['athlete']['id'],
                        b['batsman']['team']['name'],
                        b['bowler']['athlete']['displayName'],
                        b['bowler']['athlete']['id'],
                        b['bowler']['team']['name']
                    ]
                r2 = [
                        b['over']['ball'],
                        b['over']['unique'],
                        b['playType']['description'],
                        b['scoreValue'],
                        b['dismissal']['dismissal'],
                        b['dismissal']['type'],
                        b['dismissal']['batsman']['athlete']['id'],
                        b['over']['number'],
                        b['over']['ball'],
                        b['over']['noBall'],
                        b['over']['wide'],
                        b['over']['byes'],
                        b['over']['legByes']
                    ]
                r3 = [
                        b['batsman']['totalRuns'],
                        b['batsman']['faced'],
                        b['bowler']['overs'],
                        b['bowler']['wickets'],
                        b['bowler']['conceded']
                    ]
            except:
                continue
            i = b['innings']
            if inn == 1:
                rr = i.get('runRate', None)
                target = ''
                rruns = ''
                rrr = ''
            elif inn == 2:
                rr = i.get('runRate', None)
                target = i['target']
                rruns = i.get('remainingRuns', 0)
                rrr = i.get('requiredRunRate', 0.00)
            r4 = [
                    i['runs'],
                    i['wickets'],
                    i['balls'],
                    rruns,
                    i['remainingBalls'],
                    rr,
                    rrr,
                    target,
                    i['ballLimit']
                ]
            data.loc[dataind] = r1 + r2 + r3 + r4
            dataind += 1
    return data

def add_metadata(df, mat):
    matchinfo = pd.DataFrame(columns=['p_match','date','year','ground','country','winner','toss','competition'])
    playerinfo = pd.DataFrame(columns=['p_player','bat_hand','bowl_style','bowl_kind'])
    r = req.get('https://www.espncricinfo.com/ci/engine/match/{}.json'.format(mat)).json()
    dat = r['match']
    t1_name = dat['team1_name']
    t2_name = dat['team2_name']
    t1_id = int(dat['team1_id'])
    t2_id = int(dat['team2_id'])
    toss_winner_id = int(dat["toss_winner_team_id"])
    winner_id = int(dat["winner_team_id"])
    res_type = dat['result_short_name']
    ground = dat["ground_name"]
    date = dat["start_date_raw"]
    country = dat['country_name']
    year = date.split('-')[0]
    try:
        if r['series'][0]['class_id'] == 2:
            comp = r['series'][0]['short_alternate_name']
            if comp == '':
                comp = r['series'][0]['series_short_name']
            elif comp == None:
                comp = r['series'][0]['series_short_name']
            elif comp == '':
                comp = r['series'][0]['series_name']
        else:
            comp = 'ODI'
    except:
        comp = '-'
    toss_winner = t1_name if toss_winner_id == t1_id else t2_name
    if winner_id == 0:
        winner = '-'
    else:
        winner = t1_name if winner_id == t1_id else t2_name
    matchinfo.loc[mat] = [mat, date, year, ground, country, winner, toss_winner, str(comp.strip())]
    pinfo = r['team'][0]['player'] + r['team'][1]['player']
    for play in pinfo:
        key = str(play['object_id'])
        batst = play.get('batting_style', '-')
        batst = batst.upper() if batst != None else '-'
        bowlst = play.get('bowling_style', '-')
        bowlst = bowlst.upper() if bowlst != None else '-'
        bowlk = play.get('bowling_pacespin', '-')
        playerinfo.loc[key] = [key,batst,bowlst,bowlk]
    df = df.merge(matchinfo, on='p_match')
    df = df.merge(playerinfo[['p_player','bat_hand']],left_on='p_bat',right_on='p_player')
    df = df.merge(playerinfo[['p_player','bowl_style','bowl_kind']],left_on='p_bowl',right_on='p_player')
    df['batruns'] = df.score - df.noball - df.wide - df.byes - df.legbyes
    df['ballfaced'] = 1-np.sign(df.wide)
    df['bowlruns'] = df.score - df.byes - df.legbyes
    df = df.drop(columns = ['p_player_x','p_player_y'])
    df['bat_out'] = df.p_bat == df.p_out
    return df

def main():
    file = 'odi_bbb.csv'
    idx = 0
    livegames = get_livegames()
    if os.path.isfile(file):
        df = pd.read_csv(file)
        idx = df.last_valid_index() + 1
        processed_ids = df.p_match.unique()
        max_date = datetime.strptime(df.date.max(), '%Y-%m-%d')
        ids = get_matids(max_date.year, current_year) # start to end (inclusive)
        queue = []
        for k, v in ids.items():
            if v > (max_date - timedelta(days=3)):
                queue.append(k)
        match_queue = np.array(queue)
        matids = match_queue[~np.in1d(match_queue, processed_ids, assume_unique=True)]
    else:
        matids = get_matids(2005, current_year).keys() # start to end (inclusive)
    to_fetch = len(matids)
    for cur, id in enumerate(matids):
        cur = cur + 1
        if cur % 1000 == 0:
            print('Updating list of ongoing matches every 1000 ids')
            livegames = get_livegames()
        if id in livegames:
            print('Skipping ongoing match', id)
            continue
        print('\n{}/{}'.format(cur, to_fetch))
        print('Getting', id)
        matdata = get_match_data(id)
        if matdata == None:
            print('No match data found', id)
            continue
        print('Sanitizing', id)
        out = sanitize(matdata, id)
        if len(out.index) == 0:
            print('Abandoned match(?)', id)
            continue
        print('Fetching metadata', id)
        out = add_metadata(out, id)
        out.index += idx
        idx = out.last_valid_index() + 1
        print('Writing to csv', id)
        out.to_csv(file, mode='a', header=not os.path.isfile(file))
        print('Done')
    print('Finished')

def start():
    try:
        main()
    except Exception:
        start()
    
start()
