#!/usr/bin/python

def pm10(pm10):
  pm1 = 0
  pm2 = 54
  pm3 = 154
  pm4 = 254
  pm5 = 354
  pm6 = 424
  pm7 = 504
  pm8 = 604

  aqi1 = 0
  aqi2 = 50
  aqi3 = 100
  aqi4 = 150
  aqi5 = 200
  aqi6 = 300
  aqi7 = 400
  aqi8 = 500

  aqipm10 = 0

  if pm10 >= pm1 and pm10 <= pm2:
    aqipm10 = ((aqi2 - aqi1)/(pm2 - pm1))*(pm10 - pm1)+aqi1
  elif pm10 >= pm2 and pm10 <= pm3:
    aqipm10 = ((aqi3 - aqi2) / (pm3 - pm2)) * (pm10 - pm2) + aqi2
  elif pm10 >= pm3 and pm10 <= pm4:
    aqipm10 = ((aqi4 - aqi3) / (pm4 - pm3)) * (pm10 - pm3) + aqi3
  elif pm10 >= pm4 and pm10 <= pm5:
    aqipm10 = ((aqi5 - aqi4) / (pm5 - pm4)) * (pm10 - pm4) + aqi4
  elif pm10 >= pm5 and pm10 <= pm6:
    aqipm10 = ((aqi6 - aqi5) / (pm6 - pm5)) * (pm10 - pm5) + aqi5
  elif pm10 >= pm6 and pm10 <= pm7:
    aqipm10 = ((aqi7 - aqi6) / (pm7 - pm6)) * (pm10 - pm6) + aqi6
  elif pm10 >= pm7 and pm10 <= pm8:
    aqipm10 = ((aqi8 - aqi7) / (pm8 - pm7)) * (pm10 - pm7) + aqi7

  return round(aqipm10,2)

def pm25(pm25):
  pm1 = 0
  pm2 = 12
  pm3 = 35.4
  pm4 = 55.4
  pm5 = 150.4
  pm6 = 250.4
  pm7 = 350.4
  pm8 = 500.4

  aqi1 = 0
  aqi2 = 50
  aqi3 = 100
  aqi4 = 150
  aqi5 = 200
  aqi6 = 300
  aqi7 = 400
  aqi8 = 500

  aqipm25 = 0

  if pm25 >= pm1 and pm25 <= pm2:
    aqipm25 = ((aqi2 - aqi1) / (pm2 - pm1)) * (pm25 - pm1) + aqi1
  elif pm25 >= pm2 and pm25 <= pm3:
    aqipm25 = ((aqi3 - aqi2) / (pm3 - pm2)) * (pm25 - pm2) + aqi2
  elif pm25 >= pm3 and pm25 <= pm4:
    aqipm25 = ((aqi4 - aqi3) / (pm4 - pm3)) * (pm25 - pm3) + aqi3
  elif pm25 >= pm4 and pm25 <= pm5:
    aqipm25 = ((aqi5 - aqi4) / (pm5 - pm4)) * (pm25 - pm4) + aqi4
  elif pm25 >= pm5 and pm25 <= pm6:
    aqipm25 = ((aqi6 - aqi5) / (pm6 - pm5)) * (pm25 - pm5) + aqi5
  elif pm25 >= pm6 and pm25 <= pm7:
    aqipm25 = ((aqi7 - aqi6) / (pm7 - pm6)) * (pm25 - pm6) + aqi6
  elif pm25 >= pm7 and pm25 <= pm8:
    aqipm25 = ((aqi8 - aqi7) / (pm8 - pm7)) * (pm25 - pm7) + aqi7

  return round(aqipm25,2)
