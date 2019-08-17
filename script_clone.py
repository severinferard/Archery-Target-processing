import io
import socket
import time
import logging
import sys
import base64
from struct import pack
import os
from _thread import *
import keyboard


logger = logging.getLogger("Rpi_logger")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class NetworkCamera():

    def __init__(self, host, port, id):
        self.id = id
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.addr = (self.host, self.port)
        self.client.connect(self.addr)


    def ready(self):
        self.client.send(str.encode("ready"))
        return self.client.recv(2048)

    def send_id(self):
        self.client.send(str.encode("id"))
        self.client.recv(1)
        self.client.send(str.encode("Raspberry1"))

    def send_pictures(self):
        start_new_thread(self.check_calibrate, ("_",))

        while not self.ready():

            logger.info("waiting for Analyzer to connect")
            time.sleep(1)


        self.stream = io.BytesIO()
        logger.debug("created stream object")
        self.send_id()

        path = '/home/criuser/Documents/Progra_Perso/Python3/Archery project/Server/Image'
        files = []
        for r, d, f in os.walk(path):         # r=root, d=directories, f = files
            for file in f:
                if '.jpg' in file:
                    files.append(os.path.join(r, file))
        ordered = sorted((time.strptime(d[-12:-4], "%H:%M:%S") for d in files), reverse=False)
        files = []
        for f in ordered:
            hour = f.tm_hour
            if len(str(f.tm_min)) == 1:
                min = f"{0}{f.tm_min}"
            else:
                min = f.tm_min
            if len(str(f.tm_sec)) == 1:
                sec = f"{0}{f.tm_sec}"
            else:
                sec = f.tm_sec
            files.append(f"Image/2019-07-27_{hour}:{min}:{sec}.jpg")

        for f in files:
            logger.info(f"picture : {f}")
            with open(f, 'rb') as img:
                logger.info("Image captured")

                self.stream.seek(0)
                self.image_data = img.read()
                self.str = base64.b64encode(self.image_data)
                self.client.sendall(b"IMAGE")
                self.client.recv(1)

                self.length = pack('>Q', len(self.image_data))
                self.client.sendall(self.length)
                logger.info("Transmiting image")

                self.client.sendall(self.image_data)
                ack = self.client.recv(1)
                logger.info("Recieved acknoledgment")

                self.stream.seek(0)
                self.stream.truncate()
                time.sleep(0.1)

    def check_calibrate(self, *args, **kwargs):
        run = True
        while run:  # making a loop
            try:
                if keyboard.is_pressed('q'):
                    logger.info("Button pressed")
                    time.sleep(1)
                    self.client.send(str.encode("calibrate"))
                    logger.info("check_calibratebration request sent")
                    self.client.recv(1)
                    logger.info("cali Ack recieved")
                else:
                    pass

            except Exception as e:
                print(e)
                break


nwcamera = NetworkCamera("192.168.1.40", 5000, 1)
nwcamera.send_pictures()
