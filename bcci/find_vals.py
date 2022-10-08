#!/usr/bin/env python3

import requests
import json
import string
import csv
import os


FULL_MEMBERS = ['Afghanistan', 'Australia', 'Bangladesh', 'England', 'India', 
        'Ireland', 'New Zealand', 'Pakistan', 'South Africa', 'Sri Lanka', 
        'West Indies', 'Windies', 'Zimbabwe']
BASE_URL = 'https://scores.bcci.tv/feeds-international/scoringfeeds/'
NOT_FOUND_IDX = []


def fetch_json(id, endpoint):
    global NOT_FOUND_IDX
    r = requests.get(BASE_URL + str(id) + '-' + endpoint + '.js')
    ret = None
    if r.status_code == 200:
        start = r.text.find('(')
        end = r.text.rfind(')')
        ret = json.loads(r.text[start+1:end])
    if ret == None:
        if endpoint == "matchsummary":
            NOT_FOUND_IDX.append(id)
            print(str(id) + " was not found")
    return ret

def main():
    match = set()
    for id in range(2, 700):
        summary = fetch_json(id, 'matchsummary')
        if summary == None:
            continue
        summary = summary['MatchSummary'][0]
        team_1 = summary['Team1']
        team_2 = summary['Team2']
        match.add(team_1)
        match.add(team_2)
        print(id, match)


main()


# {'India Legends', 'Delhi Capitals', 'United Arab Emirates', 'Barbados Women', 'India U19', 'Reliance One A', 'New Zealand', 'South Africa Legends', 'Nepal (Women)', 'Australia', 'Pakistan Women', 'Supernovas', 'United Arab Emirates (Women)', 'Oman (Women)', 'Sri Lanka Women', 'Hongkong (Women)', 'Namibia', 'Royal Challengers Bangalore', 'Bangladesh Women', 'Uganda U19', 'England Women', 'Sri Lanka', 'Durham', 'Ireland U19', 'Kuwait', 'South Africa U19', 'Chennai Super Kings', 'West Indies Legends', 'Bangladesh U19', 'West Indies Women', 'Singapore (Women)', 'Qatar (Women)', 'Sussex', 'Netherlands', 'New Zealand Women', 'Afghanistan', 'Mumbai Indians', 'Kuwait (Women)', 'South Africa Women', 'Ireland', 'Bahrain (Women)', 'Gujarat Titans', 'Reliance One B', 'Sunrisers Hyderabad', 'India Women', 'Trailblazers', 'England U19', 'Australia Women', 'Australia Legends', 'Australia U19', 'India', 'Lucknow Super Giants', 'Punjab Kings', 'Kolkata Knight Riders', 'Bhutan (Women)', 'Kent Second XI', 'Malaysia (Women)', 'Zimbabwe', 'Velocity', 'Sri Lanka Legends', 'Singapore', 'Hong Kong', 'West Indies', 'South Africa', 'Rajasthan Royals', 'Bangladesh', 'Scotland', 'Pakistan', 'England'}
