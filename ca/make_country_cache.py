import pandas as pd
import os
from geopy import Nominatim # pip3 install geopy

geolocator = Nominatim(user_agent="geoapiExercises")
data = []
country_cache = {'Central Broward Regional Park Stadium Turf Ground': 'United States'}
def filter(ground):
    global country_cache
    if ground != 'TBC':
        if ground not in country_cache:
            print(ground)
            if len(ground.split(', ')) >= 2:
                ground = ground.split(', ')[-1]
            country = geolocator.geocode(ground, language='en').raw['display_name'].split(', ')[-1]
            country_cache[ground] = country
        else:
            country = country_cache[ground]

df = pd.read_csv(r'full.csv')
data.extend(df['ground'].tolist())

#Fetch unique values with Set
data_unique = list(set(data))
data_unique_string = map(str, data_unique)
for item in data_unique_string:
    filter(item)
print(country_cache)
