import pandas as pd
import board
from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import neopixel
import time
import math

def strToInt(string, pressure=''):
    step1 = float(string) * 33.86 if pressure == 'hpa' else float(string)
    return 0 if math.isnan(step1) else math.floor(step1)


def oledMETAR(display, airport, flight_category, obs_time, wind_speed, wind_dir, temp, dewpoint, pressure):
    
    print('Inside oledMETAR')
    width = disp.width
    height = disp.height
    
    x = 0
    image = Image.new("1", (width, height))
    draw = ImageDraw.Draw(image)
	# Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf', 16)
    mediumFont = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf', 14)
    smallFont = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 10)

    draw.text((x, 0), f"{airport} {flight_category}", font=font, fill=255)
    draw.text((x + 90, 2), f"{obs_time[11:16]}Z", font=smallFont, fill=255)
    draw.text((x, 18), f"{strToInt(wind_speed)}/{strToInt(wind_dir)} {strToInt(temp)}/{strToInt(dewpoint)}C", font=font, fill=255)
    draw.text((x, 36), f"Q{strToInt(pressure, 'hpa')}", font=font, fill=255)

    disp.image(image)
    disp.show()


LED_PIN			= board.D18		# GPIO pin connected to the pixels (18 is PCM).
PIXEL_ORDER		= neopixel.RGB		# Strip type and colour ordering
# LED_PIN = 1
# PIXEL_ORDER = 'GRB'

COLOUR_DICT = {
    'VFR'  : (255,0,0),
    'MVFR' : (0,0,255),
    'IFR'  : (0,255,0),
    'LIFR' : (0,125,125),
    'LIGHTNING' : (255,255,255),
    'HIGH_WINDS' : (255,255,0),
    'OFF' : (0,0,0)
}

WIND_KTS = 15
HIGH_WIND_KTS = 25

LOOP_TIME = 300 # time in seconds (roughly) for LED loop to run

# Read in list of airports
file = open('airports.txt', 'r')
with file as f:
    airports = [line.rstrip() for line in f]
file.close()

pixels = neopixel.NeoPixel(LED_PIN, len(airports), brightness = 0.2, pixel_order = PIXEL_ORDER, auto_write = False)

i2c = busio.I2C(SCL, SDA)
disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
disp.poweron()

try:

    df = pd.read_csv('https://www.aviationweather.gov/adds/dataserver_current/current/metars.cache.csv.gz', compression='gzip', skiprows=5)

    airport_metar_df = df[df['station_id'].isin(airports)][['station_id', 'observation_time', 'temp_c', 'dewpoint_c', 'wind_dir_degrees', 'wind_speed_kt', 'wind_gust_kt', 'altim_in_hg', 'wx_string', 'flight_category']].copy().reset_index()

    # Need to flash on/off or yellow during wind cycle
    wind_cycle = False
    loop_time = LOOP_TIME
    displayLoopTimer = 0
    displayAirport = 0

    while loop_time > 0:
        # keep track of LED number
        i = 0
        for a in airports:
            colour = COLOUR_DICT['OFF']
            a_metar = airport_metar_df.loc[airport_metar_df.station_id == a].copy()
            #print(a_metar)
            if len(a_metar) == 1:
                # Work out correct colour
                flight_category = a_metar.flight_category.values[0]
                if flight_category in COLOUR_DICT.keys() :
                    colour = COLOUR_DICT[flight_category]
                if wind_cycle:
                    # Adjust colours only on wind cycle AND if it is windy!
                    #print(a_metar.wx_string.isnull().values[0])
                    lightning_list = ['TS', 'LTG', 'VCTS']
                    if not a_metar.wx_string.isnull().values[0] :
                        if any(x in a_metar.wx_string.values[0] for x in lightning_list) :
                            print('Lightning')
                            colour = COLOUR_DICT['LIGHTNING']
                    elif not a_metar.wind_gust_kt.isnull().values[0] :
                        colour = COLOUR_DICT['HIGH_WINDS']
                    elif not a_metar.wind_speed_kt.isnull().values[0] :
                        if a_metar.wind_speed_kt.values[0] > HIGH_WIND_KTS :
                            colour = COLOUR_DICT['HIGH_WINDS']
                        elif a_metar.wind_speed_kt.values[0] > WIND_KTS :
                            colour = COLOUR_DICT['OFF']

            print(f"Airport {a} and flight_category is {flight_category}. Setting LED {i} for {a} to {colour}")

            pixels[i] = colour
            i += 1

        pixels.show()
        time.sleep(2)
        wind_cycle = False if wind_cycle else True
        loop_time -= 1

        if displayLoopTimer == 0:
            displayLoopTimer = 4
            print(f"Checking index number {displayAirport}")
            metar = airport_metar_df.iloc[displayAirport]
            displayAirport += 1
            displayAirport = 0 if displayAirport == len(airport_metar_df) else displayAirport
            print(f"displayAirport value is {displayAirport}")
            oledMETAR(disp, metar['station_id'], metar['flight_category'], metar['observation_time'], metar['wind_speed_kt'], metar['wind_dir_degrees'], metar['temp_c'], metar['dewpoint_c'], metar['altim_in_hg'])

        displayLoopTimer -= 1

finally:
    for i in range(len(airports)):
        pixels[i] = COLOUR_DICT['OFF']
    pixels.show()

    disp.fill(0)
    disp.show()
    disp.poweroff()

