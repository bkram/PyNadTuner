from time import sleep
from NadTuner import NadTuner

Tuner = NadTuner()

Tuner.set_power_on()
# # Tuner.set_power_off()


# Tuner.get_device_id()
# Tuner.set_frequency(93.9)
Tuner.set_frequency(106.3)
# #
# from time import sleep
# #
sleep(5)
print(Tuner.get_frequency(force=True))

# print(Tuner.get_rds_ps())
