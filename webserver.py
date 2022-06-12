import _thread

import cherrypy as http

from NadTuner import NadTuner


class Storage:

    def __init__(self):
        self.rdsps = 'No RDS PS'
        self.frequency = 0


class WebTuner:

    def __init__(self):
        self.Tuner = NadTuner()
        self.Storage = Storage()

        self.Tuner.get_device_id()
        self.Tuner.get_power()
        self.Tuner.get_blend()
        self.Tuner.get_mute()
        self.Tuner.get_frequency_fm()
        self.Storage.frequency = self.Tuner.frequency

        if self.Tuner.blend:
            self.blend = 'checked'
        else:
            self.blend = ''

        if self.Tuner.mute:
            self.mute = 'checked'
        else:
            self.mute = ''
        if self.Tuner.power:
            self.power = 'On'
        else:
            self.power = 'Off'

        _thread.start_new_thread(self.serial_poller, ())

    def serial_poller(self):
        http.log('Serial Poller: Started')
        while 1:
            response = self.Tuner.__read_bytes__()

            if response[1] == 27:
                if response[2] == 2:
                    ps = 'No RDS PS'
                else:
                    ps = response[2:10].decode('utf-8', errors='ignore')
                http.log('Serial Poller: RDS PS Update: {}'.format(ps))
                self.Storage.rdsps = ps

            if response[2] == 45:
                print(response)
                if response[5] == 2:
                    freq_bytes = bytes([response[3], response[4]])
                elif response[5] == 39:
                    freq_bytes = bytes([response[4] - 64, response[5]])
                else:
                    freq_bytes = bytes([response[4], response[5]])
                frequency = int.from_bytes(freq_bytes, "little") / 100
                self.Storage.frequency = frequency
                http.log('Serial Poller: Frequency Update: {}'.format(frequency))

    # @http.expose
    # def test(self):
    #     return open('test.html')

    @http.expose
    @http.tools.json_out()
    def status(self):
        return {'frequency': self.Storage.frequency, 'rdsps': self.Storage.rdsps}

    @http.expose
    def rds(self):
        return '{:.2f} : {}'.format(self.Storage.frequency, self.Storage.rdsps)

    @http.expose
    def index(self):

        if self.power == "On":
            powerstyle = "button-error pure-button"
        else:
            powerstyle = "button-neutral pure-button"

        style = """
<style>
    .button-success,
    .button-error,
    .button-neutral {
        color: white;
        border-radius: 4px;
        text-shadow: 0 1px 1px rgba(0, 0, 0, 0.2);
    }

    .button-success {
        background: rgb(28, 184, 65);
        /* this is a green */
    }

    .button-error {
        background: rgb(202, 60, 60);
        /* this is a maroon */
    }

    .button-neutral {
        background: rgb(59, 70, 228);
        /* this is a maroon */
    }

    .pure-u-1,
    h1 {
        text-align: center;
    }

    .pure-u-1 {
        padding: 1em;
    }
</style>
"""
        script = """
<script>
var myVar = setInterval(myTimer, 1000);

function myTimer() {
    $.getJSON("/status", function(data) {
        var items = [];
        $.each(data, function(key, val) {
            console.log(key + " " + val)
            $('#' + key).html(val)
        });
    });
}
</script>
        """

        return """
<!DOCTYPE html>
<html lang="EN">

<head>
    <link rel="stylesheet" href="https://unpkg.com/purecss@1.0.0/build/pure-min.css"
        integrity="sha384-nn4HPE8lTHyVtfCBi5yW9d20FjT8BJwUXyWZT9InLYax14RDjBj46LmSztkmNP9w"
        crossorigin="anonymous">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
    <title>Nad Tuner Interface</title>
    {}
    {}
</head>
<body>
<div class="pure-g">
    <div class="pure-u-1-3">
    </div>
    <div class="pure-u-1-3">
        <div style="background-color:teal">
            <h1> Tuner {}</h1>
        </div>
        <!--        <div id="rdsps"></div>-->
        <form class="pure-form pure-form-aligned" method="get" action="/tuner">
            <fieldset>
               <div class="pure-control-group">
                    <label for="aligned-name">Power:</label>
                    <span>{}</span>
                </div>
                <div class="pure-control-group">
                    <label for="aligned-name">RDS PS
                    </label>
                    <span id="rdsps"></span>
                </div>
                <div class="pure-control-group">
                    <label for="aligned-name">Frequency
                    </label>
                    <span id="frequency"></span>
                </div>
                <div class="pure-control-group">
                    <label for="aligned-name">Stereo / Mute</label>
                    <input type="checkbox" id="aligned-cb-mute" name="mute" {}/>
                </div>
                <div class="pure-control-group">
                    <label for="aligned-name">Stereo Blend</label>
                    <input type="checkbox" id="aligned-cb-blend" name="blend" {} />
                </div>
                 <div class="pure-control-group">
                    <label for="aligned-name">Set Frequency</label>
                    <input type="text" id="aligned-name" name="frequency" size="4" value="{}"/>
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
    </div>
</div>
</body>
</html>
""".format(script, style, self.Tuner.id,  self.power, self.mute, self.blend, self.Tuner.frequency,
           powerstyle)

    @http.expose
    def tuner(self, frequency, blend='0', mute='0', submit=''):

        if submit == "power":
            if self.power == 'On':
                http.log('Power Off')
                self.power = 'Off'
                self.Tuner.set_power_off()
            else:
                http.log('Power On')
                self.power = 'On'
                self.Tuner.set_power_on()
        if mute == 'on':
            http.log('Mute is on')
            if not self.mute:
                http.log('Enable mute')
                self.mute = 'checked'
                self.Tuner.set_mute_on()
        else:
            http.log('Mute is off')
            self.mute = ''
            self.Tuner.set_mute_off()

        if blend == 'on':
            http.log('Blend is on')
            if not self.blend:
                http.log('Enable blend')
                self.Tuner.set_blend_on()
                self.blend = 'checked'
        else:
            http.log('Blend is off')
            if self.blend:
                http.log('Disable blend')
                self.Tuner.set_blend_off()
                self.blend = ''

        if self.Tuner.frequency != float(frequency):
            self.Tuner.set_frequency_fm(frequency=float(frequency))
            http.log('Freq change to: {}'.format(float(frequency)))
            self.Storage.rdsps = 'No RDS PS'

        else:
            http.log('Freq no change staying at: {}'.format(float(frequency)))

        raise http.HTTPRedirect("/")


if __name__ == "__main__":
    http.config.update({'server.socket_host': "0.0.0.0",
                        'server.socket_port': 8181})
    http.quickstart(WebTuner())
