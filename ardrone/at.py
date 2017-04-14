import socket
import struct

import ardrone.constant


def f2i(f):
    """Interpret IEEE-754 floating-point value as signed integer.

    Arguments:
    f -- floating point value
    """
    return struct.unpack('i', struct.pack('f', f))[0]


def ref(host, seq, takeoff, emergency=False):
    """
    Basic behaviour of the drone: take-off/landing, emergency stop/reset)

    Parameters:
    seq -- sequence number
    takeoff -- True: Takeoff / False: Land
    emergency -- True: Turn off the engines
    """
    p = 0b10001010101000000000000000000
    if takeoff:
        p |= 0b1000000000
    if emergency:
        p |= 0b100000000
    at(host, 'REF', seq, [p])


def pcmd(host, seq, progressive, lr, fb, vv, va):
    """
    Makes the drone move (translate/rotate).

    Parameters:
    seq -- sequence number
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
    at(host, 'PCMD', seq, [p, float(lr), float(fb), float(vv), float(va)])


def ftrim(host, seq):
    """
    Tell the drone it's lying horizontally.

    Parameters:
    seq -- sequence number
    """
    at(host, 'FTRIM', seq, [])


def zap(host, seq, stream):
    """
    Selects which video stream to send on the video UDP port.

    Parameters:
    seq -- sequence number
    stream -- Integer: video stream to broadcast
    """
    # FIXME: improve parameters to select the modes directly
    at(host, 'ZAP', seq, [stream])


def config(host, seq, option, value):
    """Set configuration parameters of the drone."""
    at(host, 'CONFIG', seq, [str(option), str(value)])


def comwdg(host, seq):
    """
    Reset communication watchdog.
    """
    # FIXME: no sequence number
    at(host, 'COMWDG', seq, [])


def aflight(host, seq, flag):
    """
    Makes the drone fly autonomously.

    Parameters:
    seq -- sequence number
    flag -- Integer: 1: start flight, 0: stop flight
    """
    at(host, 'AFLIGHT', seq, [flag])


def pwm(host, seq, m1, m2, m3, m4):
    """
    Sends control values directly to the engines, overriding control loops.

    Parameters:
    seq -- sequence number
    m1 -- Integer: front left command
    m2 -- Integer: front right command
    m3 -- Integer: back right command
    m4 -- Integer: back left command
    """
    at(host, 'PWM', seq, [m1, m2, m3, m4])


def led(host, seq, anim, f, d):
    """
    Control the drones LED.

    Parameters:
    seq -- sequence number
    anim -- Integer: animation to play
    f -- Float: frequency in HZ of the animation
    d -- Integer: total duration in seconds of the animation
    """
    at(host, 'LED', seq, [anim, float(f), d])


def anim(host, seq, anim, d):
    """
    Makes the drone execute a predefined movement (animation).

    Parameters:
    seq -- sequcence number
    anim -- Integer: animation to play
    d -- Integer: total duration in seconds of the animation
    """
    at(host, 'ANIM', seq, [anim, d])

def at(host, command, seq, params):
    """
    Parameters:
    command -- the command
    seq -- the sequence number
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
    msg = 'AT*{:s}={:d},{:s}\r'.format(command, seq, ','.join(params_str))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(msg.encode(), (host, ardrone.constant.COMMAND_PORT))
