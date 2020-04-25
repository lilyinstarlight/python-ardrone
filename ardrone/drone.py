"""
Python library for the AR.Drone.
"""

import time
import threading

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

        self.sequence = 1
        self.timer = 0.2
        self.com_watchdog_timer = threading.Timer(self.timer, self.commwdg)
        self.lock = threading.Lock()
        self.speed = 0.2
        self.at(ardrone.at.config, 'general:navdata_demo', 'TRUE')
        self.at(ardrone.at.config, 'control:control_level', '3')
        self.at(ardrone.at.config, 'control:altitude_max', '20000')

        self.image = None
        self.navdata = None

        self.video_thread = ardrone.network.VidThread(
            self.host,
            self.image_callback
        )
        self.navdata_thread = ardrone.network.NavThread(
            self.host,
            self.navdata_callback
        )
        self.video_thread.start()
        self.navdata_thread.start()

        self.time = 0

    def image_callback(self, im_data):
        w, h, img = im_data
        self.image = PIL.Image.frombuffer('RGB', (w, h), img, 'raw', 'RGB', 0, 1)

    def navdata_callback(self, navdata):
        self.navdata = navdata

    def takeoff(self):
        """Make the drone takeoff."""
        self.at(ardrone.at.ref, True)

    def land(self):
        """Make the drone land."""
        self.at(ardrone.at.ref, False)

    def hover(self):
        """Make the drone hover."""
        self.at(ardrone.at.pcmd, False, 0, 0, 0, 0)

    def move_left(self):
        """Make the drone move left."""
        self.at(ardrone.at.pcmd, True, -self.speed, 0, 0, 0)

    def move_right(self):
        """Make the drone move right."""
        self.at(ardrone.at.pcmd, True, self.speed, 0, 0, 0)

    def move_up(self):
        """Make the drone rise upwards."""
        self.at(ardrone.at.pcmd, True, 0, 0, self.speed, 0)

    def move_down(self):
        """Make the drone decent downwards."""
        self.at(ardrone.at.pcmd, True, 0, 0, -self.speed, 0)

    def move_forward(self):
        """Make the drone move forward."""
        self.at(ardrone.at.pcmd, True, 0, -self.speed, 0, 0)

    def move_backward(self):
        """Make the drone move backwards."""
        self.at(ardrone.at.pcmd, True, 0, self.speed, 0, 0)

    def turn_left(self):
        """Make the drone rotate left."""
        self.at(ardrone.at.pcmd, True, 0, 0, 0, -self.speed)

    def turn_right(self):
        """Make the drone rotate right."""
        self.at(ardrone.at.pcmd, True, 0, 0, 0, self.speed)

    def reset(self):
        """Toggle the drone's emergency state."""
        self.at(ardrone.at.ref, False, True)
        time.sleep(0.1)
        self.at(ardrone.at.ref, False, False)

    def trim(self):
        """Flat trim the drone."""
        self.at(ardrone.at.ftrim)

    def set_cam(self, cam):
        """Set active camera.

        Valid values are 0 for the front camera and 1 for the bottom camera
        """
        self.at(ardrone.at.config, 'video:video_channel', cam)

    def set_speed(self, speed):
        """Set the drone's speed.

        Valid values are floats from [0..1]
        """
        self.speed = speed

    def at(self, cmd, *args, **kwargs):
        """Wrapper for the low level at commands.

        This method takes care that the sequence number is increased after each
        at command and the watchdog timer is started to make sure the drone
        receives a command at least every second.
        """
        with self.lock:
            self.com_watchdog_timer.cancel()
            cmd(self.host, self.sequence, *args, **kwargs)
            self.sequence += 1
            self.com_watchdog_timer = threading.Timer(self.timer, self.commwdg)
            self.com_watchdog_timer.start()

    def commwdg(self):
        """Communication watchdog signal.

        This needs to be sent regularly to keep the communication
        with the drone alive.
        """
        self.at(ardrone.at.comwdg)

    def halt(self):
        """Shutdown the drone.

        This method does not land or halt the actual drone, but the
        communication with the drone. You should call it at the end of your
        application to close all sockets, pipes, processes and threads related
        with this object.
        """
        with self.lock:
            self.com_watchdog_timer.cancel()
            self.video_thread.stop()
            self.video_thread.join()
            self.navdata_thread.stop()
            self.navdata_thread.join()

    def move(self, lr, fb, vv, va):
        """Makes the drone move (translate/rotate).

        Parameters:
        lr -- left-right tilt: float [-1..1] negative: left, positive: right
        fb -- front-back tilt: float [-1..1] negative: forwards, positive:
            backwards
        vv -- vertical speed: float [-1..1] negative: go down, positive: rise
        va -- angular speed: float [-1..1] negative: spin left, positive: spin
            right"""
        self.at(ardrone.at.pcmd, True, lr, fb, vv, va)

    def move2(self, vv, va):
        """Makes the drone move (up-down and rotate only) while trying
        to stay above the same point on the ground.

        Parameters:
        vv -- vertical speed: float [-1..1] negative: go down, positive: rise
        va -- angular speed: float [-1..1] negative: spin left, positive: spin
            right"""
        self.at(ardrone.at.pcmd, False, 0, 0, vv, va)
