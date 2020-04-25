import socket
import struct
import threading

import ardrone.constant


def f2i(f):
    """Interpret IEEE-754 floating-point value as signed integer.

    Arguments:
    f -- floating point value
    """
    return struct.unpack('i', struct.pack('f', f))[0]


class ATCommand(object):
    def __init__(self, host):
        """
        Open a new AT command socket

        Parameters:
        host -- destination address
        """
        self.host = host
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.seq = 1
        self.interval = 0.2

        self.comwdg_timer = threading.Timer(self.interval, self.comwdg)
        self.lock = threading.Lock()

    def halt(self):
        """
        Halts communication with the drone
        """
        self.comwdg_timer.cancel()

    def ref(self, takeoff, emergency=False):
        """
        Basic behaviour of the drone: take-off/landing, emergency stop/reset)

        Parameters:
        takeoff -- True: Takeoff / False: Land
        emergency -- True: Turn off the engines
        """
        p = 0b10001010101000000000000000000
        if takeoff:
            p |= 0b1000000000
        if emergency:
            p |= 0b100000000
        self.at('REF', [p])

    def pcmd(self, progressive, lr, fb, vv, va):
        """
        Makes the drone move (translate/rotate).

        Parameters:
        progressive -- True: enable progressive commands, False: disable (i.e.
            enable hovering mode)
        lr -- left-right tilt: float [-1..1] negative: left, positive: right
        rb -- front-back tilt: float [-1..1] negative: forwards, positive:
            backwards
        vv -- vertical speed: float [-1..1] negative: go down, positive: rise
        va -- angular speed: float [-1..1] negative: spin left, positive: spin
            right

        The above float values are a percentage of the maximum speed.
        """
        p = 1 if progressive else 0
        self.at('PCMD', [p, float(lr), float(fb), float(vv), float(va)])

    def ftrim(self):
        """
        Tell the drone it's lying horizontally.
        """
        self.at('FTRIM')

    def zap(self, stream):
        """
        Selects which video stream to send on the video UDP port.

        Parameters:
        stream -- Integer: video stream to broadcast
        """
        # FIXME: improve parameters to select the modes directly
        self.at('ZAP', [stream])

    def config(self, option, value):
        """Set configuration parameters of the drone."""
        self.at('CONFIG', [str(option), str(value)])

    def comwdg(self):
        """
        Reset communication watchdog.
        """
        self.at('COMWDG')

    def aflight(self, flag):
        """
        Makes the drone fly autonomously.

        Parameters:
        flag -- Integer: 1: start flight, 0: stop flight
        """
        self.at('AFLIGHT', [flag])

    def pwm(self, m1, m2, m3, m4):
        """
        Sends control values directly to the engines, overriding control loops.

        Parameters:
        m1 -- Integer: front left command
        m2 -- Integer: front right command
        m3 -- Integer: back right command
        m4 -- Integer: back left command
        """
        self.at('PWM', [m1, m2, m3, m4])

    def led(self, anim, f, d):
        """
        Control the drones LED.

        Parameters:
        anim -- Integer: animation to play
        f -- Float: frequency in HZ of the animation
        d -- Integer: total duration in seconds of the animation
        """
        self.at('LED', [anim, float(f), d])

    def anim(self, anim, d):
        """
        Makes the drone execute a predefined movement (animation).

        Parameters:
        anim -- Integer: animation to play
        d -- Integer: total duration in seconds of the animation
        """
        self.at('ANIM', [anim, d])

    def at(self, command, params=[]):
        """
        Encodes and sends AT command

        Parameters:
        command -- the command
        params -- a list of elements which can be either int, float or string
        """
        params_str = []
        for p in params:
            if type(p) == int:
                params_str.append('{:d}'.format(p))
            elif type(p) == float:
                params_str.append('{:d}'.format(f2i(p)))
            elif type(p) == str:
                params_str.append('"{:s}"'.format(p))

        with self.lock:
            self.comwdg_timer.cancel()

            msg = 'AT*{:s}={:d}{:s}\r'.format(command, self.seq, ''.join(',' + param for param in params_str))
            self.sock.sendto(msg.encode(), (self.host, ardrone.constant.COMMAND_PORT))

            self.seq += 1

            self.comwdg_timer = threading.Timer(self.interval, self.comwdg)
            self.comwdg_timer.start()
