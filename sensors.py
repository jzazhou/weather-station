import board 
import adafruit_bme680

i2c = board.I2C()

bme688 = adafruit_bme680.Adafruit_BME680_I2C(i2c, address=0x77)

bme688.sea_level_pressure = 1013.25

def air_quality_label(gas_ohms):
    if gas_ohms is None:
        return "-"
    elif gas_ohms > 50000:
        return "Excellent"
    elif gas_ohms > 25000:
        return "Good"
    elif gas_ohms > 10000:
        return "Fair"
    else:
        return "Poor"
    
def read_bme688():
    try: 
        gas = bme688.gas
        return {
            "temp": bme688.temperature,
            "humidity": bme688.relative_humidity,
            "pressure": bme688.pressure,
            "gas": gas,
            "air_quality": air_quality_label(gas),
        }
    except Exception as e:
        print(f"[sensors] BME688 read failed: {e}")
        return None