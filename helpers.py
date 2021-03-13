import configparser
import requests
import json
from datetime import datetime
from matplotlib import pyplot as plt
import os
 
# Function for getting api_key from config.ini
def get_api_key():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config['openweathermap']['api']

def get_city_state(coords):
    print(coords)
    full_list = json.loads(us_cities.json)
    print(full_list)


# Function to use api_key and location 
# This will also be used for current forecast on main page
def get_weather(api_key, location):
    url = "https://api.openweathermap.org/data/2.5/weather?q={}&appid={}&units={}".format(location, api_key, "imperial")
    r = requests.get(url)
    return r.json()

def get_coords(api_key, location):
    lat_long = []

    weather = get_weather(api_key, location)
    print(weather)
    lat_long.append(weather["coord"]["lat"])
    lat_long.append(weather["coord"]["lon"])

    return(lat_long)

# Function to get the rest of the information (hourly, weekly, etc.)
# Also gets the city and state name from us_cities.json
# Second part to do
def one_call_info(api_key, location):
    city_coords = get_coords(api_key, location)

    # Dict to hold coordinates
    coords = {}
    coords["lat"] = city_coords[0]
    coords["long"] = city_coords[1]

    # Make api call using coordinates
    url = "https://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&exclude=minutely&appid={}&units=imperial".format(coords["lat"], coords["long"], api_key)
    r = requests.get(url)
    weather_all = r.json()

    return weather_all

# Current days info 
def get_info_current(weather_all):
    current = {}

    # Visual day information
    current['temp'] = weather_all['current']['temp']
    current['feel'] = weather_all['current']['feels_like']
    current['hum'] = weather_all['current']['humidity']
    current['desc'] = weather_all['current']['weather'][0]['description'].title()
    current['icon'] = weather_all['current']['weather'][0]['icon']
    current['img'] = "http://openweathermap.org/img/wn/" + current['icon'] + "@2x.png"

   
    # Written day information
    current['visibility'] = weather_all['current']['visibility']
    current['wspeed'] = weather_all['current']['wind_speed']
    current['sunrise'] = datetime.fromtimestamp(weather_all['daily'][0]['sunrise']).strftime("%-I:%M %p")
    current['sunset'] = datetime.fromtimestamp(weather_all['daily'][0]['sunset']).strftime("%-I:%M %p")
    current['weekday'] = datetime.fromtimestamp(weather_all['current']['dt']).strftime("%A")
    current['date'] = datetime.fromtimestamp(weather_all['current']['dt']).strftime('%m/%d/%Y')
    current['datelong'] = datetime.fromtimestamp(weather_all['current']['dt']).strftime('%B %-d, %Y')

    # Get any weather warnings in effect
    string = json.dumps(weather_all)
    warnings = json.loads(string)
    if 'alerts' in warnings:
        current['event'] = warnings['alerts'][0]['event']
        current['eventdesc'] = warnings['alerts'][0]['description']

    # Weather icon for day
    current['img'] = "http://openweathermap.org/img/wn/" + current['icon'] + "@2x.png"

    with open('one_call_current.json', 'w') as f:
        json.dump(weather_all, f, indent = 4)

    return(current)

# Hourly info
# To be used in graph on main page
# Covers up to 48 hours, uses 12
def get_info_hourly(weather_all):
    hourly = weather_all["hourly"]

    # List to store dicts of hourly weather info
    hourly_forecast = []

    for hour in hourly:
        temp_dict = {}

        temp_dict["temp"] = hour["temp"]
        temp_dict["feels"] = hour["feels_like"]
        temp_dict["hum"] = hour["humidity"]

        # Use function to match timezone to city
        temp_dict["dt"] = hour['dt'] 
        temp_dict["pop"] = hour["pop"]

        hourly_forecast.append(temp_dict)

    return(hourly_forecast)

# Hourly Graph
# Create line graph of hourly data for 24 hours
    # Different colors for different data points
    # Convert epoch time to hourly am/pm
def graph_hourly(hourly_forecast):
    # y-axis
    graph_temp = []
    graph_feels = []
    graph_humidity = []
    graph_chance_rain = []

    # x-axis
    graph_hours = []

    # Fill lists with data, convert hours from UTC to hour am/pm
    for item in hourly_forecast[:12]:
        graph_temp.append(item['temp'])
        graph_feels.append(item['feels'])
        graph_humidity.append(item['hum'])
        graph_chance_rain.append((item['pop'] * 100))
        
        graph_hours.append(datetime.fromtimestamp(item['dt']).strftime("%-I %p"))
        
    # Create simple chart of both
    fig = plt.figure(dpi=128, figsize=(6,4))
    plt.plot(graph_hours, graph_chance_rain, c='blue', label='Chance of Rain')
    plt.plot(graph_hours, graph_humidity, c='red', label='Humidity')
    plt.fill_between(graph_hours, graph_chance_rain, facecolor='blue', alpha=0.1)
    plt.ylim(0,100)
    plt.margins(x=0)
    plt.legend(loc='upper right')

    # Format plot for rain probability
    plt.title('12 Hour Forecast')
    plt.tick_params(axis='x', which='major', labelsize=6, labelrotation=310)

    my_path = os.path.abspath(__file__)
    plt.savefig('/home/vuhnilaguhrila/the_odin_project/weather_api/weather_app/static/css/hourly_forecast.png')


# Weekly info
def get_info_daily(weather_all):
    daily = (weather_all["daily"])

    daily_forecast = []

    for day in daily:
        temp_dict = {}

        # List to store temps to find high and low
        temps = []
        
        # Find high and low temp
        for i in day["temp"].values():
            temps.append(i)

        temp_dict["high"] = int(max(temps))
        temp_dict["low"] = int(min(temps))

        # Find average temp
        total = 0
        for num in temps:
            total += num
        total = total / len(temps)
        temp_dict['avg'] = int(total)

        temp_dict["dt"] = day["dt"]
        temp_dict["icon"] = day["weather"][0]["icon"]
        temp_dict["description"] = day["weather"][0]["description"]
        temp_dict["img"] = "http://openweathermap.org/img/wn/" + temp_dict['icon'] + "@2x.png"

        # Convert dt from epoch time to day of week
        ep = temp_dict['dt']
        temp_dict["day"] = datetime.fromtimestamp(ep).strftime("%A")
        daily_forecast.append(temp_dict)

    return(daily_forecast)

