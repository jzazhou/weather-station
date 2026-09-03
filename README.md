# Weather Station

An always-on desktop weather station built on a Raspberry Pi 4. It reads indoor air conditions from a Bosch BME688 sensor, pulls outdoor weather from the OpenWeatherMap API, and shows both on a small colour LCD.

![The weather station UI](preview.png)

The interface is drawn from scratch using Pillow UI due to outdated Waveshare. 

---

## What it does

**Indoor** — read from the BME688 sensor every 10 seconds:

- Temperature (°C)
- Humidity (%)
- Barometric pressure (hPa)
- Air quality, rated Excellent / Good / Fair / Poor based on the sensor's gas reading

**Outdoor** — fetched from OpenWeatherMap every 10 minutes:

- Temperature and feels-like temperature
- Weather description, with a matching icon
- Wind speed and humidity

**Also:**

- Clock and date
- Timestamps showing when each reading last updated
- Screen dims to 45% brightness between 10pm and 7am
- Starts automatically on boot and runs with no keyboard or monitor attached

---

## Files

| File | What it does |
|---|---|
| `station.py` | Starts everything and runs the main loop |
| `data_store.py` | Holds the latest indoor and outdoor readings |
| `sensors.py` | Reads the BME688 and rates the air quality |
| `weather_api.py` | Calls the OpenWeatherMap API |
| `ui.py` | Draws the whole interface |
| `icons.py` | Draws the weather icons |
| `theme.py` | All the colours and fonts |
| `display.py` | Sends the finished image to the LCD |
| `test_display.py` | Test script for checking the LCD works |
| `fonts/` | Quicksand font files |
| `weather-station.service` | Makes it start on boot |

Three files can be run on their own for testing:

```bash
python weather_api.py   # prints the current outdoor weather
python ui.py            # saves preview.png using fake data
python display.py       # shows colour bars on the LCD
```

---

## Hardware

| Part | Component |
|---|---|
| Computer | Raspberry Pi 4 Model B (2GB), Raspberry Pi OS 64-bit |
| Sensor | Bosch BME688 breakout (Adafruit #5046) |
| Display | Waveshare 3.5" IPS LCD, SPI, 480×320 |
| Storage | 32GB microSD, Class 10 |
| Power | USB-C 5V / 3A |
| Other | Breadboard and jumper wires |

---

## Wiring

These are **physical pin numbers** — counted along the 40-pin header, not GPIO numbers.

### BME688 (I²C)

| BME688 | Pi pin | What it's for |
|---|---|---|
| VIN | 1 | 3.3V power |
| GND | 6 | Ground |
| SDA | 3 | Data |
| SCL | 5 | Clock |

The sensor's address is `0x77`. Run `i2cdetect -y 1` to check it's connected — `77` should appear in the grid.

### Waveshare 3.5" LCD (SPI)

| LCD | Pi pin | What it's for |
|---|---|---|
| VCC | 2 | 5V power |
| GND | 6 | Ground |
| DIN | 19 | Data in |
| CLK | 23 | Clock |
| CS | 24 | Chip select |
| DC | 22 | Data/command |
| RST | 18 | Reset |
| BL | 12 | Backlight |

Both devices share pin 6 for ground. Any of the header's ground pins will work.

---

## Setup

**1. Turn on I²C and SPI.** Both are off by default.

```bash
sudo raspi-config
```

Go to Interface Options, enable I2C, then enable SPI. Then reboot:

```bash
sudo reboot
```

**2. Download the code and install what it needs.**

```bash
git clone https://github.com/jzazhou/weather-station.git ~/weather_station
cd ~/weather_station
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

The `venv` step creates a virtual environment — a separate folder for this project's libraries. Raspberry Pi OS requires this, it won't let you install packages system-wide.

**3. Check the LCD.** The code writes to `/dev/fb0`. Confirm that's where the LCD is:

```bash
ls /dev/fb*
fbset -fb /dev/fb0 -i
```

That should report 480x320. If the LCD turns out to be `/dev/fb1` instead, change `FB_DEVICE` at the top of `display.py`.

Then run `python display.py`. You should see red, green, blue, white, and a gradient.

---

## Configuration

The API key lives in `config.py`, which isn't in this repo. Make your own from the template:

```bash
cp config.example.py config.py
nano config.py
```

| Setting | What it is |
|---|---|
| `OWM_API_KEY` | Your [OpenWeatherMap](https://openweathermap.org/api) key (free tier is fine) |
| `CITY_NAME` | City for outdoor weather |
| `COUNTRY_CODE` | Country code, like `"US"` |
| `UNITS` | `"metric"` for °C |
| `SENSOR_INTERVAL` | Seconds between sensor reads (10) |
| `API_INTERVAL` | Seconds between API calls (600) |

A brand new API key can take a couple of hours to start working. If you get a `401` error right after signing up, that's usually why.

---

## Running it

To run it yourself and watch the output:

```bash
source venv/bin/activate
python station.py
```

To make it start on boot and restart itself if it crashes:

```bash
sudo cp weather-station.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable weather-station
sudo systemctl start weather-station
```

Useful commands after that:

```bash
systemctl status weather-station      # is it running?
journalctl -u weather-station -f      # watch the log
```

The service file assumes the project is at `/home/pi/weather_station` and the user is `pi`. If yours is different, edit those paths in `weather-station.service`.

---

## Design notes

**Three jobs running at the same time.** Reading the sensor, calling the API, and drawing the screen all happen at once rather than one after another. This matters because the API call can take up to 10 seconds when the network is slow — long enough to freeze the clock if the screen had to wait for it. The sensor and the API each run in their own thread and drop their results into a shared `DataStore`. That store uses a lock, so the drawing code never reads a value while it's halfway through being written.

**Only redrawing when something changes.** The main loop checks 10 times a second, but drawing a frame means building a whole new 480×320 image and sending 307,200 bytes to the screen. Most of the time nothing has actually changed — the clock only shows hours and minutes, so it updates once a minute. Before drawing, the loop compares the current minute and the two update timestamps against the last frame it drew. If they match, the new frame would look identical, so it skips it. That's about 3 redraws a minute instead of 600.

**Writing straight to the screen.** On Linux, the display is a file: `/dev/fb0`. Whatever bytes you write to it become pixels. Pillow makes images with 3 bytes per pixel, but the LCD's controller wants 2 bytes per pixel in a format called RGB565 — 5 bits of red, 6 of green, 5 of blue. `display.py` converts between them with bit shifts, using NumPy so all 153,600 pixels are converted at once instead of in a loop. Doing it this way means the Pi needs no desktop environment at all.

---

Built by a first-year Electrical and Computer Engineering student at Cornell University.
