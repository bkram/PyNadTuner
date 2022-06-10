import cherrypy as http

from NadTuner import NadTuner


class WebTuner:

    def __init__(self):
        self.Tuner = NadTuner()
        self.Tuner.get_device_id()
        self.Tuner.get_power()
        self.Tuner.get_blend()
        self.Tuner.get_mute()
        self.Tuner.get_frequency_fm()

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

        return """
        <!DOCTYPE html>
        <html lang="EN">

        <head>
            <link rel="stylesheet" href="https://unpkg.com/purecss@1.0.0/build/pure-min.css"
                integrity="sha384-nn4HPE8lTHyVtfCBi5yW9d20FjT8BJwUXyWZT9InLYax14RDjBj46LmSztkmNP9w"
                crossorigin="anonymous">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Nad Tuner Interface</title>
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
                    <form class="pure-form pure-form-aligned" method="get" action="/tuner">
                        <fieldset>
                            <div class="pure-control-group">
                                <label for="aligned-power">Power:</label>{}
                            </div>
                            <div class="pure-control-group">
                                <label for="aligned-name">Frequency</label>
                                <input type="text" id="aligned-name" name="frequency" size="4" value="{:.2f}" />
                            </div>
                            <div class="pure-control-group">
                                <label for="aligned-name">Stereo / Mute</label>
                                <input type="checkbox" id="aligned-cb-mute" name="mute" {} />
                            </div>
                            <div class="pure-control-group">
                                <label for="aligned-name">Stereo Blend</label>
                                <input type="checkbox" id="aligned-cb-blend" name="blend" {} />
                            </div>
                            <div class="pure-controls">
                                <button type="submit" name="submit" value="submit"
                                    class="button-success pure-button">Submit</button>
                                <button type="submit" name="submit" value="power"
                                    class="{}">Power</button>
                            </div>
                        </fieldset>
                    </form>
                </div>
            </div>
        </body>

        </html>
        """.format(style, self.Tuner.id, self.power, self.Tuner.frequency, self.mute, self.blend, powerstyle)

    @http.expose
    def tuner(self, frequency, blend='0', mute='0', power='', submit=''):

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
        else:
            http.log('Freq no change staying at: {}'.format(float(frequency)))

        raise http.HTTPRedirect("/")


if __name__ == "__main__":
    http.config.update({'server.socket_host': "0.0.0.0",
                        'server.socket_port': 8181})
    http.quickstart(WebTuner())
