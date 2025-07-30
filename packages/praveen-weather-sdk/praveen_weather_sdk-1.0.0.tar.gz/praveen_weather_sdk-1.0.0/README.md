# Weather SDK

A simple and lightweight Python SDK to fetch current weather and 5-day forecast data using the [OpenWeather API](https://openweathermap.org/api).  
This SDK wraps the API endpoints into easy-to-use Python methods, allowing you to quickly integrate weather data into your applications.

---

## Features

- Fetch current weather and 5-day/3-hour interval forecasts for any city worldwide  
- Easy-to-use Python client with minimal setup  
- Supports city argument input with fallback default to your favorite city (Patna)  
- Configurable units (metric by default)  
- Handles API requests and JSON parsing transparently  
- Suitable for hobby projects, demos, and quick integrations

---

## Installation

You can install the SDK via pip (once published) or install locally during development:

```bash
pip install weather-sdk

Usage
Script accepts city name as an argument (optional)
If you provide a city name as a command-line argument, the script fetches weather for that city. Otherwise, it defaults to Patna.

```bash
python check_sdk.py Mumbai

About
Developed by Praveen Kumar Bharti — a straightforward SDK to get weather data effortlessly.
Find me on GitHub | LinkedIn

