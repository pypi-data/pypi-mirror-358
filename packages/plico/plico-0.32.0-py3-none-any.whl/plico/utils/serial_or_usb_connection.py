'''
Serial/USB connection dynamic lookup
'''

import serial.tools.list_ports


class SerialOrUSBException(Exception):
    pass


class SerialOrUSBConnection:

    def __init__(self, comport=None, usb_serial_number=None, usb_vendor_id=None, usb_product_id=None):
        '''
        comport: serial connection port, if known.
        usb_serial_number: device USB serial number, if known. Either the com
                           port or the device serial number must be specified.
        '''
        if (comport is None and usb_serial_number is None and
           ((usb_vendor_id is None) or (usb_product_id is None))):
            raise Exception('At least one of comport, usb_serial_number or usb vendor/product ID must be set')

        self.comport = comport
        self.usb_serial_number = usb_serial_number
        self.usb_vendor_id = usb_vendor_id
        self.usb_product_id = usb_product_id

    @staticmethod
    def fromConfiguration(configuration, section_name):
        try:
            comport = configuration.getValue(section_name, 'port')
        except KeyError:
            comport = None
        try:
            usb_serial_number = configuration.getValue(section_name, 'usb_serial_number')
        except KeyError:
            usb_serial_number = None
        try:
            usb_vendor_id = configuration.getValue(section_name, 'usb_vendor_id')
            usb_vendor_id = int(usb_vendor_id, 0)
        except KeyError:
            usb_vendor_id = None
        try:
            usb_product_id = configuration.getValue(section_name, 'usb_product_id')
            usb_product_id = int(usb_product_id, 0)
        except KeyError:
            usb_product_id = None
        return SerialOrUSBConnection(comport, usb_serial_number, usb_vendor_id, usb_product_id)

    def port_name(self):
        '''
        Returns the serial port name, either because if was specified
        in the constructor, or because it was found by looking up
        the USB serial number. Raises a ConnectionException if not found
        '''
        if self.comport:
            return self.comport

        usbport = self.device_by_serial_number(self.usb_serial_number)
        if usbport:
            return usbport

        usbport = self.device_by_id(self.usb_vendor_id, self.usb_product_id)
        if usbport:
            return usbport

        errmsg = 'No COM port specified and/or USB serial number not found'
        raise SerialOrUSBException(errmsg)

    @staticmethod
    def device_by_serial_number(serial_number):
        '''
        Returns the device path (i.e. '/dev/ttyUSB1') for the
        USB device identified by the serial_number, or None
        if the device is not found.
        '''
        if serial_number is None:
            return None
        ports = serial.tools.list_ports.comports()
        my_ports = [x for x in ports if x.serial_number == serial_number]
        if len(my_ports) > 0:
            return my_ports[0].device
        else:
            return None

    @staticmethod
    def device_by_id(vendor_id, product_id):
        '''
        Returns the device path (i.e. '/dev/ttyUSB1') for the
        USB device identified by the vendor and product id,
        or None if the device is not found.
        '''
        if vendor_id is None or product_id is None:
            return None

        hwid = '%04X:%04X' % (vendor_id, product_id)
        ports = serial.tools.list_ports.comports()
        my_ports = [x for x in ports if hwid in x.hwid]
        if len(my_ports) > 0:
            return my_ports[0].device
        else:
            return None

# ___oOo___

