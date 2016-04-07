"""
This module provides access to the data provided by the AR.Drone.
"""

import select
import socket
import struct
import threading
import multiprocessing

import PIL.Image

import ardrone.constant
import ardrone.navdata
import ardrone.video


class ARDroneNetworkProcess(multiprocessing.Process):
    """ARDrone Network Process.

    This process collects data from the video and navdata port, converts the
    data and sends it to the IPCThread.
    """

    def __init__(self, host, nav_pipe, video_pipe, com_pipe):
        multiprocessing.Process.__init__(self)
        self.nav_pipe = nav_pipe
        self.video_pipe = video_pipe
        self.com_pipe = com_pipe
        self.host = host

    def run(self):
        video_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        video_socket.connect((self.host, ardrone.constant.VIDEO_PORT))

        nav_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        nav_socket.setblocking(False)
        nav_socket.bind(('', ardrone.constant.NAVDATA_PORT))
        nav_socket.sendto(b'\x01\x00\x00\x00', (self.host, ardrone.constant.NAVDATA_PORT))

        stopping = False
        while not stopping:
            inputready, outputready, exceptready = select.select([nav_socket, video_socket, self.com_pipe], [], [])
            for i in inputready:
                if i == video_socket:
                    # get first few bytes of header
                    data = video_socket.recv(12, socket.MSG_WAITALL)
                    if len(data) != 12:
                        continue

                    # decode relevant portions of the header
                    sig_p, sig_a, sig_v, sig_e, version, codec, header, payload = struct.unpack('4cBBHI', data)

                    # check signature (and ignore packet otherwise)
                    if sig_p != b'P' or sig_a != b'a' or sig_v != b'V' or sig_e != b'E':
                        continue

                    # get remaining frame
                    data += video_socket.recv(header - 12 + payload, socket.MSG_WAITALL)

                    try:
                        # decode the frame
                        image = ardrone.video.decode(data)
                        self.video_pipe.send(image)
                    except ardrone.video.DecodeError:
                        pass
                elif i == nav_socket:
                    while 1:
                        try:
                            data = nav_socket.recv(65535)
                        except IOError:
                            # we consumed every packet from the socket and
                            # continue with the last one
                            break
                    navdata = ardrone.navdata.decode(data)
                    self.nav_pipe.send(navdata)
                elif i == self.com_pipe:
                    _ = self.com_pipe.recv()
                    stopping = True
                    break
        video_socket.close()
        nav_socket.close()


class IPCThread(threading.Thread):
    """Inter Process Communication Thread.

    This thread collects the data from the ARDroneNetworkProcess and forwards
    it to the ARDrone.
    """

    def __init__(self, drone):
        threading.Thread.__init__(self)
        self.drone = drone
        self.stopping = False

    def run(self):
        while not self.stopping:
            inputready, outputready, exceptready = select.select([self.drone.video_pipe, self.drone.nav_pipe], [], [], 1)
            for i in inputready:
                if i == self.drone.video_pipe:
                    while self.drone.video_pipe.poll():
                        width, height, image = self.drone.video_pipe.recv()
                    self.drone.image = PIL.Image.frombuffer('RGB', (width, height), image, 'raw', 'RGB', 0, 1)
                elif i == self.drone.nav_pipe:
                    while self.drone.nav_pipe.poll():
                        navdata = self.drone.nav_pipe.recv()
                    self.drone.navdata = navdata

    def stop(self):
        """Stop the IPCThread activity."""
        self.stopping = True
