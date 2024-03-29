#!/usr/bin/python3
import time, json, os, sys, yaml
from datetime import date
from aqiCalc import *

MY_PATH = os.path.dirname(os.path.realpath(__file__))

# path to sensorbox-station folder
STATION_PATH = "/home/pi/sensorbox-station/"

# sensorbox config (default: STATION_PATH + "config.yaml")
CONFIG_PATH = STATION_PATH + "config.yaml"

def loadConfig(path):
    with open(path, "r") as ymlfile:
        return yaml.safe_load(ymlfile)

def parseJsonAqi():
  # path to JSON file
  TODAY_DATE_STAMP = date.today().strftime("%Y-%m-%d")
  jsonPath = MY_PATH + "/../data/aqi/" + TODAY_DATE_STAMP + ".json"

  # Opening JSON file
  f = open(jsonPath)

  # returns JSON object as a dictionary
  data = json.load(f)[-1]

  # Closing file
  f.close()

  aqiPM25 = pm25(data['pm25'])
  aqiPM10 = pm10(data['pm10'])

  return data 

def parseJsonTemp():
  # path to JSON file
  TODAY_DATE_STAMP = date.today().strftime("%Y-%m-%d")
  jsonPath = MY_PATH + "/../data/temp/" + TODAY_DATE_STAMP + ".json"

  # Opening JSON file
  f = open(jsonPath)

  # returns JSON object as a dictionary
  data = json.load(f)[-1]

  # Closing file
  f.close()

  return data


def color(aqiVal):
  if aqiVal < 51:
    return "✅ Good"
  elif aqiVal < 101:
    return "⚠ Moderate"
  elif aqiVal < 151:
    return "❗Unhealthy❗"
  elif aqiVal < 201:
    return "‼Unhealthy‼ "
  else:
    return "‼💀 Hazardous 💀‼"

  return ""

if __name__=="__main__":

  config = loadConfig(CONFIG_PATH)
  aqi = parseJsonAqi()
  temp = parseJsonTemp()

  msg = "*" + config['name'] + ' - ' + str(aqi['created']) + "* \n" + \
        "-- \n" + \
        str(color(aqi['aqiPM25'])) + " - AQI (PM 2.5): *" + str(aqi['aqiPM25']) + "* (" + str(aqi['pm25']) + " ug/m3) \n" + \
        str(color(aqi['aqiPM10'])) + " - AQI (PM 10): *" + str(aqi['aqiPM10']) + "* (" + str(aqi['pm10']) + " ug/m3) \n" + \
  	"-- \n" + \
	"Temperature: *" + str(temp['temperature']) + " C* \n" + \
	"Pressure: *" + str(temp['pressureNormalized']) + " hPa* \n" + \
        "Humidity: *" + str(temp['humidity']) + "% * \n" + \
	"--" + "\n" + \
	"Heat index: *" + str(round(temp['heatIndex'],2)) + " C* \n" + \
	"Dew point: *" + str(round(temp['dewPoint'],2)) + " C* \n" + \
	"--" + "\n" + \
	"RPi temperature: *" + str(temp['rpi_temp']) + " C*"

  os.system(MY_PATH + '/telegramBotNotify "' + msg + '"' )

