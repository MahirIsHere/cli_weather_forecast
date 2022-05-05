import argparse
import json
import sys
from configparser import ConfigParser
from urllib import error, parse, request

import style

BASE_WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"

# Weather Condition Codes
# https://openweathermap.org/weather-conditions#Weather-Condition-Codes-2
THUNDERSTORM = range(200, 300)
DRIZZLE = range(300, 400)
RAIN = range(500, 600)
SNOW = range(600, 700)
MIST = (701,)
SMOKE = (711,)
HAZE = (721,)
# sand/ dust whirls
DUSTWHRIL = (731,)
FOG = (741,)
SAND = (751,)
DUST = (761,)
# 	volcanic ash
ASH = (762,)
SQUALL = (771,)
TORNADO = (781,)
CLEAR = range(800, 801)
CLOUDY = range(801, 900)


def read_user_cli_args():
    """Handles the CLI user interactions.

    Returns:
        argparse.Namespace: Populated namespace object
    """
    parser = argparse.ArgumentParser(
        description="gets weather and temperature information for a city"
    )
    parser.add_argument("city", nargs="+", type=str, help="enter the city name")
    return parser.parse_args()


def build_weather_query(city_input):
    """Builds the URL for an API request to OpenWeather's Weather API.

    Args:
        city_input (List[str]): Name of a city as collected by argparse

    Returns:
        str: URL formatted for a call to OpenWeather's city name endpoint
    """
    api_key = _get_api_key()
    city_name = " ".join(city_input)
    url_encoded_city_name = parse.quote_plus(city_name)
    units = "metric"
    url = (
        f"{BASE_WEATHER_API_URL}?q={url_encoded_city_name}"
        f"&units={units}&appid={api_key}"
    )
    return url


def _get_api_key():
    """Fetch the API key from your configuration file.

    Expects a configuration file named "secrets.ini" with structure:

        [openweather]
        api_key=<YOUR-OPENWEATHER-API-KEY>
    """
    config = ConfigParser()
    config.read("secrets.ini")
    return config["openweather"]["api_key"]


def get_weather_data(query_url):
    """Makes an API request to a URL and returns the data as a Python object.

    Args:
        query_url (str): URL formatted for OpenWeather's city name endpoint

    Returns:
        dict: Weather information for a specific city
    """
    try:
        response = request.urlopen(query_url)
    except error.HTTPError as http_error:
        if http_error.code == 401:  # 401 - Unauthorized
            sys.exit("Access denied. Check your API key.")
        elif http_error.code == 404:  # 404 - Not Found
            sys.exit("Can't find weather data for this city.")
        else:
            sys.exit(f"Something went wrong... ({http_error.code})")

    data = response.read()

    try:
        return json.loads(data)
    except json.JSONDecodeError:
        sys.exit("Couldn't read the server response.")


def display_weather_info(weather_data):
    """Prints formatted weather information about a city.

    Args:
        weather_data (dict): API response from OpenWeather by city name

    More information at https://openweathermap.org/current#name
    """
    city = weather_data["name"]
    weather_id = weather_data["weather"][0]["id"]
    weather_description = weather_data["weather"][0]["description"]
    temperature = weather_data["main"]["temp"]

    style.change_color(style.REVERSE)
    print(f"{city:^{style.PADDING}}", end="")
    style.change_color(style.RESET)
    weather_symbol, color = _select_weather_display_params(weather_id)
    style.change_color(color)

    print(f"\t{weather_symbol}", end=" ")
    print(
        f"\t{weather_description.capitalize():^{style.PADDING}}", end=" ",
    )
    style.change_color(style.RESET)

    print(f"({temperature}°{'C'})", end="")


def _select_weather_display_params(weather_id):
    """Selects a weather symbol and a display color for a weather state.

    Args:
        weather_id (int): Weather condition code from the OpenWeather API

    Returns:
        tuple[str]: Contains a weather symbol and a display color
    """

    if weather_id in THUNDERSTORM:
        display_params = ("⛈️", style.RED)
    elif weather_id in DRIZZLE:
        display_params = ("🌧️", style.CYAN)
    elif weather_id in RAIN:
        display_params = ("☔", style.BLUE)
    elif weather_id in SNOW:
        display_params = ("❄️", style.WHITE)
    elif weather_id in MIST:
        display_params = ("🌫️", style.PALEBLUEHUE)
    elif weather_id in SMOKE:
        display_params = ("💨", style.ASH)
    elif weather_id in HAZE:
        display_params = ("😶‍🌫️", style.LIGHTBLUE)
    elif weather_id in DUSTWHRIL:
        display_params = ("🌪️", style.BROWN)
    elif weather_id in FOG:
        display_params = ("😶‍🌫️", style.ASH)
    elif weather_id in SAND:
        display_params = ("🏜️", style.YELLOW)
    elif weather_id in DUST:
        display_params = ("💨", style.BROWN)
    elif weather_id in ASH:
        display_params = ("🌋", style.RED)
    elif weather_id in SQUALL:
        display_params = ("🌬️", style.BLUE)
    elif weather_id in TORNADO:
        display_params = ("🌪️", style.WHITE)
    elif weather_id in CLEAR:
        display_params = ("☀️", style.YELLOW)
    elif weather_id in CLOUDY:
        display_params = ("⛅", style.WHITE)
    else:  # In case the API adds new weather codes
        display_params = ("🌈", style.RESET)
    return display_params


if __name__ == "__main__":
    user_args = read_user_cli_args()
    query_url = build_weather_query(user_args.city)
    weather_data = get_weather_data(query_url)
    display_weather_info(weather_data)
