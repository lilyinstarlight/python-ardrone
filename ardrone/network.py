"""
This module provides access to the data provided by the AR.Drone.
"""

import select
import socket
import struct
import threading

import ardrone.constant
import ardrone.navdata


class NavThread(threading.Thread):
    """Inter Process Communication Thread.

    This thread collects navdata from the navdata port and makes it available
    to the ARDrone.
    """

    def __init__(self, host, callback):
        threading.Thread.__init__(self)
        self.host = host
        self.callback = callback
        self.stopping = False

    def run(self):
        nav_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        nav_socket.setblocking(False)
        nav_socket.bind(('', ardrone.constant.NAVDATA_PORT))
        nav_socket.sendto(b'\x01\x00\x00\x00', (self.host, ardrone.constant.NAVDATA_PORT))

        while not self.stopping:
            inputready, outputready, exceptready = select.select([nav_socket], [], [])
            if len(inputready) < 1:
                continue
            while True:
                try:
                    data = nav_socket.recv(65535)
                except IOError:
                    # we consumed every packet from the socket and continue with the last one
                    break
            navdata = ardrone.navdata.decode(data)
            self.callback(navdata)
        nav_socket.close()

    def stop(self):
        """Stop the IPCThread activity."""
        self.stopping = True
