#!/usr/bin/python3
import os

def notify(rpiTemp):
  msg = "\\[ RPi ] OVERHEAT WARNING  *" + str(round(rpiTemp,1)) + "°C* \n"

  os.system('/home/pi/sensorbox-station/scripts/telegramBotNotify "' + msg + '"')



