#!/usr/bin/python3
# coding=utf-8
# updated for python 3.8 compatibility
import serial, struct, sys, time, json, subprocess, os
from datetime import date, datetime, timedelta
from pymongo import MongoClient
from lib import utils, aqiCalc, warnAqi

# serial config (do not modify)
DEBUG = 0
CMD_MODE = 2
CMD_QUERY_DATA = 4
CMD_DEVICE_ID = 5
CMD_SLEEP = 6
CMD_FIRMWARE = 7
CMD_WORKING_PERIOD = 8
MODE_ACTIVE = 0
MODE_QUERY = 1
PERIOD_CONTINUOUS = 0

# path to sensorbox-station folder
STATION_PATH = "/home/pi/sensorbox-station/"

# sensorbox config (default: STATION_PATH + "config.yaml")
CONFIG_PATH = STATION_PATH + "config.yaml"
config = utils.loadConfig(CONFIG_PATH)

# local data storage (json) location (default: STATION_PATH + "data/aqi/")
AQI_DATA_LOCAL_PATH = STATION_PATH + "data/aqi/"

# AQI measurement timings config
AQI_SAMPLE_SIZE = 15 #number of samples for avg calc (default: 15)
AQI_SLEEP_BETWEEN = 2 #seconds between each measuring within the sample (default: 2)
AQI_SLEEP_PERIOD = 120 #seconds between measuring cycle (default: 120)

# warnings will be sent every n seconds (default: 3600)
NOTIFY_PERIOD_SECONDS = 3600 # 1hour

# threshold for unhealthy air quality (default: 35) 
NOTIFY_WARNING_THRESHOLD_PM25 = 35 # 35ug/m3 ~100 AQI - unhealthy for sensitive groups

# USB-serial port device - sensor (default: "/dev/ttyUSB0")
SENSOR_USB_PORT = "/dev/ttyUSB0"

#------------------------------------

ser = serial.Serial()
ser.port = SENSOR_USB_PORT
ser.baudrate = 9600

ser.open()
ser.flushInput()

byte, data = 0, ""


def dump(d, prefix=''):
    print(prefix + ' '.join(str(x) for x in d))

def construct_command(cmd, data=[]):
    assert len(data) <= 12
    data += [0,]*(12-len(data))
    checksum = (sum(data)+cmd-2)%256
    ret = b"\xaa\xb4" + bytes([cmd])
    ret += bytes(data)
    ret += b"\xff\xff" + bytes([checksum]) + b"\xab"

    if DEBUG:
        dump(ret, '> ')
    return ret

def process_data(d):
    r = struct.unpack('<HHxxBB', d[2:])
    pm25 = r[0]/10.0
    pm10 = r[1]/10.0
    checksum = sum(d[2:8])%256
    print("PM 2.5: {} μg/m^3  PM 10: {} μg/m^3 CRC={}".format(pm25, pm10, "OK" if (checksum==r[2] and r[3]==0xab) else "NOK"))
    return [pm25, pm10]

def process_version(d):
    r = struct.unpack('<BBBHBB', d[3:])
    checksum = sum(d[2:8])%256
    print("Y: {}, M: {}, D: {}, ID: {}, CRC={}".format(r[0], r[1], r[2], hex(r[3]), "OK" if (checksum==r[4] and r[5]==0xab) else "NOK"))

def read_response():
    byte = 0
    while byte != b"\xaa":
        byte = ser.read(size=1)

    d = ser.read(size=9)

    if DEBUG:
        dump(d, '< ')
    return byte + d

def cmd_set_mode(mode=MODE_QUERY):
    ser.write(construct_command(CMD_MODE, [0x1, mode]))
    read_response()

def cmd_query_data():
    ser.write(construct_command(CMD_QUERY_DATA))
    d = read_response()
    values=[]
    if d[1:2] == b"\xc0":
        values = process_data(d)
    return values

def cmd_set_sleep(sleep=1):
    mode = 0 if sleep else 1
    ser.write(construct_command(CMD_SLEEP, [0x1, mode]))
    read_response()

def cmd_set_working_period(period):
    ser.write(construct_command(CMD_WORKING_PERIOD, [0x1, period]))
    read_response()

def cmd_firmware_ver():
    ser.write(construct_command(CMD_FIRMWARE))
    d = read_response()
    process_version(d)

def cmd_set_id(id):
    id_h = (id>>8) % 256
    id_l = id % 256
    ser.write(construct_command(CMD_DEVICE_ID, [0]*10+[id_l, id_h]))
    read_response()

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
        collection = db['aqi']
        collection.insert_one(data)
        client.close()
    except Exception as e:
        print("Mongo error occured", e)

def saveToJSON(jsonRow):
    TODAY_DATE_STAMP = date.today().strftime("%Y-%m-%d")
    JSON_FILE = AQI_DATA_LOCAL_PATH + TODAY_DATE_STAMP + ".json"

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


def prepareData(aqis):
    data = {
          'pm25': aqis[0],
          'pm10': aqis[1],
          'aqiPM25': aqiCalc.pm25(aqis[0]),
          'aqiPM10': aqiCalc.pm10(aqis[1]),
          'created': time.strftime("%Y-%m-%d %H:%M:%S"),
          'UTC': datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }
    return data

def notifyWarning(lastWarning, data):
    currentTime = datetime.now()
    difference = currentTime - lastWarning

    if difference.total_seconds() > NOTIFY_PERIOD_SECONDS:
        data['stationName'] = config['name']
        warnAqi.notify(data)
        return currentTime
    else:
        print("Skipping warning - too soon")

    return lastWarning

if __name__ == "__main__":
    cmd_set_sleep(0)
    cmd_firmware_ver()
    cmd_set_working_period(PERIOD_CONTINUOUS)
    cmd_set_mode(MODE_QUERY);

    # warning intervals - 1 hour
    lastWarning = datetime.now() - timedelta(seconds=NOTIFY_PERIOD_SECONDS)
    warnBadAirQuality = config['notifications']['warnBadAirQuality']


    while True:
        cmd_set_sleep(0)
        try:

            aqis = [0,0]
            for t in range(AQI_SAMPLE_SIZE):
                values = cmd_query_data();

                if values is not None and len(values) == 2:
                    aqis[0] += values[0]
                    aqis[1] += values[1]
                    time.sleep(AQI_SLEEP_BETWEEN)

            aqis[0] = round((aqis[0]/AQI_SAMPLE_SIZE),2)
            aqis[1] = round((aqis[1]/AQI_SAMPLE_SIZE),2)

            # lets prepare payload
            payload = prepareData(aqis)

            # save locally as well
            saveToJSON(payload)

            # save to mongoDb
            saveToDB(payload)

            # notify warning if defined
            if (warnBadAirQuality == True and int(payload['pm25']) > NOTIFY_WARNING_THRESHOLD_PM25):
                lastWarning = notifyWarning(lastWarning, payload)

            print ("Going to sleep for", AQI_SLEEP_PERIOD, "seconds...")
            cmd_set_sleep(1)
            time.sleep(AQI_SLEEP_PERIOD)

        except:
           break

    cmd_set_mode(0);
    cmd_set_sleep()
