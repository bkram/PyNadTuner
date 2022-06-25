import _thread

import cherrypy as http

from NadSerial import Device


class Storage:

    def __init__(self):
        self.power = None
        self.mute = None
        self.blend = None
        self.rdsps = ''
        self.frequency = 0
        self.rdsrt = {}


class WebTuner:

    def __init__(self):
        self.Tuner = Device()
        self.Storage = Storage()
        self.Tuner.get_device_id()
        _thread.start_new_thread(self.serial_poller, ())
        self.Tuner.serial_send(self.Tuner.getter.POWER)
        self.Tuner.serial_send(self.Tuner.getter.BLEND)
        self.Tuner.serial_send(self.Tuner.getter.FM_MUTE)
        self.Tuner.serial_send(self.Tuner.getter.FM_FREQUENCY)

    def __rds_text__(self):
        result = ''
        for i in sorted(self.Storage.rdsrt):
            result += self.Storage.rdsrt[i].decode('ascii', errors='ignore').replace('^M', '')
        return result

    def serial_poller(self):
        http.log('Serial Poller: Started')
        while 1:
            response = self.Tuner.__read_bytes__()

            if response[2] == 21:
                if response[4] == 64:
                    self.Storage.power = False
                elif response[4] == 65:
                    self.Storage.power = True
                http.log('Serial Poller: Power Update: {}'.format(
                    self.Storage.power))

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

                    http.log('Serial Poller: RDS Text Update Position {} Value {}'.format(pos, content))

                    # if pos==0:
                        # self.Storage.rdsrt={}
                    if '^M' in str(response):
                        # TODO: What do we need to do when we get a ^M, for now strip it out in the self.__rds_text__()
                        # self.Storage.rdsrt = {}
                        # self.Storage.rdsrt[pos+100] = content
                        self.Storage.rdsrt[pos] = content
                        pass
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

    # @http.expose
    # def test(self):
    #     return open('test.html')

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

        if self.Storage.power:
            power = 'On'
        else:
            power = 'Off'

        return {'frequency': '{0:.2f} Mhz'.format(self.Storage.frequency),
                'rdsps': self.Storage.rdsps,
                'rdsrt': self.__rds_text__(),
                'blend': blend, 'mute': mute,
                'power': power}

    @http.expose
    def rds(self):
        return '{:.2f} : {}'.format(self.Storage.frequency, self.Storage.rdsps)

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

        if self.Storage.power == "On":
            powerstyle = "button-error pure-button"
        else:
            powerstyle = "button-neutral pure-button"

        style = """
<style>
    aside,
    .button-success,
    .button-error,
    .button-neutral {
        color: white;
        border-radius: 4px;
        text-shadow: 0 1px 1px rgba(0, 0, 0, 0.2);
    }

    .button-success {
        background: rgb(28, 184, 65);
    }

    .button-error {
        background: rgb(202, 60, 60);
    }

    .button-neutral {
        background: rgb(59, 70, 228);
    }

    .pure-u-1,
    h1 {
        text-align: center;
    }

    .pure-u-1 {
        padding: 1em;
    }
    aside {
      background: #000;
      padding: .1em 1em;
    }
</style>
"""
        script = """
<script>
var myVar = setInterval(myTimer, 2000);

function myTimer() {
    $.getJSON("/status", function(data) {
        var items = [];
        $.each(data, function(key, val) {
            // console.log(key + " " + val)
            $('#' + key).html(val)
        });
    });
}
</script>
"""

        return """<!DOCTYPE html>
<html lang="EN">

<head>
    <link rel="stylesheet" href="https://unpkg.com/purecss@2.1.0/build/pure-min.css"
     integrity="sha384-yHIFVG6ClnONEA5yB5DJXfW2/KC173DIQrYoZMEtBvGzmf0PKiGyNEqe9N6BNDBH"
     crossorigin="anonymous">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"
     integrity="sha384-vtXRMe3mGCbOeY7l30aIg8H9p3GdeSe4IFlP6G8JMa7o7lXvnz3GFKzPxzJdPfGK"
     crossorigin="anonymous"></script>
    <title>Nad WebTuner</title>
    {}
    {}
</head>
<body>
<div class="pure-g">
    <div class="pure-u-1-3">
    </div>
    <div class="pure-u-1-3">
        <br>
        <aside>
        <p>
            <h1>NAD {} Tuner</h1>
        </p>
        </aside>
        <br>
        <form class="pure-form pure-form-aligned" method="get" action="/tuner">
            <fieldset>
               <legend>Realtime Information</legend>
               <div class="pure-control-group">
                    <label for="aligned-name">Power:</label>
                    <span id="power"></span>
                </div>
                <div class="pure-control-group">
                    <label for="aligned-name">RDS PS:
                    </label>
                    <span id="rdsps"></span>
                </div>
                <div class="pure-control-group">
                    <label for="aligned-name">RDS RT:
                    </label>
                    <span id="rdsrt"></span>
                </div>
                <div class="pure-control-group">
                    <label for="aligned-name">Frequency:
                    </label>
                    <span id="frequency"></span>
                </div>
                <div class="pure-control-group">
                    <label for="aligned-name">Stereo / Mute:</label>
                    <span id="mute"></span>
                </div>                
                <div class="pure-control-group">
                    <label for="aligned-name">Stereo Blend:</label>
                    <span id="blend"></span>
                </div>
                <legend>Update Settings</legend>
                <div class="pure-control-group">
                    <label for="aligned-name">Stereo / Mute:</label>
                    <input type="checkbox" id="aligned-cb-mute" name="mute" {}/>
                </div>
                <div class="pure-control-group">
                    <label for="aligned-name">Stereo Blend:</label>
                    <input type="checkbox" id="aligned-cb-blend" name="blend" {} />
                </div>
                 <div class="pure-control-group">
                    <label for="aligned-name">Set Frequency:</label>
                    <input type="text" id="aligned-name" class="pure-input-rounded"
                    name="frequency" size="2" placeholder="97.2"/>
                </div>
                <div class="pure-controls">
                    <button type="submit" name="submit" value="submit"
                            class="button-success pure-button">Submit
                    </button>
                    <button type="submit" name="submit" value="power"
                            class="{}">Power
                    </button>
                </div>
            </fieldset>
        </form>
    <div class="pure-u-1-3">
    </div>
    </div>
</div>
</body>
</html>
""".format(script, style, self.Tuner.id, mute, blend,
           powerstyle)

    @http.expose
    def tuner(self, frequency='', blend='0', mute='0', submit=''):

        if submit == "power":
            if self.Storage.power:
                http.log('Power Off')
                self.Tuner.set_power_off()
            else:
                http.log('Power On')
                self.Tuner.set_power_on()

        if mute == 'on':
            http.log('Mute on selected')
            if not self.Storage.mute:
                http.log('Enable mute')
                self.Tuner.set_mute_on()
        else:
            http.log('Mute is off')
            self.Tuner.set_mute_off()

        if blend == 'on':
            http.log('Blend on selected')
            if not self.Storage.blend:
                http.log('Enable blend')
                self.Tuner.set_blend_on()
        else:
            http.log('Blend is off')
            if self.Storage.blend:
                http.log('Disable blend')
                self.Tuner.set_blend_off()

        if frequency:
            if self.Tuner.frequency != float(frequency):
                self.Tuner.set_frequency_fm(frequency=float(frequency))
                http.log('Freq change to: {}'.format(float(frequency)))

        raise http.HTTPRedirect("/")


if __name__ == "__main__":
    http.config.update({'server.socket_host': "0.0.0.0",
                        'server.socket_port': 8181})
    http.quickstart(WebTuner())
