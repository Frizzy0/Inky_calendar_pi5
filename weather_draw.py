import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry
from PIL import Image, ImageDraw, ImageFont, ImageOps
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
	"daily": ["temperature_2m_max", "temperature_2m_min", "wind_speed_10m_max", "wind_gusts_10m_max", "precipitation_probability_max"],
	"current": ["temperature_2m", "weather_code","apparent_temperature", "relative_humidity_2m"],
	"timezone": "America/New_York",
    "forecast_days": 1,
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

current_weather_code = current.Variables(1).Value()
current_apparent_temperature = current.Variables(2).Value()
current_relative_humidity_2m = current.Variables(3).Value()

print(f"Current time {current.Time()}")

print(f"Current temperature_2m {current_temperature_2m}")
print(f"Current weather_code {current_weather_code}")
print(f"Current apparent_temperature {current_apparent_temperature}")
print(f"Current relative_humidity_2m {current_relative_humidity_2m}")
# Process daily data. The order of variables needs to be the same as requested.
daily = response.Daily()
daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
daily_wind_speed_10m_max = daily.Variables(2).ValuesAsNumpy()
daily_wind_gusts_10m_max = daily.Variables(3).ValuesAsNumpy()
daily_precipitation_probability_max = daily.Variables(4).ValuesAsNumpy()

daily_data = {"date": pd.date_range(
	start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
	end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = daily.Interval()),
	inclusive = "left"
)}

daily_data["temperature_2m_max"] = daily_temperature_2m_max
daily_data["temperature_2m_min"] = daily_temperature_2m_min
daily_data["wind_speed_10m_max"] = daily_wind_speed_10m_max
daily_data["wind_gusts_10m_max"] = daily_wind_gusts_10m_max
daily_data["precipitation_probability_max"] = daily_precipitation_probability_max

daily_dataframe = pd.DataFrame(data = daily_data)
print(daily_dataframe)

def draw_weather():
    img = Image.new('RGB', (400, 240), color = "white")
    #d = ImageDraw.Draw(img)
    text_layer = Image.new('1', (400, 240), 0)
    d = ImageDraw.Draw(text_layer)
    # Load a font
    
    font = ImageFont.truetype("./AtkinsonHyperlegible-Regular.ttf", 48)
    font_small = ImageFont.truetype("./AtkinsonHyperlegible-Regular.ttf", 24)
    # Draw text
    d.text((15, 0), f"{str(current_temperature_2m)[:2]}°F", font=font, fill=1)
    d.text((130, 15), f"H/L: {str(daily_temperature_2m_max[0])[:2]}/{str(daily_temperature_2m_min[0])[:2]}°F", font=font_small, fill=1)
    d.text((15, 80), f"Wind: {str(daily_wind_speed_10m_max[0])[:2]} mph", font=font_small, fill=1)
    d.text((15, 120), f"Gusts: {str(daily_wind_gusts_10m_max[0])[:2]} mph", font=font_small, fill=1)
    d.text((15, 160), f"Precip: {str(daily_precipitation_probability_max[0])[:2]}%", font=font_small, fill=1)
    d.text((200, 160), f"Feels like: {str(current_apparent_temperature)[:2]}°F", font=font_small, fill=1)
    d.text((15, 200), f"Humidity: {str(current_relative_humidity_2m)[:2]}%", font=font_small, fill=0)
    
    # Add weather image
    weather_image_path = "./static/airy/" + weather_code_to_image.get(int(current_weather_code), "default.png")
    weather_image = Image.open(weather_image_path).convert("RGB")
    img.paste(weather_image, (320, 20), weather_image)
    
    img.paste((0,0,0), (0,0), mask=text_layer)

    img.save("./weather_image.png")
    #img_clean = clean_text_image(img)

    #img_clean.save("./weather_image.png")
    # Save the image

#def clean_text_image(image):
#    return image.convert("L").point(lambda x:255 if x>128 else 0).convert("RGB")
draw_weather()