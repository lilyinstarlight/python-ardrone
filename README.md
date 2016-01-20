python-ardrone
==============

python-ardrone is a Python library for controlling the Parrot AR.Drone 2.0 over a network.


Usage
=====

```python
import ardrone

drone = ardrone.ARDrone()

drone.takeoff()
drone.land()

print(drone.navdata['demo']['battery'])

drone.image.show()

drone.halt()
```
