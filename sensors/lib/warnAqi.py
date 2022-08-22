#!/usr/bin/python3
import os

def severity(level):
  if level == "ERROR":
      return "❌ Error"
  elif level == "GOOD":
      return "✅ Good"
  elif level == "MODERATE":
      return "⚠️ Moderate"
  elif level == "UNHEALTHY_1":
      return "❗Unhealthy❗"
  elif level == "UNHEALTHY_2":
      return "‼️Unhealthy‼️"
  elif level == "VERY_UNHEALTHY":
      return "‼☣‼️ Very unhealthy"
  elif level == "HAZARDOUS":
      return "‼💀‼ Hazardous"
  elif level == "EXTREMELY_HAZARDOUS":
      return "‼☠️️‼ Extremely hazardous"
  else:
      return "Something's wrong :("


def severity25(pmVal):
  if pmVal == 0:
    return severity("ERROR")
  elif pmVal < 13:
    return severity("GOOD")
  elif pmVal < 36:
    return severity("MODERATE")
  elif pmVal < 56:
    return severity("UNHEALTHY_1")
  elif pmVal < 150:
    return severity("UNHEALTHY_2")
  elif pmVal < 250:
    return severity("VERY_UNHEALTHY")
  elif pmVal <= 500:
    return severity("HAZARDOUS")
  elif pmVal > 500:
    return severity("EXTREMELY_HAZARDOUS")

def severity10(pmVal):
  if pmVal == 0:
    return severity("ERROR")
  elif pmVal < 55:
    return severity("GOOD")
  elif pmVal < 155:
    return severity("MODERATE")
  elif pmVal < 255:
    return severity("UNHEALTHY_1")
  elif pmVal < 355:
    return severity("UNHEALTHY_2")
  elif pmVal < 425:
    return severity("VERY_UNHEALTHY")
  elif pmVal <= 604:
    return severity("HAZARDOUS")
  elif pmVal > 604:
    return severity("EXTREMELY_HAZARDOUS")

def notify(aqi):
  msg = "==================== WARNING ==================== \n" + \
        "-> " + str(aqi['stationName']) + " \n" + \
        str(severity25(aqi['pm25'])) + " - AQI (PM 2.5): *" + str(aqi['aqiPM25']) + "* (" + str(aqi['pm25']) + " ug/m3) \n" + \
        str(severity10(aqi['pm10'])) + " - AQI (PM 10): *" + str(aqi['aqiPM10']) + "* (" + str(aqi['pm10']) + " ug/m3) \n" + \
        "================ " + str(aqi['created']) + " ================ \n"

  os.system('/home/pi/sensorbox-station/scripts/telegramBotNotify "' + msg + '"')


## for testing purposes only 
#if __name__=="__main__":
#  aqi = {
#    'pm25': 5,
#    'pm10': 42,
#    'aqiPM25': 100,
#    'aqiPM10': 100,
#    'created': '2022-08-22',
#    'stationName': 'Testna stanica Varaždin'
#  }
#
#  notify(aqi)

