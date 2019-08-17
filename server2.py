import socket
import sys
import logging
import io
import os
import math
from _thread import *
from struct import unpack
from time import gmtime, strftime
import cv2
import numpy as np
from Analyze import ArrowHandler, TargetHandler
from send_json import Status, jsonPipe

logger = logging.getLogger("Server_logger")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class targetCamera():

    def __init__(self, conn):
        self.conn = conn
        self.ArrowHandler = ArrowHandler("LEFT")
        self.TargetHandler = TargetHandler("LEFT")
        self.cali = True
        self.jsonpipe = jsonPipe()

    def func_ready(self, clients_list):
        logger.debug(f"Ready request received")
        if len(clients_list) == 1:
            self.conn.send(str.encode("1"))
            logger.debug(f"Replied 1 to ready request")
        else:
            self.conn.send(str.encode("0"))
            logger.debug(f"Replied 0 to ready request")

    def func_id(self):
        self.conn.sendall(b'\00')
        self.id = self.conn.recv(100).decode('utf-8')
        logger.info(f"Received id {self.id}")
        self.status = Status("target{}".format(self.id[-1]))
        self.status.write_status(1)
        return(self.id)

    def func_image(self):
        self.conn.sendall(b'\00')
        bs = self.conn.recv(8)
        logger.debug("Recieving image lenght")
        (length,) = unpack('>Q', bs)
        data = b''
        while len(data) < length:
            to_read = length - len(data)
            data += self.conn.recv(
                4096 if to_read > 4096 else to_read)
        assert len(b'\00') == 1

        with open("current_image", "wb") as f:
            f.write(data)
        img = cv2.imread("current_image", 1)
        img = cv2.resize(img, (2000, 2000))

        if self.cali == True:
            logger.info("CALIBRATE")
            try:
                self.ArrowHandler.calibrate(img)
                self.TargetHandler.findZones(img)
            except:
                logger.warning("No target found !")
                return
            # self.jsonpipe.write_zones(self.id[-1], self.TargetHandler.main_ellipse.values())
            self.impacts = []
            self.impacts_flat = []
            self.point = None
            self.points = []
            self.score = 0
            self.cali = False

        computer_vis = np.zeros(img.shape, dtype=np.uint8)
        computer_vis_flat = np.zeros(img.shape, dtype=np.uint8)
        impact = self.ArrowHandler.newest_impact(img)

        if impact is not None:
            logger.info(f"New impact detected : {impact}")
            self.impacts.append(impact)
            self.impacts_flat.append(self.TargetHandler.change_to_flat(self.TargetHandler.main_ellipse["center"],
                                                            self.TargetHandler.main_ellipse["a"],
                                                            self.TargetHandler.main_ellipse["b"],
                                                            impact)
                                                            )
            self.point = self.ArrowHandler.get_point(impact, self.TargetHandler.zones)
            self.points.append(self.point)
            self.score += self.point
            logger.info(f"Point : {self.point}")
            self.jsonpipe.write_impact(self.id[-1], self.impacts_flat, self.points)

        for contour in self.TargetHandler.zones:
            cv2.drawContours(computer_vis, contour, -1, (255, 0, 0), 5)
        for imp in self.impacts:
            cv2.circle(computer_vis, imp, 13, (0, 255, 255), -1)

        cv2.drawContours(computer_vis, self.ArrowHandler.target_space, -1, (0,255,0), 3)
        cv2.putText(computer_vis, f"Last arrow : {self.point}", org=(100, 100),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=3, color=(0, 0, 255), thickness=3)
        cv2.putText(computer_vis, f"Score : {self.score}", org=(1400, 100),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=3, color=(0, 0, 255), thickness=3)

        cv2.circle(computer_vis_flat, (1000, 1000), 500, (0, 255, 255), 3)


        for polar_coord in self.impacts_flat:
            x = 500 * polar_coord[0] * math.cos(polar_coord[1]) + 1000
            y = 500 * polar_coord[0] * math.sin(polar_coord[1]) + 1000
            cv2.circle(computer_vis_flat, (int(x), int(y)), 13, (0, 255, 255), -1)


        cv2.imshow("computer_vis_flat", cv2.resize(computer_vis_flat, (500, 500)))
        cv2.imshow("img", cv2.resize(img, (500, 500)))
        cv2.imshow("Computer vision", cv2.resize(computer_vis, (500, 500)))
        cv2.waitKey(1)

        self.conn.sendall(b'\00')
        logger.debug("send acknoledgment")

    def func_cali(self):
        self.cali = True
        self.conn.sendall(b'\00')


class Server():

    def __init__(self, server_ip, port):
        self.status = Status("server")
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server = 'localhost'
        self.port = port
        self.server_ip = server_ip
        try:
            self.s.bind((self.server_ip,self.port))
            logger.info("Server created succesfully")
            logger.info(f"Server running | Hosted by {self.server_ip} on port {self.port}")
            self.status.write_status(1)

        except socket.error as e:
            logger.warning(f"Error while creating server : {e}")

    def threaded_client(self, conn):
        self.conn.settimeout(3.0)
        tc = targetCamera(conn)

        while len(self.clients):
            try:
                data = self.conn.recv(40000)
                reply = data.decode('utf-8')
                logger.debug(f"Received {reply}")

                if not data:
                    self.conn.send(str.encode("Goodbye"))
                    logger.warning(f"No data reveived from {tc.id}")
                    break
                elif reply == 'rqst img':
                    ...
                elif reply == 'ready':
                    tc.func_ready(self.clients)
                elif reply == 'id':
                    tc.func_id()
                elif reply == "IMAGE":
                    tc.func_image()
                elif reply == "calibrate":
                    tc.func_cali()

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                logger.error(exc_type, fname, exc_tb.tb_lineno)
                logger.error(f"{e}")
                tc.status.write_status(0)
                break

        logger.warning(f"Connection lost with {tc.id}")
        self.clients.remove(self.conn)
        if len(self.clients) < 1:
            self.status.write_status(3)

    def run_server(self):
        self.s.listen(2)
        logger.info("waiting for connections ...")

        self.clients = []
        while True:
            if len(self.clients) < 1:
                self.status.write_status(3)
            self.conn, addr = self.s.accept()
            self.clients.append(self.conn)
            logger.info(f"Connected to {addr}")
            self.status.write_status(2)
            start_new_thread(self.threaded_client, (self.conn,))
            logger.info(f"Starting thread for conn of addr {addr}")



if __name__ == "__main__":
    try:
        server = Server("192.168.1.40", 5000)
        server.run_server()
    except KeyboardInterrupt:
        print("recievd KeyboardInterrupt, shutting down...")
        server.status.reset()
