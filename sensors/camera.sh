#!/bin/bash
STATION_PATH="/home/pi/sensorbox-station"
source $STATION_PATH/scripts/parse_yaml

eval $(parse_yaml $STATION_PATH/config.yaml)

STREAM_URL=$camera_streamUrl
STREAM_KEY=$camera_streamKey
RTSP_URL=$camera_rtspUrl

if ! command -v ffmpeg &> /dev/null
then
    echo "FFmpeg could not be found.. exiting script"
    exit
fi

COMMAND="sudo ffmpeg -f lavfi -i anullsrc -rtsp_transport tcp -i ${RTSP_URL} -tune zerolatency -t 12:00:00 -pix_fmt + -c:v copy -f flv ${STREAM_URL}/${STREAM_KEY}"

i=0
while true
do

        if sudo /usr/bin/pgrep ffmpeg > /dev/null
        then
                echo "Service is already running."
        else
                echo "Service is NOT running! Starting now... (instance #$i)"
                $COMMAND
                ((i=i+1))
        fi

        sleep 60
done
