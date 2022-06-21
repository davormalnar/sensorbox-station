#!/usr/bin/python3
# Web streaming example
# Source code from the official PiCamera package
# http://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming

import io
import sched
import time
import picamera
import logging
import socketserver
from threading import Condition
from http import server
from fractions import Fraction
from datetime import datetime

PAGE="""\
<html>
<head>
<title>Raspberry Pi - Surveillance Camera</title>
</head>
<body>
<center><h1>Raspberry Pi - Surveillance Camera</h1></center>
<!--<center><img src="stream.mjpg" width="640" height="480"></center>-->
<center><img src="stream.mjpg"></center>
</body>
</html>
"""

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

with picamera.PiCamera() as camera:


    s = sched.scheduler(time.time, time.sleep)

    def foo(s):
        print("Call every 5 seconds")
        s.enter(5, 1, foo, (s,))

    def bar(s):
        print("Call every 10 seconds")
        s.enter(10, 1, bar, (s,))

    s.enter(5, 1, foo, (s,))
    s.enter(10, 1, bar, (s,))
    s.run()


    output = StreamingOutput()

    # Camera warm-up time
    time.sleep(2)

    camera.rotation = 180
    camera.resolution = (480,360)

    camera.sensor_mode = 3
    camera.exposure_mode = 'night' #preview' #raises the gains, and lowers the iso

    camera.iso = 0 #Auto.This will yield less noise during day exposures and keep the iso down in low light for less noise. 
    camera.framerate_range = (0.167, 30) #this should match the values available in sensor mode, allowing upto a 6 second exposure

    camera.start_recording(output, format='mjpeg')
    try:
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        camera.stop_recording()

    #camera.framerate = Fraction(1, 6)
    #camera.shutter_speed = 6000000
    #camera.exposure_mode = 'off'
    #camera.iso = 800

    #timestamp = datetime.now()
    #imageFile = timestamp.strftime("%Y-%m-%d_%H-%M-%S")+".jpg"
    #camera.capture(imageFile)

    while True:
        camera.shutter_speed = 6000000
        camera.exposure_mode = 'off'
        camera.iso = 800

        timestamp = datetime.now()
        imageFile = timestamp.strftime("%Y-%m-%d_%H-%M-%S")+".jpg"
        camera.capture(imageFile)
        time.sleep(10)
