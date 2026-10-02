"""Read the battery ADC without assuming a clone's voltage divider."""
import analogio
import microcontroller
import json
import time

class Battery:
    def __init__(self):
        self.adc = analogio.AnalogIn(microcontroller.pin.P0_04)
        self.cached = None
        self.last = -60
        self.ratio = None
        try:
            with open('/battery_config.json') as config:
                profile = json.load(config)
            ratio = float(profile.get('divider_ratio', 0))
            if profile.get('verified') is True and 1 <= ratio <= 20:
                self.ratio = ratio
        except (OSError, ValueError, TypeError):
            pass

    def sample(self, force=False):
        if not force and self.cached and time.monotonic() - self.last < 60:
            return self.cached
        values = [self.adc.value for _ in range(16)]
        sensor = sum(values) / len(values) / 65535 * self.adc.reference_voltage
        voltage = sensor * self.ratio if self.ratio else None
        valid = voltage is not None and 2.5 <= voltage <= 4.3
        percent = None
        # Approximate resting-voltage curve for a single Li-ion cell, not a fuel gauge.
        curve = ((3.0, 0), (3.4, 5), (3.6, 15), (3.7, 35), (3.8, 55),
                 (3.9, 75), (4.0, 85), (4.1, 95), (4.2, 100))
        if valid:
            percent = 0 if voltage <= 3.0 else 100
            for low, high in zip(curve, curve[1:]):
                if low[0] <= voltage <= high[0]:
                    percent = round(low[1] + (voltage-low[0])/(high[0]-low[0])*(high[1]-low[1]))
                    break
        self.cached = {'sensor_voltage': round(sensor, 4),
                       'voltage': round(voltage, 3) if valid else None,
                       'estimated_percent': percent,
                       'calibrated': self.ratio is not None,
                       'measurement_valid': valid,
                       'charging': None}
        self.last = time.monotonic()
        return self.cached
