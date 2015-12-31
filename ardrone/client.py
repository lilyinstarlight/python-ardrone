from __future__ import print_function

import fcntl
import sys
import termios
import os

import ardrone

if len(sys.argv) != 1 and len(sys.argv) != 2:
    print('usage: ' + sys.argv[0] + ' [host]')
    sys.exit(1)

fd = sys.stdin.fileno()

oldterm = termios.tcgetattr(fd)
newattr = termios.tcgetattr(fd)
newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
termios.tcsetattr(fd, termios.TCSANOW, newattr)

oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

if len(sys.argv) >= 2:
    drone = ardrone.ARDrone(sys.argv[1])
else:
    drone = ardrone.ARDrone()

try:
    while 1:
        try:
            c = sys.stdin.read(1).lower()

            if c == 'q':
                break
            elif c == 'a':
                drone.move_left()
            elif c == 'd':
                drone.move_right()
            elif c == 'w':
                drone.move_forward()
            elif c == 's':
                drone.move_backward()
            elif c == ' ':
                drone.land()
            elif c == '\n':
                drone.takeoff()
            elif c == 'q':
                drone.turn_left()
            elif c == 'e':
                drone.turn_right()
            elif c == '1':
                drone.move_up()
            elif c == '2':
                drone.hover()
            elif c == '3':
                drone.move_down()
            elif c == 't':
                drone.reset()
            elif c == 'x':
                drone.hover()
            elif c == 'y':
                drone.trim()
        except IOError:
            pass
finally:
    termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
    fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
    drone.halt()
