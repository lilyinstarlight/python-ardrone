import struct


def decode(packet):
    """Decode a navdata packet."""
    offset = 0

    _ = struct.unpack_from('IIII', packet, offset)
    s = _[1]
    state = dict()
    state['fly']                 = s       & 1 # FLY MASK : (0) ardrone is landed, (1) ardrone is flying
    state['video']               = s >>  1 & 1 # VIDEO MASK : (0) video disable, (1) video enable
    state['vision']              = s >>  2 & 1 # VISION MASK : (0) vision disable, (1) vision enable
    state['control']             = s >>  3 & 1 # CONTROL ALGO (0) euler angles control, (1) angular speed control
    state['altitude']            = s >>  4 & 1 # ALTITUDE CONTROL ALGO : (0) altitude control inactive (1) altitude control active
    state['user_feedback_start'] = s >>  5 & 1 # USER feedback : Start button state
    state['command']             = s >>  6 & 1 # Control command ACK : (0) None, (1) one received
    state['fw_file']             = s >>  7 & 1 # Firmware file is good (1)
    state['fw_ver']              = s >>  8 & 1 # Firmware update is newer (1)
    state['fw_upd']              = s >>  9 & 1 # Firmware update is ongoing (1)
    state['navdata_demo']        = s >> 10 & 1 # Navdata demo : (0) All navdata, (1) only navdata demo
    state['navdata_bootstrap']   = s >> 11 & 1 # Navdata bootstrap : (0) options sent in all or demo mode, (1) no navdata options sent
    state['motors']              = s >> 12 & 1 # Motor status : (0) Ok, (1) Motors problem
    state['com_lost']            = s >> 13 & 1 # Communication lost : (1) com problem, (0) Com is ok
    state['vbat_low']            = s >> 15 & 1 # VBat low : (1) too low, (0) Ok
    state['user_el']             = s >> 16 & 1 # User Emergency Landing : (1) User EL is ON, (0) User EL is OFF
    state['timer_elapsed']       = s >> 17 & 1 # Timer elapsed : (1) elapsed, (0) not elapsed
    state['angles_out_of_range'] = s >> 19 & 1 # Angles : (0) Ok, (1) out of range
    state['ultrasound']          = s >> 21 & 1 # Ultrasonic sensor : (0) Ok, (1) deaf
    state['cutout']              = s >> 22 & 1 # Cutout system detection : (0) Not detected, (1) detected
    state['pic_version']         = s >> 23 & 1 # PIC Version number OK : (0) a bad version number, (1) version number is OK
    state['atcodec_thread_on']   = s >> 24 & 1 # ATCodec thread ON : (0) thread OFF (1) thread ON
    state['navdata_thread_on']   = s >> 25 & 1 # Navdata thread ON : (0) thread OFF (1) thread ON
    state['video_thread_on']     = s >> 26 & 1 # Video thread ON : (0) thread OFF (1) thread ON
    state['acq_thread_on']       = s >> 27 & 1 # Acquisition thread ON : (0) thread OFF (1) thread ON
    state['ctrl_watchdog']       = s >> 28 & 1 # CTRL watchdog : (1) delay in control execution (> 5ms), (0) control is well scheduled
    state['adc_watchdog']        = s >> 29 & 1 # ADC Watchdog : (1) delay in uart2 dsr (> 5ms), (0) uart2 is good
    state['com_watchdog']        = s >> 30 & 1 # Communication Watchdog : (1) com problem, (0) Com is ok
    state['emergency']           = s >> 31 & 1 # Emergency landing : (0) no emergency, (1) emergency

    data = dict()
    data['state'] = state
    data['header'] = _[0]
    data['sequence'] = _[2]
    data['vision'] = _[3]

    offset += struct.calcsize('IIII')

    demo_fields = [
        'ctrl_state',
        'battery',
        'theta',
        'phi',
        'psi',
        'altitude',
        'vx',
        'vy',
        'vz',
        'num_frames'
    ]
    angles = ['theta', 'phi', 'psi']
    while True:
        try:
            id_nr, size = struct.unpack_from('HH', packet, offset)
            offset += struct.calcsize('HH')
        except struct.error:
            break

        values = []
        for i in range(size - struct.calcsize('HH')):
            values.append(struct.unpack_from('c', packet, offset)[0])
            offset += struct.calcsize('c')

        if id_nr == 0:
            values = struct.unpack_from('IIfffIfffI', b''.join(values))
            demo = dict(zip(demo_fields, values))
            for a in angles:
                demo[a] = int(demo[a] / 1000)

            data['demo'] = demo

    return data
