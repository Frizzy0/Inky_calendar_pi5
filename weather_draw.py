import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry
from PIL import Image, ImageDraw, ImageFont
import os
# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

weather_code_to_image = {
    0: "clear@4x.png",
    1: "mostly-clear@4x.png",
    2: "partly-cloudy@4x.png",
    3: "overcast@4x.png",
    45: "fog@4x.png",
    48: "rime-fog@4x.png",
    51: "light-drizzle@4x.png",
    53: "moderate-drizzle@4x.png",
    55: "dense-drizzle@4x.png",
    61: "light-rain@4x.png",
    80: "light-rain@4x.png",
    63: "moderate-rain@4x.png",
    81: "moderate-rain@4x.png",
    65: "heavy-rain@4x.png",
    82: "heavy-rain@4x.png",
    56: "light-freezing-drizzle@4x.png",
    57: "dense-freezing-drizzle@4x.png",
    66: "light-freezing-rain@4x.png",
    67: "heavy-freezing-rain@4x.png",
    77: "snowflake@4x.png",
    85: "slight-snowfall@4x.png",
    86: "heavy-snowfall@4x.png",
    71: "slight-snowfall@4x.png",
    73: "moderate-snowfall@4x.png",
    75: "heavy-snowfall@4x.png",
    95: "thunderstorm@4x.png",
    96: "thundestorm-with-hail@4x.png",
    97: "thundestorm-with-hail@4x.png"
}

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": 43.5781,
	"longitude": -70.3217,
	"daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
	"current": ["temperature_2m", "precipitation", "weather_code", "wind_speed_10m", "relative_humidity_2m"],
	"wind_speed_unit": "mph",
	"temperature_unit": "fahrenheit",
	"precipitation_unit": "inch"
}
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()}{response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

							
# Current values. The order of variables needs to be the same as requested.
current = response.Current()

current_temperature_2m = current.Variables(0).Value()

current_precipitation = current.Variables(1).Value()

current_weather_code = current.Variables(2).Value()

current_wind_speed_10m = current.Variables(3).Value()

current_relative_humidity_2m = current.Variables(4).Value()

print(f"Current time {current.Time()}")

print(f"Current temperature_2m {current_temperature_2m}")
print(f"Current precipitation {current_precipitation}")
print(f"Current weather_code {current_weather_code}")
print(f"Current wind_speed_10m {current_wind_speed_10m}")
print(f"Current relative_humidity_2m {current_relative_humidity_2m}")
# Process daily data. The order of variables needs to be the same as requested.
daily = response.Daily()
daily_weather_code = daily.Variables(0).ValuesAsNumpy()
daily_temperature_2m_max = daily.Variables(1).ValuesAsNumpy()
daily_temperature_2m_min = daily.Variables(2).ValuesAsNumpy()
daily_precipitation_sum = daily.Variables(3).ValuesAsNumpy()

daily_data = {"date": pd.date_range(
	start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
	end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = daily.Interval()),
	inclusive = "left"
)}

daily_data["weather_code"] = daily_weather_code
daily_data["temperature_2m_max"] = daily_temperature_2m_max
daily_data["temperature_2m_min"] = daily_temperature_2m_min
daily_data["precipitation_sum"] = daily_precipitation_sum

daily_dataframe = pd.DataFrame(data = daily_data)
print(daily_dataframe)

def draw_weather():
    img = Image.new('RGB', (400, 240), color = "white")
    d = ImageDraw.Draw(img)
    # Load a font
    font = ImageFont.truetype("./AtkinsonHyperlegible-Regular.ttf", 18)
    
    # Draw text
    d.text((10, 10), f"Current temperature: {str(current_temperature_2m)[:2]}°F", font=font, fill="black")
    d.text((10, 30), f"Current precipitation: {current_precipitation} inches", font=font, fill="black")
    
    # Add weather image
    weather_image_path = "./static/airy/" + weather_code_to_image.get(current_weather_code, "default.png")
    weather_image = Image.open(weather_image_path).convert("RGBA")
    img.paste(weather_image, (300, 20), weather_image)
    
    img.save("./weather_image.png")
    # Save the image
draw_weather()