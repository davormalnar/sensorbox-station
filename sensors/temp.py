#!/usr/bin/python3
import smbus, yaml, time, os, json, datetime
from datetime import date, datetime, timedelta
from pymongo import MongoClient
from ctypes import c_short
from ctypes import c_byte
from ctypes import c_ubyte
from gpiozero import CPUTemperature
from meteocalc import Temp, dew_point, heat_index
from lib import utils, warnRPiTemp

# I2C device (sensor) address (default: 0x76)
DEVICE = 0x76 # you can get list of i2c devices-> sudo i2cdetect -y 1

bus = smbus.SMBus(1) # Rev 2 Pi, Pi 2 & Pi 3 uses bus 1
                     # Rev 1 Pi uses bus 0


# path to sensorbox-station folder
STATION_PATH = "/home/pi/sensorbox-station/"

# sensorbox config (default: STATION_PATH + "config.yaml")
CONFIG_PATH = STATION_PATH + "config.yaml"
config = utils.loadConfig(CONFIG_PATH)

# local data storage (json) location (default: STATION_PATH + "data/temp/")
TEMP_DATA_LOCAL_PATH = STATION_PATH + "data/temp/"

# temperature measurement timings
TEMP_SLEEP_PERIOD = 120 #seconds between measuring cycle (default: 120)

# warnings will be sent every n seconds (default: 3600)
NOTIFY_PERIOD_SECONDS = 3600 # 1hour

# RPi temperature treshold before sending warning notification (default: 75)
NOTIFY_WARNING_TEMP_THRESHOLD = 75 #°C

#------------------------------------

def getShort(data, index):
  # return two bytes from data as a signed 16-bit value
  return c_short((data[index+1] << 8) + data[index]).value

def getUShort(data, index):
  # return two bytes from data as an unsigned 16-bit value
  return (data[index+1] << 8) + data[index]

def getChar(data,index):
  # return one byte from data as a signed char
  result = data[index]
  if result > 127:
    result -= 256
  return result

def getUChar(data,index):
  # return one byte from data as an unsigned char
  result =  data[index] & 0xFF
  return result

def readBME280ID(addr=DEVICE):
  # Chip ID Register Address
  REG_ID     = 0xD0
  (chip_id, chip_version) = bus.read_i2c_block_data(addr, REG_ID, 2)
  return (chip_id, chip_version)

def readBME280All(addr=DEVICE):
  # Register Addresses
  REG_DATA = 0xF7
  REG_CONTROL = 0xF4
  REG_CONFIG  = 0xF5

  REG_CONTROL_HUM = 0xF2
  REG_HUM_MSB = 0xFD
  REG_HUM_LSB = 0xFE

  # Oversample setting - page 27
  OVERSAMPLE_TEMP = 2
  OVERSAMPLE_PRES = 2
  MODE = 1

  # Oversample setting for humidity register - page 26
  OVERSAMPLE_HUM = 2
  bus.write_byte_data(addr, REG_CONTROL_HUM, OVERSAMPLE_HUM)

  control = OVERSAMPLE_TEMP<<5 | OVERSAMPLE_PRES<<2 | MODE
  bus.write_byte_data(addr, REG_CONTROL, control)

  # Read blocks of calibration data from EEPROM
  # See Page 22 data sheet
  cal1 = bus.read_i2c_block_data(addr, 0x88, 24)
  cal2 = bus.read_i2c_block_data(addr, 0xA1, 1)
  cal3 = bus.read_i2c_block_data(addr, 0xE1, 7)

  # Convert byte data to word values
  dig_T1 = getUShort(cal1, 0)
  dig_T2 = getShort(cal1, 2)
  dig_T3 = getShort(cal1, 4)

  dig_P1 = getUShort(cal1, 6)
  dig_P2 = getShort(cal1, 8)
  dig_P3 = getShort(cal1, 10)
  dig_P4 = getShort(cal1, 12)
  dig_P5 = getShort(cal1, 14)
  dig_P6 = getShort(cal1, 16)
  dig_P7 = getShort(cal1, 18)
  dig_P8 = getShort(cal1, 20)
  dig_P9 = getShort(cal1, 22)

  dig_H1 = getUChar(cal2, 0)
  dig_H2 = getShort(cal3, 0)
  dig_H3 = getUChar(cal3, 2)

  dig_H4 = getChar(cal3, 3)
  dig_H4 = (dig_H4 << 24) >> 20
  dig_H4 = dig_H4 | (getChar(cal3, 4) & 0x0F)

  dig_H5 = getChar(cal3, 5)
  dig_H5 = (dig_H5 << 24) >> 20
  dig_H5 = dig_H5 | (getUChar(cal3, 4) >> 4 & 0x0F)

  dig_H6 = getChar(cal3, 6)

  # Wait in ms (Datasheet Appendix B: Measurement time and current calculation)
  wait_time = 1.25 + (2.3 * OVERSAMPLE_TEMP) + ((2.3 * OVERSAMPLE_PRES) + 0.575) + ((2.3 * OVERSAMPLE_HUM)+0.575)
  time.sleep(wait_time/1000)  # Wait the required time  

  # Read temperature/pressure/humidity
  data = bus.read_i2c_block_data(addr, REG_DATA, 8)
  pres_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
  temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
  hum_raw = (data[6] << 8) | data[7]

  #Refine temperature
  var1 = ((((temp_raw>>3)-(dig_T1<<1)))*(dig_T2)) >> 11
  var2 = (((((temp_raw>>4) - (dig_T1)) * ((temp_raw>>4) - (dig_T1))) >> 12) * (dig_T3)) >> 14
  t_fine = var1+var2
  temperature = float(((t_fine * 5) + 128) >> 8);

  # Refine pressure and adjust for temperature
  var1 = t_fine / 2.0 - 64000.0
  var2 = var1 * var1 * dig_P6 / 32768.0
  var2 = var2 + var1 * dig_P5 * 2.0
  var2 = var2 / 4.0 + dig_P4 * 65536.0
  var1 = (dig_P3 * var1 * var1 / 524288.0 + dig_P2 * var1) / 524288.0
  var1 = (1.0 + var1 / 32768.0) * dig_P1
  if var1 == 0:
    pressure=0
  else:
    pressure = 1048576.0 - pres_raw
    pressure = ((pressure - var2 / 4096.0) * 6250.0) / var1
    var1 = dig_P9 * pressure * pressure / 2147483648.0
    var2 = pressure * dig_P8 / 32768.0
    pressure = pressure + (var1 + var2 + dig_P7) / 16.0

  # Refine humidity
  humidity = t_fine - 76800.0
  humidity = (hum_raw - (dig_H4 * 64.0 + dig_H5 / 16384.0 * humidity)) * (dig_H2 / 65536.0 * (1.0 + dig_H6 / 67108864.0 * humidity * (1.0 + dig_H3 / 67108864.0 * humidity)))
  humidity = humidity * (1.0 - dig_H1 * humidity / 524288.0)
  if humidity > 100:
    humidity = 100
  elif humidity < 0:
    humidity = 0

  return temperature/100.0,pressure/100.0,humidity


def saveToDB(data):
    db_user = config['database']['username']
    db_pass = config['database']['password']
    db_host = config['database']['host']
    db_port = config['database']['port']
    db_alias = "sensorbox_"+config['database']['alias']

    conn_str = f'mongodb://{db_user}:{db_pass}@{db_host}:{db_port}/?authSource=admin&readPreference=primary&ssl=false'

    try:
        client = MongoClient(conn_str, serverSelectionTimeoutMS=5000)

        db = client[db_alias]
        collection = db['temperature']
        collection.insert_one(data)
        client.close()
    except Exception as e:
        print("Mongo error occured", e)


def saveToJSON(jsonRow):
    TODAY_DATE_STAMP = date.today().strftime("%Y-%m-%d")
    JSON_FILE = TEMP_DATA_LOCAL_PATH + TODAY_DATE_STAMP + ".json"

    # open stored data
    try:
        with open(JSON_FILE) as json_data:
            data = json.load(json_data)
    except Exception as e:
        print ("An error occured while reading data:", e)
        data = []

    data.append(jsonRow)

    # save it
    try:
        with open(JSON_FILE, 'w') as outfile:
            json.dump(data, outfile)
    except Exception as e:
        print("And error occured while saving data:", e)


def notifyWarning(lastWarning, temp):
    currentTime = datetime.now()
    difference = currentTime - lastWarning

    if difference.total_seconds() > NOTIFY_PERIOD_SECONDS:
        data['rpiTemp'] = temp
        data['stationName'] = config['name']
        warnRPiTemp.notify(data)
        return currentTime
    else:
        print("Skipping warning - too soon")

    return lastWarning


if __name__ == "__main__":
  (chip_id, chip_version) = readBME280ID()
  #print "Chip ID: ", chip_id
  #print "Version: ", chip_version

  lastWarning = datetime.now() - timedelta(seconds=NOTIFY_PERIOD_SECONDS)
  warnRPiOverheating = config['notifications']['warnRPiOverheating']

  while True:
    try:

      temperature,pressure,humidity = readBME280All()
      pressure = round(pressure, 2)
      humidity = round(humidity, 2)

      # Height above sea level
      hasl = config["station"]["elevation"]

      # Adjusted-to-the-sea barometric pressure
      pressureNormalized = round(pressure + ((pressure * 9.80665 * hasl)/(287 * (273 + temperature + (hasl/400)))),2)

      rpiTemp = CPUTemperature().temperature

      # create input temperature in different units
      t = Temp(temperature, 'c')  # c - celsius, f - fahrenheit, k - kelvin
      t2 = Temp(((temperature * 9/5) + 32) , 'f')

      # calculate Dew Point
      dp = dew_point(temperature=t, humidity=humidity)

      # calculate Heat Index
      hi = heat_index(temperature=t2, humidity=humidity)

      dewPoint = round(dp.c, 2)
      heatIndex = round(hi.c, 2)

      payload = {
        'temperature': round(temperature, 2),
        'pressure': round(pressure, 2),
        'pressureNormalized': round(pressureNormalized, 2),
        'humidity': round(humidity, 2),
        'dewPoint': round(dewPoint, 2),
        'heatIndex': round(heatIndex, 2),
        'rpi_temp': round(rpiTemp, 2),
        'created': time.strftime("%Y-%m-%d %H:%M:%S"),
        'UTC': datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
      }

      print ("Temperature : ", round(temperature,2), "C")
      print ("Pressure : ", round(pressureNormalized,2),"(",round(pressure,2),") hPa")
      print ("Humidity : ", round(humidity,2), "%")

      # save locally as well
      saveToJSON(payload)

      # save to db
      saveToDB(payload)

      if (warnRPiOverheating == True and int(rpiTemp) > NOTIFY_WARNING_TEMP_THRESHOLD): #RPi temp above 75C
        print("\nRPi overheating!!")
        lastWarning = notifyWarning(lastWarning, rpiTemp)

      print ("\nGoing to sleep for", TEMP_SLEEP_PERIOD, "seconds...")
      time.sleep(TEMP_SLEEP_PERIOD)


    except Exception as e:
        print("An error occured", e)

