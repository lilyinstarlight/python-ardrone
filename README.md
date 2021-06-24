python-ardrone
==============

_**Note: This library is looking for testers and/or maintainers! I have not had access myself to an AR.Drone 2.0 for a while, but there are several important unreleased changes that need testing on actual hardware as well as [stuff that still needs to be done](TODO.md) to make the library more robust. Open a new issue on this repository if you are interested!**_

A Python library for controlling the Parrot AR.Drone 2.0 over a network.


Usage
-----

```python
import ardrone

drone = ardrone.ARDrone()

drone.takeoff()
drone.land()

print(drone.navdata['demo']['battery'])

drone.image.show()

drone.halt()
```


Thanks
------

Thanks to Bastian Venthur for making the beginnings on which this library was based at https://github.com/venthur/python-ardrone!
