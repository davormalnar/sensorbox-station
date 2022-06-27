#!/usr/bin/python3
import os

def color(aqiVal):
  if aqiVal < 51:
    return "Good"
  elif aqiVal < 101:
    return "Moderate"
  elif aqiVal < 151:
    return "Unhealthy (!)"
  elif aqiVal < 201:
    return "Unhealthy (!!)"
  elif aqiVal < 301:
    return "Hazardous"
  elif aqiVal > 401:
    return "Extremely hazardous"

  return ""

def notify(aqi):
  msg = "============== WARNING ============== \n" + \
        "-> station: " + str(aqi['stationName']) + " \n" + \
        str(color(aqi['aqiPM25'])) + " - AQI (PM 2.5): *" + str(aqi['aqiPM25']) + "* (" + str(aqi['pm25']) + " ug/m3) \n" + \
        str(color(aqi['aqiPM10'])) + " - AQI (PM 10): *" + str(aqi['aqiPM10']) + "* (" + str(aqi['pm10']) + " ug/m3) \n" + \
        "========== " + str(aqi['created']) + " ========== \n"

  os.system('/home/pi/sensorbox-station/scripts/telegramBotNotify "' + msg + '"')


