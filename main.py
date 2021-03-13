from flask import Flask, render_template, redirect, request
import requests
import configparser
from helpers import *
import json
from matplotlib import pyplot as plt
import geocoder

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0



# Global variable to store users current city
myloc = geocoder.ip('me')
current_city = myloc.city


# Home page
@app.route("/", methods=["GET", "POST"])
def home(): 
    # If visiting first time, give form to locate city
    if request.method == "GET":
        if current_city:
                api_key = get_api_key()

                try:
                    weather_all = one_call_info(api_key, current_city)

                except KeyError:
                    return render_template("main.html")
                
                current = get_info_current(weather_all)
                daily = get_info_daily(weather_all)
                hourly = get_info_hourly(weather_all)
                graph_hourly(hourly)

                return render_template("main_weather_hub.html", current = current, daily = daily, location = current_city)
        
        return render_template("main.html")

    # Once form submitted, attempt to look up city

    else:
        # Get api key, location (from form submitted)
        api_key = get_api_key()

        if request.form.get("city"):
            location = request.form.get("city")

            if location == '':
                return render_template('main.html')

            # Use function to try to make api call
            # Automatically parses necessary information into dict
            try:
                weather_all = one_call_info(api_key, location)

            except KeyError:    
                print("KeyError")
                return render_template("main.html")
                

            else: 
                current = get_info_current(weather_all)
                daily = get_info_daily(weather_all)
                hourly = get_info_hourly(weather_all)
                graph_hourly(hourly)

                return render_template("main_weather_hub.html", current = current, daily = daily, location = location.title())
    
# Weather display page
@app.route("/city_weather.html", methods=["POST"])
def city_weather(): 
     # Get api key, location (from form submitted)
        api_key = get_api_key()
        location = request.form.get("city").lower()

        # Use function to try to make api call
        # Automatically parses necessary information into dict
        try:
            weather_info = parse_weather(api_key, location)

        except KeyError:    
            return render_template("main.html")

        else: 
            # Get image for icon
            icon = weather_info["pic_id"]
            pic_url = "http://openweathermap.org/img/wn/" + icon + "@2x.png"

            print(pic_url)
            # return render_template("city_weather.html", location = location, weather_info = weather_info, pic_url = pic_url)
            return render_template("7dayforecast.html", seven_day_info = seven_day_info, location = location)

@app.route("/about")
def about():
    return render_template("about.html")

# No caching at all for API endpoints
@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

# Run program
if __name__ == "__main__":
    app.run(debug=True)

