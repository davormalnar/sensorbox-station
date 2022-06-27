#!/usr/bin/python3
import os

def notify(data):
  msg = "\\[ " + data['stationName'] + " ] OVERHEAT WARNING  *" + str(round(data['rpiTemp'],1)) + "°C* \n"

  os.system('/home/pi/sensorbox-station/scripts/telegramBotNotify "' + msg + '"')



