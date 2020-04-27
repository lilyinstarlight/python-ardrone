"""
Python library for the AR.Drone.
"""

import time
import multiprocessing

import PIL.Image

import ardrone.at
import ardrone.network


class ARDrone(object):
    """ARDrone Class.

    Instantiate this class to control your drone and receive decoded video and
    navdata.
    """

    def __init__(self, host='192.168.1.1'):
        self.host = host

        self.speed = 0.2

        self.atcmd = ardrone.at.ATCommand(self.host)
        self.atcmd.config('general:navdata_demo', 'TRUE')
        self.atcmd.config('control:altitude_max', '20000')
        self.video_pipe, video_pipe_other = multiprocessing.Pipe()
        self.nav_pipe, nav_pipe_other = multiprocessing.Pipe()
        self.com_pipe, com_pipe_other = multiprocessing.Pipe()
        self.network_process = ardrone.network.ARDroneNetworkProcess(self.host, nav_pipe_other, video_pipe_other, com_pipe_other)
        self.network_process.start()
        self.ipc_thread = ardrone.network.IPCThread(self)
        self.ipc_thread.start()

        self.image = PIL.Image.new('RGB', (640, 360))
        self.navdata = dict()

        self.time = 0

    def takeoff(self):
        """Make the drone takeoff."""
        self.atcmd.ref(True)

    def land(self):
        """Make the drone land."""
        self.atcmd.ref(False)

    def hover(self):
        """Make the drone hover."""
        self.atcmd.pcmd(False, 0, 0, 0, 0)

    def move_left(self):
        """Make the drone move left."""
        self.atcmd.pcmd(True, -self.speed, 0, 0, 0)

    def move_right(self):
        """Make the drone move right."""
        self.atcmd.pcmd(True, self.speed, 0, 0, 0)

    def move_up(self):
        """Make the drone rise upwards."""
        self.atcmd.pcmd(True, 0, 0, self.speed, 0)

    def move_down(self):
        """Make the drone decent downwards."""
        self.atcmd.pcmd(True, 0, 0, -self.speed, 0)

    def move_forward(self):
        """Make the drone move forward."""
        self.atcmd.pcmd(True, 0, -self.speed, 0, 0)

    def move_backward(self):
        """Make the drone move backwards."""
        self.atcmd.pcmd(True, 0, self.speed, 0, 0)

    def turn_left(self):
        """Make the drone rotate left."""
        self.atcmd.pcmd(True, 0, 0, 0, -self.speed)

    def turn_right(self):
        """Make the drone rotate right."""
        self.atcmd.pcmd(True, 0, 0, 0, self.speed)

    def reset(self):
        """Toggle the drone's emergency state."""
        self.atcmd.ref(False, True)
        time.sleep(0.1)
        self.atcmd.ref(False, False)

    def trim(self):
        """Flat trim the drone."""
        self.atcmd.ftrim

    def set_cam(self, cam):
        """Set active camera.

        Valid values are 0 for the front camera and 1 for the bottom camera
        """
        self.atcmd.config('video:video_channel', cam)

    def set_speed(self, speed):
        """Set the drone's speed.

        Valid values are floats from [0..1]
        """
        self.speed = speed

    def halt(self):
        """Shutdown the drone.

        This method does not land or halt the actual drone, but the
        communication with the drone. You should call it at the end of your
        application to close all sockets, pipes, processes and threads related
        with this object.
        """
        self.atcmd.halt()
        self.ipc_thread.stop()
        self.ipc_thread.join()
        self.network_process.terminate()
        self.network_process.join()

    def move(self, lr, fb, vv, va):
        """Makes the drone move (translate/rotate).

        Parameters:
        lr -- left-right tilt: float [-1..1] negative: left, positive: right
        fb -- front-back tilt: float [-1..1] negative: forwards, positive:
            backwards
        vv -- vertical speed: float [-1..1] negative: go down, positive: rise
        va -- angular speed: float [-1..1] negative: spin left, positive: spin
            right"""
        self.atcmd.pcmd(True, lr, fb, vv, va)
