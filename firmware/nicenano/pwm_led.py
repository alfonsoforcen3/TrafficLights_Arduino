"""Boolean LED interface with a validated, fixed PWM on-level."""
import pwmio


class PwmLED:
    def __init__(self, pin, duty_ratio=0.5, frequency=5000):
        ratio = float(duty_ratio)
        if not 0.0 <= ratio <= 1.0:
            raise ValueError('green_brightness must be a finite number between 0 and 1')
        self.max_duty = round(65535 * ratio)
        self._pwm = pwmio.PWMOut(pin, frequency=frequency, duty_cycle=0)
        self._value = False

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = bool(value)
        self._pwm.duty_cycle = self.max_duty if self._value else 0
