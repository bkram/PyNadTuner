import serial
from time import sleep


class NadGetters:
    """
    a class containing the binary get commands
    """

    def __init__(self):
        self.AM_FREQUENCY = bytes([1, 20, 44, 2, 191])
        self.BAND = bytes([1, 20, 43, 2, 192])
        self.BLEND = bytes([1, 20, 49, 2, 186])
        self.DEVICE_ID = bytes([1, 20, 20, 2, 215])
        self.FM_FREQUENCY = bytes([1, 20, 45, 2, 190])
        self.FM_MUTE = bytes([1, 20, 47, 2, 188])
        self.POWER = bytes([1, 20, 21, 2, 214])


class NadSetters:
    """
    a class containing the binary set commands
    """

    def __init__(self):
        self.AM = bytes([0x01, 0x16, 0x82, 0x02, 0x67])
        self.BLEND = bytes([0x01, 0x16, 0x35, 0x02, 0xB4])
        self.BLEND_OFF = bytes([1, 21, 49, 94, 64, 2, 185])
        self.BLEND_ON = bytes([1, 21, 49, 94, 65, 2, 184])
        self.BRIGHTNESS_FULL = bytes([1, 21, 22, 94, 64, 2, 212])
        self.BRIGHTNESS_MED = bytes([1, 21, 22, 94, 65, 2, 211])
        self.BRIGHTNESS_OFF = bytes([1, 21, 22, 94, 66, 2, 210])
        self.DIGIT_0 = bytes([0x01, 0x16, 0xC7, 0x02, 0x22])
        self.DIGIT_1 = bytes([0x01, 0x16, 0x8A, 0x02, 0x5F])
        self.DIGIT_2 = bytes([0x01, 0x16, 0x8E, 0x02, 0x5B])
        self.DIGIT_3 = bytes([0x01, 0x16, 0x92, 0x02, 0x57])
        self.DIGIT_4 = bytes([0x01, 0x16, 0x96, 0x02, 0x53])
        self.DIGIT_5 = bytes([0x01, 0x16, 0x8B, 0x02, 0x5E, 0x5E])
        self.DIGIT_6 = bytes([0x01, 0x16, 0x8F, 0x02, 0x5A])
        self.DIGIT_7 = bytes([0x01, 0x16, 0x93, 0x02, 0x56])
        self.DIGIT_8 = bytes([0x01, 0x16, 0x97, 0x02, 0x52])
        self.DIGIT_9 = bytes([0x01, 0x16, 0x98, 0x02, 0x51])
        self.DIMMER = bytes([0x01, 0x16, 0xF2, 0x02, 0xF7])
        self.DISPLAY = bytes([0x01, 0x16, 0x26, 0x02, 0xC3])
        self.FM = bytes([0x01, 0x16, 0x81, 0x02, 0x68])
        self.FM_MUTE = bytes([0x01, 0x16, 0x37, 0x02, 0xB2])
        self.FM_MUTE_OFF = bytes([1, 21, 47, 94, 64, 2, 187])
        self.FM_MUTE_ON = bytes([1, 21, 47, 94, 65, 2, 186])
        self.POWER_OFF = bytes([0x1, 0x16, 0xF1, 0x02, 0xF8])
        self.POWER_ON = bytes([0x01, 0x16, 0xF0, 0x02, 0xF9])
        self.PRESET_DOWN = bytes([0x01, 0x16, 0xD1, 0x02, 0x18])
        self.PRESET_UP = bytes([0x01, 0x16, 0xD1, 0x02, 0x18])
        self.SLEEP = bytes([0x01, 0x16, 0xF3, 0x02, 0xF6])
        self.TUNER_AM = bytes([1, 21, 43, 94, 64, 2, 191])
        self.TUNER_FM = bytes([1, 21, 43, 94, 65, 2, ])
        self.TUNE_DOWN = bytes([0x01, 0x16, 0xD3, 0x02, 0x16])
        self.TUNE_UP = bytes([0x01, 0x16, 0xD4, 0x02, 0x15])


class NadTuner:
    """
    A class to communicate with NAD C-425 and C-426 tuners.
    """

    def __init__(self, port='/dev/ttyUSB0'):
        """
        __init__
        :param port: serial port to use if the default=/dev/ttyUSB0 is not correct
        """
        self.band = None
        self.id = None
        self.power = None
        self.frequency = None
        self.blend = None
        self.fmmute = None
        self.__port__ = port
        self.__serial__ = serial.Serial(port, 9600,
                                        exclusive=False, )  # open serial port
        self.setter = NadSetters()
        self.getter = NadGetters()

    def __read_bytes__(self):
        """
        Read command set of bytes
        :return: the command set read
        """

        response = bytes()
        while True:
            r = self.__serial__.read(1)
            if r == b'':
                continue
            elif r == b'\x01':
                response = response + r
            elif r == b'\x02':
                response = response + r
                r = self.__serial__.read(1)
                response = response + r
                break
            else:
                response = response + r
        return response

    def serial_send(self, message):
        """
        :param message: serial command in bytes to send
        :return: None
        """
        self.__serial__.write(message)
        sleep(DELAY)

    def serial_query(self, message, responsecode):
        """
        :param message: command in bytes to send
        :param responsecode: response code to wait for
        :return: queury response bytes
        """
        self.__serial__.write(message)

        attempts = 0
        while attempts <= 5:
            response = self.__read_bytes__()
            # Skip RDS Data
            if response[2] == 83:
                continue
            if response[2] == responsecode:
                return response
            attempts += 1
        return False

    def get_band(self):
        """
        Get the current operation band
        :return: band
        """

        response = self.serial_query(self.getter.BAND, responsecode=43)
        if response[4] == 64:
            self.band = 'AM'
        elif response[4] == 65:
            self.band = 'FM'
        return self.band

    def get_device_id(self):
        """
        Get the device id
        :return: Device Id
        """

        self.id = self.serial_query(self.getter.DEVICE_ID, responsecode=20)[
            3:7].decode('utf-8')
        return self.id

    def get_frequency_fm(self, force=False):
        """
        Get the current tuned FM Frequency
        :param force: Force retrival
        :return: Frequency
        """

        if not self.frequency or force:
            attempts = 0
            while attempts < 20:
                response = self.serial_query(
                    self.getter.FM_FREQUENCY, responsecode=45)

                if response is False:
                    continue
                if response[5] == 2:
                    freq_bytes = bytes([response[3], response[4]])
                    self.frequency = int.from_bytes(freq_bytes, "little") / 100
                else:
                    freq_bytes = bytes([response[4], response[5]])
                    self.frequency = int.from_bytes(freq_bytes, "little") / 100
                # break
                attempts += 1

        return self.frequency

    def get_power(self):
        """
        :returns: Power
        """

        power = self.serial_query(self.getter.POWER, responsecode=21)

        if power[4] == 64:
            self.power = False
        elif power[4] == 65:
            self.power = True
        return self.power

    def set_frequency_fm(self, frequency):
        """
        Sets the frequency
        :param frequency:
        :return: the set frequency
        """

        for c in str(round(frequency * 100)):
            if c == "0":
                self.serial_send(self.setter.DIGIT_0)
            if c == "1":
                self.serial_send(self.setter.DIGIT_1)
            if c == "2":
                self.serial_send(self.setter.DIGIT_2)
            if c == "3":
                self.serial_send(self.setter.DIGIT_3)
            if c == "4":
                self.serial_send(self.setter.DIGIT_4)
            if c == "5":
                self.serial_send(self.setter.DIGIT_5)
            if c == "6":
                self.serial_send(self.setter.DIGIT_6)
            if c == "7":
                self.serial_send(self.setter.DIGIT_7)
            if c == "8":
                self.serial_send(self.setter.DIGIT_8)
            if c == "9":
                self.serial_send(self.setter.DIGIT_9)
            self.frequency = frequency
        return self.frequency

    def set_power_on(self):
        """
        Power on tuner
        """

        self.serial_send(self.setter.POWER_ON)
        self.power = True
        return self.power

    def set_power_off(self):
        """
        Power off tuner
        """

        self.serial_send(self.setter.POWER_OFF)
        self.power = False
        return self.power

    def set_tune_up(self):
        """
        Tunes up 0,5 Mhz
        """

        self.serial_send(self.setter.TUNE_UP)

    def set_tune_down(self):
        """
        Tunes down 0,5 Mhz
        """

        self.serial_send(self.setter.TUNE_DOWN)

    def set_sleep(self):
        """
        Sets the sleep timer, 30,60,90 off depending on the amount of invocations
        """

        self.serial_send(self.setter.SLEEP)

    def set_display_off(self):
        """
        Turns off the LCD Display
        """

        self.serial_send(self.setter.BRIGHTNESS_OFF)

    def set_display_on(self):
        """
        Turns on the LCD Display
        """

        self.serial_send(self.setter.BRIGHTNESS_FULL)

    def set_display_dimmed(self):
        """
        Dims on the LCD Display
        """

        self.serial_send(self.setter.BRIGHTNESS_MED)

    def set_band(self, band='FM'):
        """
        :params: band to select
        :returns: band
        """

        if band == "FM":
            self.serial_send(self.setter.FM)
        elif band == 'AM':
            self.serial_send(self.setter.AM)
        self.band = band
        return band


DELAY = 0.2
