"""
Monitor for Temperature/Humidity ranges
Include some basic logic on how to montior barometric pressure
and determine if a storm is incoming or not.

hector@hectorleiva.com
"""

import time
from adafruit_clue import clue

# Set desired temperature range in degrees Celsius.
min_temperature = 24
max_temperature = 32.2

# Set desired humidity range in percent.
min_humidity = 20
max_humidity = 65

# Current Sea Level - NYC
clue.sea_level_pressure = 100490.0
pressure_lock_val = clue.pressure
initial_time = time.monotonic()

def weatherCheck(currPressure, pressureDiff):
    diffLimit = 338.5 # ((102268.9 - 100914.4) / 4)
    
    if (currPressure > 102268.9):
        if (pressureDiff < (diffLimit * -1)): # There is a significant pressure change heading down
            return 'Fair - Dropping'
        else:
            return 'Fair - Clear'
    elif (currPressure > 100914.4 and currPressure < 102268.9):
        if pressureDiff < (diffLimit * -1):
            return 'Zone - Dropping'
        elif pressureDiff > diffLimit:
            return 'Zone - Rising'
        else:
            return 'Zone - Stable'
    else: # Under 100914.4
        if pressureDiff < (diffLimit * -1):
            return 'Storm - Immeinent'
        elif pressureDiff > diffLimit:
            return 'Storm - Clearing'
        else:
            return 'Storm'

def setSensorTextColor(val, min_val, max_val, display):
    if val < min_val:
        display.color = clue.BLUE
    elif val > max_val:
        display.color = clue.RED
    else:
        display.color = clue.WHITE

# Every 10 minutes, reset the pressure_lock_val to the current pressure value
def pressureCheck(initial_time, pressure_lock_val, current_pressure):
    now = time.monotonic()

    if now - initial_time > 600: # If 600 seconds or 10 minutes have passed
        pressure_lock_val = current_pressure
    else:
        initial_time = now

clue_display = clue.simple_text_display(
    title="Temp & Humidity",
    title_color=(197,229,245), # Colors of weather.gov
    title_scale=1,
    text_scale=2,
    colors=(clue.WHITE,)
)

while True:
    temperature = clue.temperature
    temperature_f = (temperature * 9/5) + 32
    humidity = clue.humidity

    clue_display[0].text = "{:.1f} C | {:.1f} F".format(temperature, temperature_f)
    clue_display[2].text = "Humidity: {:.1f} %".format(humidity)
    clue_display[4].text = "Pres: {:.3f}hPa".format(clue.pressure)
    clue_display[5].text = "Pres. diff: {:.3f}hPA".format(clue.pressure - pressure_lock_val)

    setSensorTextColor(temperature, min_temperature, max_temperature, clue_display[2])
    setSensorTextColor(humidity, min_humidity, max_humidity, clue_display[3])

    pressureCheck(initial_time, pressure_lock_val, clue.pressure)
    clue_display[6].text = weatherCheck(clue.pressure, pressure_lock_val)

    clue_display.show()
