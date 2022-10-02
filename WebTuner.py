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
        result = []
        for i in sorted(self.Storage.rdsrt):
            result += self.Storage.rdsrt[i]
        return ''.join(result).replace('^M', '').replace('^@', '')

    def serial_poller(self):

        debug = False
        if debug:
            http.log('Serial Poller: Started')
        while 1:
            response = self.Tuner.__read_bytes__()

            if response[2] == 21:
                if response[4] == 64:
                    self.Storage.standby = False
                elif response[4] == 65:
                    self.Storage.standby = True
                if debug:
                    http.log('Serial Poller: Power Update: {}'.format(
                        self.Storage.standby))

            if response[1] == 27:
                if response[2] == 2:
                    ps = ''
                    self.Storage.rdsrt = {}
                else:
                    ps = response[2:10].decode('ascii', errors='ignore')
                    if debug:
                        http.log('Serial Poller: RDS PS Update: {}'.format(ps))
                self.Storage.rdsps = ps

            if response[1] == 28:
                if len(response) == 4:
                    # self.Storage.rdsrt = {}
                    self.Storage.rdsrt = {0: '    ', 4: '    ', 8: '    ', 12: '    ', 16: '    ', 20: '    ',
                                          24: '    ', 28: '    ', 32: '    ', 36: '    ', 40: '    ', 44: '    ',
                                          48: '    ', 52: '    ', 56: '    ', 60: '    ', 64: '    ', 68: '    ',
                                          72: '    ', 76: '    '}

                    if debug:
                        http.log('Serial Poller: RDS Text Update Reset')
                else:
                    if response[2] == 94:
                        pos = response[3] - 64
                        content = response[4:][:-2]
                    else:
                        pos = response[2]
                        content = response[3:][:-2]
                    if debug:
                        http.log(
                            'Serial Poller: RDS Text Pos {} Test {}'.format(pos, content))
                    # http.log(
                    #     'Serial Poller: RDS Text Update Position {} Value {}'.format(pos, content))
                    #
                    # if '^M' in str(response):
                    #     # TODO: What do we need to do when we get a ^M, for now strip it out in the self.__rds_text__()
                    self.Storage.rdsrt[pos] = content.decode(
                        'ascii', errors='ignore')

            # TODO: frequency around 97.30-97.45 is still wrong
            if response[2] == 45:
                if response[5] == 2:
                    freq_bytes = bytes([response[3], response[4]])
                elif response[5] == 39:
                    freq_bytes = bytes([response[4] - 64, response[5]])
                else:
                    freq_bytes = bytes([response[4], response[5]])
                frequency = int.from_bytes(freq_bytes, "little") / 100
                self.Storage.frequency = frequency
                if debug:
                    http.log('Serial Poller: Frequency Update: {}'.format(frequency))

            if response[2] == 47:
                if response[4] == 64:
                    self.Storage.mute = False
                elif response[4] == 65:
                    self.Storage.mute = True
                if debug:
                    http.log('Serial Poller: Mute Update: {}'.format(
                        self.Storage.mute))

            if response[2] == 49:
                if response[4] == 64:
                    self.Storage.blend = False
                elif response[4] == 65:
                    self.Storage.blend = True
                if debug:
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
            return {'frequency': '{0:.2f} Mhz'.format(self.Storage.frequency),
                    'rdsps': self.Storage.rdsps,
                    'rdsrt': self.__rds_text__(),
                    'blend': blend, 'mute': mute}

    @http.expose
    def index(self):

        if self.Storage.standby:
            powerstyle = "button-error pure-button"
            powertext = "Turn Off"
        else:
            powerstyle = "button-success pure-button"
            powertext = "Turn On"

        template = self.jinja2.get_template('index.html')
        return template.render(tuner=self.Tuner.id, powerstyle=powerstyle, powertext=powertext)

    @http.expose
    def mute(self, mute='0'):
        if mute == 'on':
            http.log('Mute on selected')
            if not self.Storage.mute:
                self.Tuner.set_mute_on()
                http.log('Enable mute')
        else:
            self.Tuner.set_mute_off()
            http.log('Mute is off')

    @http.expose
    def blend(self, blend=''):
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

    @http.expose
    def tuner(self, frequency='', form=''):
        # Trigger query actual power status to work around bug in C 425
        self.Tuner.serial_send(self.Tuner.getter.POWER)
        time.sleep(.5)

        if frequency:
            frequency = frequency.replace(',', '.')
            if self.Tuner.frequency != float(frequency):
                self.Tuner.set_frequency_fm(frequency=float(frequency))
                http.log('Frequency change to: {}'.format(float(frequency)))

        raise http.HTTPRedirect("/")

    @http.expose
    def tune(self, step=''):
        http.log('freq {}'.format(self.Storage.frequency))
        newfreq = self.Storage.frequency + float(step)
        self.Tuner.set_frequency_fm(frequency=newfreq)
        http.log('Frequency step change to: {}'.format(float(newfreq)))


if __name__ == "__main__":
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './public'
        }
    }
    http.config.update({'server.socket_host': "0.0.0.0",
                        'server.socket_port': 8181})
    http.quickstart(WebTuner(), '/', conf)
