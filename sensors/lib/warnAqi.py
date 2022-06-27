#!/usr/bin/python3
import os

def severity25(pmVal):
  if pmVal == 0:
    return "Error"
  elif pmVal < 13:
    return "Good"
  elif pmVal < 36:
    return "Moderate"
  elif pmVal < 56:
    return "Unhealthy (!)"
  elif pmVal < 150:
    return "Unhealthy (!!)"
  elif pmVal < 250:
    return "Very unhealthy (!!!)"
  elif pmVal <= 500:
    return "Hazardous"
  elif pmVal > 500:
    return "Extremely hazardous"

def severity10(pmVal):
  if pmVal == 0:
    return "Error"
  elif pmVal < 55:
    return "Good"
  elif pmVal < 155:
    return "Moderate"
  elif pmVal < 255:
    return "Unhealthy (!)"
  elif pmVal < 355:
    return "Unhealthy (!!)"
  elif pmVal < 425:
    return "Very unhealthy (!!!)"
  elif pmVal <= 604:
    return "Hazardous"
  elif pmVal > 604:
    return "Extremely hazardous"

def notify(aqi):
  msg = "==================== WARNING ==================== \n" + \
        "-> " + str(aqi['stationName']) + " \n" + \
        str(severity25(aqi['pm25'])) + " - AQI (PM 2.5): *" + str(aqi['aqiPM25']) + "* (" + str(aqi['pm25']) + " ug/m3) \n" + \
        str(severity10(aqi['pm10'])) + " - AQI (PM 10): *" + str(aqi['aqiPM10']) + "* (" + str(aqi['pm10']) + " ug/m3) \n" + \
        "================ " + str(aqi['created']) + " ================ \n"

  os.system('/home/pi/sensorbox-station/scripts/telegramBotNotify "' + msg + '"')


