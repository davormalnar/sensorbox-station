# Sensorbox station #

This repository contains set of scripts (bash and python) for Raspberry Pi whose purpose is to gather data from sensors and store them in a remote database.

Station gathers following data:
* Air quality (PM 2.5 and PM 10 particles) - **Nova PM sensor SDS011**
* Temperature, Humidity, Pressure - **BME280 3.3V 6 Pin**
* Provides camera live stream (if available and configured)

### Tested Raspberry Pi versions ###

* Raspberry Pi 2/3/4 model B
* Raspberry Pi 1 model B (without camera feed)


## How to install ? ###

* **[Sensorbox setup](https://github.com/davormalnar/sensorbox-setup)**
* create **config.yaml** from **config.yaml.template** file
* run scripts with `./start` and when needed you can use `./stop` to stop the scripts or `./restart` to restart them.


Background scripts are running within *screen* environment and can be accessed using bash aliases:
* `aqi` - attaches to AQI sensor (screen)
* `temp` - attaches to Temperature/Humidity/Pressure sensor (screen)
* `camera` - attaches to camera live feed script (screen)

or using the command `screen -r <alias>`  

for example: `screen -r temp`


*Note: to detach from screen (and leave it active in the background) use `Ctrl + a` followed by `d` (lower case).  
  Exiting with `Ctrl + c` will kill the scripts.*

## To-do: ###

* Remove hardcoded directory paths
* AQI PM2.5 and PM10 calculation can be out of bounds (for deadly levels of pollution)


## Motivation behind this project? ###

This is purely a hobby project of mine.

For the longest time I wanted to monitor air quality in my city. Often times, especially at night, air quality becomes very poor and in regular time periods. I wanted to have concrete numbers that show just that.

This project allowed me to create detailed statistics and real-time air quality monitor with alarming system.
