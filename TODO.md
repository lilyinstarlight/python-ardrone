TODO
====

- follow ar.drone developer guide where reasonable (e.g. repeatedly send takeoff commands until they are acknowledged in a navdata)
- move more constants into `ardrone.constant`
- reduce latency by always decoding i-frames and only decoding p-frames if they are in the buffer
- add image callbacks
- implement logging
- add connection detection
- add ready callbacks and blocking methods
- enumate other navdata types (i.e. all of the id\_nr values and all of the ctrl\_state values)
- gracefully quit when ctrl+c is pressed or `sys.exit`
