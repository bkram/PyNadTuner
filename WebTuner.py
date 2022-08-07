import _thread
import os
import time

import cherrypy as http
import jinja2

from NadSerial import Device


class Storage:

    def __init__(self):
        self.standby = None
        self.mute = None
        self.blend = None
        self.rdsps = ''
        self.frequency = 0
        self.rdsrt = {}


class WebTuner:

    def __init__(self):

        if 'TUNER_PORT' in os.environ:
            self.Tuner = Device(os.environ['TUNER_PORT'])
        else:
            self.Tuner = Device()

        self.Storage = Storage()
        self.Tuner.get_device_id()
        _thread.start_new_thread(self.serial_poller, ())
        self.Tuner.serial_send(self.Tuner.getter.POWER)
        self.Tuner.serial_send(self.Tuner.getter.BLEND)
        self.Tuner.serial_send(self.Tuner.getter.FM_MUTE)
        self.Tuner.serial_send(self.Tuner.getter.FM_FREQUENCY)
        self.jinja2 = jinja2.Environment(
            loader=jinja2.FileSystemLoader('templates'))

    def __rds_text__(self):
        result = ''
        for i in sorted(self.Storage.rdsrt):
            result += self.Storage.rdsrt[i].decode(
                'ascii', errors='ignore').replace('^M', '')
        return result

    def serial_poller(self):
        http.log('Serial Poller: Started')
        while 1:
            response = self.Tuner.__read_bytes__()

            if response[2] == 21:
                if response[4] == 64:
                    self.Storage.standby = False
                elif response[4] == 65:
                    self.Storage.standby = True
                http.log('Serial Poller: Power Update: {}'.format(
                    self.Storage.standby))

            if response[1] == 27:
                if response[2] == 2:
                    ps = ''
                    self.Storage.rdsrt = {}
                else:
                    ps = response[2:10].decode('ascii', errors='ignore')
                http.log('Serial Poller: RDS PS Update: {}'.format(ps))
                self.Storage.rdsps = ps

            if response[1] == 28:
                if len(response) == 4:
                    self.Storage.rdsrt = {}
                    http.log('Serial Poller: RDS Text Update Reset')
                else:
                    if response[2] == 94:
                        pos = response[3] - 64
                        content = response[4:][:-2]
                    else:
                        pos = response[2]
                        content = response[3:][:-2]

                    http.log(
                        'Serial Poller: RDS Text Update Position {} Value {}'.format(pos, content))
                    if '^M' in str(response):
                        # TODO: What do we need to do when we get a ^M, for now strip it out in the self.__rds_text__()
                        self.Storage.rdsrt[pos] = content
                    else:
                        self.Storage.rdsrt[pos] = content

            if response[2] == 45:
                if response[5] == 2:
                    freq_bytes = bytes([response[3], response[4]])
                elif response[5] == 39:
                    freq_bytes = bytes([response[4] - 64, response[5]])
                else:
                    freq_bytes = bytes([response[4], response[5]])
                frequency = int.from_bytes(freq_bytes, "little") / 100
                self.Storage.frequency = frequency
                http.log('Serial Poller: Frequency Update: {}'.format(frequency))

            if response[2] == 47:
                if response[4] == 64:
                    self.Storage.mute = False
                elif response[4] == 65:
                    self.Storage.mute = True
                http.log('Serial Poller: Mute Update: {}'.format(
                    self.Storage.mute))

            if response[2] == 49:
                if response[4] == 64:
                    self.Storage.blend = False
                elif response[4] == 65:
                    self.Storage.blend = True
                http.log('Serial Poller: Blend Update: {}'.format(
                    self.Storage.blend))

    @http.expose
    @http.tools.json_out()
    def status(self):

        if self.Storage.blend:
            blend = 'Enabled'
        else:
            blend = 'Disabled'

        if self.Storage.mute:
            mute = 'Enabled'
        else:
            mute = 'Disabled'

        if self.Storage.standby:
            power = 'On'
        else:
            power = 'Off'

        return {'frequency': '{0:.2f} Mhz'.format(self.Storage.frequency),
                'rdsps': self.Storage.rdsps,
                'rdsrt': self.__rds_text__(),
                'blend': blend, 'mute': mute,
                'power': power}

    @http.expose
    def index(self):

        if self.Storage.blend:
            blend = 'checked'
        else:
            blend = ''

        if self.Storage.mute:
            mute = 'checked'
        else:
            mute = ''

        if self.Storage.standby:
            powerstyle = "button-success pure-button"
        else:
            powerstyle = "button-error pure-button"

        template = self.jinja2.get_template('index.html')
        return template.render(tuner=self.Tuner.id, powerstyle=powerstyle,
                               blend=blend, mute=mute)

    @http.expose
    def tuner(self, frequency='', blend='0', mute='0', submit=''):

        # Trigger query actual power status to work around bug in C 425
        self.Tuner.serial_send(self.Tuner.getter.POWER)
        time.sleep(.5)

        if submit == "standby":
            if self.Storage.standby:
                self.Tuner.set_power_off()
                http.log('Power Off')
            else:
                self.Tuner.set_power_on()
                http.log('Power On')

        if mute == 'on':
            http.log('Mute on selected')
            if not self.Storage.mute:
                self.Tuner.set_mute_on()
                http.log('Enable mute')
        else:
            self.Tuner.set_mute_off()
            http.log('Mute is off')

        if blend == 'on':
            http.log('Blend on selected')
            if not self.Storage.blend:
                self.Tuner.set_blend_on()
                http.log('Enable blend')
        else:
            http.log('Blend is off')
            if self.Storage.blend:
                self.Tuner.set_blend_off()
                http.log('Disable blend')

        if frequency:
            if self.Tuner.frequency != float(frequency):
                self.Tuner.set_frequency_fm(frequency=float(frequency))
                http.log('Frequency change to: {}'.format(float(frequency)))

        raise http.HTTPRedirect("/")


if __name__ == "__main__":
    http.config.update({'server.socket_host': "0.0.0.0",
                        'server.socket_port': 8181})
    http.quickstart(WebTuner())
