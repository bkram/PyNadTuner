from NadTuner import NadTuner

Tuner = NadTuner()

FREQ_FM = 98

if not Tuner.get_power():
    Tuner.set_power_on()

if not Tuner.get_power() == 'FM':
    Tuner.set_band(band='FM')

freq_fm = Tuner.get_frequency_fm()

if FREQ_FM != freq_fm:
    print(
        'Current frequency {}, setting frequency to {}'.format(freq_fm,
                                                               FREQ_FM,
                                                               ))
    Tuner.set_frequency_fm(FREQ_FM)

Tuner.set_blend_on()
