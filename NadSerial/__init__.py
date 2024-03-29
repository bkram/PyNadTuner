from time import sleep

import serial


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
        self.ENTER = bytes([1, 22, 197, 2, 36])


def crc_check(command):
    crc = sum(command) & 0xFF
    crc = (crc ^ 0xFF) + 1
    return command + bytes([2]) + bytes([crc])
    # return command + bytes([crc])


class Device:
    """
    A class to communicate with NAD C-425 and C-426 tuners.
    """

    def __init__(self, port='/dev/ttyUSB0'):
        """
        __init__
        :param port: serial port to use if the default=/dev/ttyUSB0 is not correct
        """

        self.__delay__ = 1 / 5
        self.__port__ = port
        self.__serial__ = serial.Serial(port, 9600,
                                        exclusive=False, timeout=1)  # open serial port
        self.band = None
        self.blend = None
        self.mute = None
        self.frequency = None
        self.id = None
        self.power = None
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

    """
    Returns an command with crc
    :command: the command to crc without 0x02
    """

    def serial_send(self, message):
        """
        :param message: serial command in bytes to send
        :return: None
        """
        self.__serial__.write(message)
        sleep(self.__delay__)

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

    @staticmethod
    def bytes_to_frequency(freq_bytes):
        if freq_bytes[3] == 94:
            frequency_value = int.from_bytes(freq_bytes[4:6], byteorder='little')
        else:
            frequency_value = int.from_bytes(freq_bytes[3:5], byteorder='little')
        return frequency_value / 100.0  # Frequency is represented in hundredths of MHz

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
                  3:7].decode('ascii')
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
                if response[2] == 45:
                    if response[5] == 2:
                        freq_bytes = bytes([response[3], response[4]])
                    elif response[5] in [35, 38, 39, 42, 94] or (response[3] == 94 and response[4] != 94):
                        freq_bytes = bytes([response[4] - 64, response[5]])
                    else:
                        freq_bytes = bytes([response[4], response[5]])

                    frequency = int.from_bytes(freq_bytes, "little") / 100

                return frequency

        return self.frequency

    def get_blend(self):
        """
        :returns: Blend
        """

        blend = self.serial_query(self.getter.BLEND, responsecode=49)

        if blend[4] == 64:
            self.blend = False
        elif blend[4] == 65:
            self.blend = True
        return self.blend

    def get_mute(self):
        """
        :returns: Blend
        """

        mute = self.serial_query(self.getter.FM_MUTE, responsecode=47)

        if mute[4] == 64:
            self.mute = False
        elif mute[4] == 65:
            self.mute = True
        return self.mute

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

    @staticmethod
    def frequency_to_bytes(frequency):
        """
        Calculcate the frequency in bytes
            :param frequency:
        :return: the frequency in bytes
        """
        freq_int = int(frequency * 100)
        freq_bytes = freq_int.to_bytes(2, byteorder='little')
        return freq_bytes

    @staticmethod
    def crc_calculate(crc_command):
        crc_calc = sum(crc_command) & 0xFF
        crc_calc = (crc_calc ^ 0xFF) + 1
        return bytes([crc_calc])

    def set_frequency_fm(self, frequency):
        """
        Sets the frequency
        :param frequency:
        :return: the set frequency
        """
        bytes_data = self.frequency_to_bytes(frequency=frequency)
        command = bytes([1, 21, 45, bytes_data[0], bytes_data[1]])
        crc = self.crc_calculate(command)

        if bytes_data[0] == 94:
            command = bytes([1, 21, 45, bytes_data[0], bytes_data[0], bytes_data[1]])
            send_command = command + bytes([2]) + crc
        elif bytes_data[0] in [60, 58, 56, 54]:
            command = bytes([1, 21, 45, bytes_data[0], bytes_data[1]])
            send_command = command + bytes([2]) + crc + bytes([94])
        elif bytes_data[0] == 2:
            command = bytes([1, 21, 45, 94, bytes_data[0] + 64, bytes_data[1]])
            send_command = command + bytes([2]) + crc
        else:
            send_command = command + bytes([2]) + crc

        self.serial_send(send_command)
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
        Turns off the LCD
        """

        self.serial_send(self.setter.BRIGHTNESS_OFF)

    def set_display_on(self):
        """
        Turns on the LCD
        """

        self.serial_send(self.setter.BRIGHTNESS_FULL)

    def set_display_dimmed(self):
        """
        Dims on the LCD
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

    def set_blend_on(self):
        """
        Enable FM Blend
        """

        self.serial_send(self.setter.BLEND_ON)
        self.blend = True
        return self.blend

    def set_blend_off(self):
        """
        Disable FM Blend
        """

        self.serial_send(self.setter.BLEND_OFF)
        self.blend = False
        return self.blend

    def set_mute_off(self):
        """
        Disable FM Mute
        """

        self.serial_send(self.setter.FM_MUTE_OFF)
        self.mute = False
        return self.mute

    def set_mute_on(self):
        """
        Disable FM Mute
        """

        self.serial_send(self.setter.FM_MUTE_ON)
        self.mute = False
        return self.mute
