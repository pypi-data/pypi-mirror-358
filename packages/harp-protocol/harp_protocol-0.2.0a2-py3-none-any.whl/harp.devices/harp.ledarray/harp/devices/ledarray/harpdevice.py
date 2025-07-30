from dataclasses import dataclass
from enum import Enum, IntFlag

from harp.communication import Device
from harp.protocol import MessageType, PayloadType
from harp.protocol.exceptions import HarpReadException, HarpWriteException
from harp.protocol.messages import HarpMessage


@dataclass
class DigitalOutputSyncPayload:
        # Configuration of the DO0 functionality.
    DO0Sync: DO0SyncConfig
        # Configuration of the DO1 functionality.
    DO1Sync: DO1SyncConfig

@dataclass
class DigitalInputTriggerPayload:
        # Configuration of the DIO input pin.
    DI0Trigger: DigitalInputTriggerConfig
        # Configuration of the DI1 input pin.
    DI1Trigger: DigitalInputTriggerConfig

@dataclass
class PulseModePayload:
        # Sets the pulse mode used in LED0.
    Led0Mode: PulseModeConfig
        # Sets the pulse mode used in LED0
    Led1Mode: PulseModeConfig


class LedState(IntFlag):
    """
    Specifies the LEDs state.

    Attributes
    ----------
    LED0_ON : int
        TODO
    LED1_ON : int
        TODO
    LED0_OFF : int
        TODO
    LED1_OFF : int
        TODO
    """

    NONE = 0x0
    LED0_ON = 0x1
    LED1_ON = 0x2
    LED0_OFF = 0x4
    LED1_OFF = 0x8


class DigitalInputs(IntFlag):
    """
    Specifies the state of port digital input lines.

    Attributes
    ----------
    DI0 : int
        TODO
    DI1 : int
        TODO
    """

    NONE = 0x0
    DI0 = 0x1
    DI1 = 0x2


class AuxDigitalOutputs(IntFlag):
    """
    Specifies the state of the auxiliary digital output lines.

    Attributes
    ----------
    AUX0_SET : int
        TODO
    AUX1_SET : int
        TODO
    AUX0_CLEAR : int
        TODO
    AUX1_CLEAR : int
        TODO
    """

    NONE = 0x0
    AUX0_SET = 0x1
    AUX1_SET = 0x2
    AUX0_CLEAR = 0x4
    AUX1_CLEAR = 0x8


class DigitalOutputs(IntFlag):
    """
    Specifies the state of port digital output lines.

    Attributes
    ----------
    DO0_SET : int
        TODO
    DO1_SET : int
        TODO
    DO0_CLEAR : int
        TODO
    DO1_CLEAR : int
        TODO
    """

    NONE = 0x0
    DO0_SET = 0x1
    DO1_SET = 0x2
    DO0_CLEAR = 0x4
    DO1_CLEAR = 0x8


class LedArrayEvents(IntFlag):
    """
    The events that can be enabled/disabled.

    Attributes
    ----------
    ENABLE_LED : int
        TODO
    DIGITAL_INPUT_STATE : int
        TODO
    """

    NONE = 0x0
    ENABLE_LED = 0x1
    DIGITAL_INPUT_STATE = 0x2


class DO0SyncConfig(Enum):
    """
    Available configurations when using digital output pin 0 to report firmware events.

    Attributes
    ----------
    NONE : int
        TODO
    MIMIC_LED0_ENABLE_POWER : int
        TODO
    MIMIC_LED0_ENABLE_BEHAVIOR : int
        TODO
    MIMIC_LED0_ENABLE_LED : int
        TODO
    """

    NONE = 0
    MIMIC_LED0_ENABLE_POWER = 1
    MIMIC_LED0_ENABLE_BEHAVIOR = 2
    MIMIC_LED0_ENABLE_LED = 3


class DO1SyncConfig(Enum):
    """
    Available configurations when using digital output pin 1 to report firmware events.

    Attributes
    ----------
    NONE : int
        TODO
    MIMIC_LED1_ENABLE_POWER : int
        TODO
    MIMIC_LED1_ENABLE_BEHAVIOR : int
        TODO
    MIMIC_LED1_ENABLE_LED : int
        TODO
    """

    NONE = 0
    MIMIC_LED1_ENABLE_POWER = 16
    MIMIC_LED1_ENABLE_BEHAVIOR = 32
    MIMIC_LED1_ENABLE_LED = 48


class DigitalInputTriggerConfig(Enum):
    """
    Available configurations when using digital inputs as an acquisition trigger.

    Attributes
    ----------
    LED0_ENABLE_POWER : int
        TODO
    LED0_ENABLE_BEHAVIOR : int
        TODO
    LED0_ENABLE_LED : int
        TODO
    LED1_ENABLE_POWER : int
        TODO
    LED1_ENABLE_BEHAVIOR : int
        TODO
    LED1_ENABLE_LED : int
        TODO
    NONE : int
        TODO
    """

    LED0_ENABLE_POWER = 0
    LED0_ENABLE_BEHAVIOR = 1
    LED0_ENABLE_LED = 2
    LED1_ENABLE_POWER = 3
    LED1_ENABLE_BEHAVIOR = 4
    LED1_ENABLE_LED = 5
    NONE = 6


class PulseModeConfig(Enum):
    """
    Available configurations modes when LED behavior is enabled.

    Attributes
    ----------
    PWM : int
        TODO
    PULSE_TIME : int
        TODO
    """

    PWM = 0
    PULSE_TIME = 1


# All available registers for the device as a Enum
class LedArrayRegisters(Enum):
    """Enum for all available registers in the LedArray device.

    Attributes
    ----------
    ENABLE_POWER : int
        Control the enable of both LEDs' power supply.
    ENABLE_LED_MODE : int
        Start/stop the LEDs according to the pulse configuration.
    ENABLE_LED : int
        Enables/disables the LEDs.
    DIGITAL_INPUT_STATE : int
        State of the digital input pins. An event will be emitted when the value of any digital input pin changes.
    DIGITAL_OUTPUT_SYNC : int
        Configuration of the digital outputs behavior.
    DIGITAL_INPUT_TRIGGER : int
        Configuration of the digital inputs pins behavior.
    PULSE_MODE : int
        Sets the pulse mode used by the LEDs.
    LED0_POWER : int
        Sets the power to LED0, between 1 and 120 (arbitrary units).
    LED1_POWER : int
        Sets the power to LED1, between 1 and 120 (arbitrary units).
    LED0_PWM_FREQUENCY : int
        Sets the frequency (Hz) of LED0 when in Pwm mode, between 0.5 and 2000.
    LED0_PWM_DUTY_CYCLE : int
        Sets the duty cycle (%) of LED0 when in Pwm mode, between 0.1 and 99.9.
    LED0_PWM_PULSE_COUNTER : int
        Sets the number of pulses of LED0 when in Pwm mode, between 1 and 65535.
    LED0_PULSE_TIME_ON : int
        Sets the time on (milliseconds) of LED0 when in PulseTime mode, between 1 and 65535.
    LED0_PULSE_TIME_OFF : int
        Sets the time off (milliseconds) of LED0 when in PulseTime mode, between 1 and 65535.
    LED0_PULSE_TIME_PULSE_COUNTER : int
        Sets the number of pulses of LED0 when in PulseTime mode, between 1 and 65535.
    LED0_PULSE_TIME_TAIL : int
        Sets the wait time between pulses (milliseconds) of LED0 when in PulseTime mode, between 1 and 65535.
    LED0_PULSE_REPEAT_COUNTER : int
        Sets the number of repetitions of LED0 pulse protocol when in PulseTime mode, between 1 and 65535.
    LED1_PWM_FREQUENCY : int
        Sets the frequency (Hz) of LED1 when in Pwm mode, between 0.5 and 2000.
    LED1_PWM_DUTY_CYCLE : int
        Sets the duty cycle (%) of LED1 when in Pwm mode, between 0.1 and 99.9.
    LED1_PWM_PULSE_COUNTER : int
        Sets the number of pulses of LED1 when in Pwm mode, between 1 and 65535.
    LED1_PULSE_TIME_ON : int
        Sets the time on (milliseconds) of LED1 when in PulseTime mode, between 1 and 65535.
    LED1_PULSE_TIME_OFF : int
        Sets the time off (milliseconds) of LED1 when in PulseTime mode, between 1 and 65535.
    LED1_PULSE_TIME_PULSE_COUNTER : int
        Sets the number of pulses of LED1 when in PulseTime mode, between 1 and 65535.
    LED1_PULSE_TIME_TAIL : int
        Sets the wait time between pulses (milliseconds) of LED1 when in PulseTime mode, between 1 and 65535.
    LED1_PULSE_REPEAT_COUNTER : int
        Sets the number of repetitions of LED1 pulse protocol when in PulseTime mode, between 1 and 65535.
    LED0_PWM_REAL : int
        Get the real frequency (Hz) of LED0 when in Pwm mode.
    LED0_PWM_DUTY_CYCLE_REAL : int
        Get the real duty cycle (%) of LED0 when in Pwm mode.
    LED1_PWM_REAL : int
        Get the real frequency (Hz) of LED1 when in Pwm mode.
    LED_D1_PWM_DUTY_CYCLE_REAL : int
        Get the real duty cycle (%) of LED1 when in Pwm mode.
    AUX_DIGITAL_OUTPUT_STATE : int
        Write the state of the auxiliary digital output bit.
    AUX_LED_POWER : int
        Sets the power to be applied to auxiliary LED, between 1 and 120.
    DIGITAL_OUTPUT_STATE : int
        Write the state of digital output lines.
    RESERVED0 : int
        Reserved for future use
    ENABLE_EVENTS : int
        Specifies all the active events in the device.
    """
    ENABLE_POWER = 32
    ENABLE_LED_MODE = 33
    ENABLE_LED = 34
    DIGITAL_INPUT_STATE = 35
    DIGITAL_OUTPUT_SYNC = 36
    DIGITAL_INPUT_TRIGGER = 37
    PULSE_MODE = 38
    LED0_POWER = 39
    LED1_POWER = 40
    LED0_PWM_FREQUENCY = 41
    LED0_PWM_DUTY_CYCLE = 42
    LED0_PWM_PULSE_COUNTER = 43
    LED0_PULSE_TIME_ON = 44
    LED0_PULSE_TIME_OFF = 45
    LED0_PULSE_TIME_PULSE_COUNTER = 46
    LED0_PULSE_TIME_TAIL = 47
    LED0_PULSE_REPEAT_COUNTER = 48
    LED1_PWM_FREQUENCY = 49
    LED1_PWM_DUTY_CYCLE = 50
    LED1_PWM_PULSE_COUNTER = 51
    LED1_PULSE_TIME_ON = 52
    LED1_PULSE_TIME_OFF = 53
    LED1_PULSE_TIME_PULSE_COUNTER = 54
    LED1_PULSE_TIME_TAIL = 55
    LED1_PULSE_REPEAT_COUNTER = 56
    LED0_PWM_REAL = 57
    LED0_PWM_DUTY_CYCLE_REAL = 58
    LED1_PWM_REAL = 59
    LED_D1_PWM_DUTY_CYCLE_REAL = 60
    AUX_DIGITAL_OUTPUT_STATE = 61
    AUX_LED_POWER = 62
    DIGITAL_OUTPUT_STATE = 63
    RESERVED0 = 64
    ENABLE_EVENTS = 65


class LedArray(Device):
    """
    LedArray class for controlling the device.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # connect and load already happened in the base class
        # verify that WHO_AM_I matches the expected value
        if self.WHO_AM_I != 1088:
            self.disconnect()
            raise Exception(f"WHO_AM_I mismatch: expected {1088}, got {self.WHO_AM_I}")

    def read_enable_power(self) -> LedState:
        """
        Reads the contents of the EnablePower register.

        Returns
        -------
        LedState
            Value read from the EnablePower register.
        """
        address = 32
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("EnablePower", reply.error_message)

        return reply.payload

    def write_enable_power(self, value: LedState):
        """
        Writes a value to the EnablePower register.

        Parameters
        ----------
        value : LedState
            Value to write to the EnablePower register.
        """
        address = 32
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("EnablePower", reply.error_message)
    def read_enable_led_mode(self) -> LedState:
        """
        Reads the contents of the EnableLedMode register.

        Returns
        -------
        LedState
            Value read from the EnableLedMode register.
        """
        address = 33
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("EnableLedMode", reply.error_message)

        return reply.payload

    def write_enable_led_mode(self, value: LedState):
        """
        Writes a value to the EnableLedMode register.

        Parameters
        ----------
        value : LedState
            Value to write to the EnableLedMode register.
        """
        address = 33
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("EnableLedMode", reply.error_message)
    def read_enable_led(self) -> LedState:
        """
        Reads the contents of the EnableLed register.

        Returns
        -------
        LedState
            Value read from the EnableLed register.
        """
        address = 34
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("EnableLed", reply.error_message)

        return reply.payload

    def write_enable_led(self, value: LedState):
        """
        Writes a value to the EnableLed register.

        Parameters
        ----------
        value : LedState
            Value to write to the EnableLed register.
        """
        address = 34
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("EnableLed", reply.error_message)
    def read_digital_input_state(self) -> DigitalInputs:
        """
        Reads the contents of the DigitalInputState register.

        Returns
        -------
        DigitalInputs
            Value read from the DigitalInputState register.
        """
        address = 35
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("DigitalInputState", reply.error_message)

        return reply.payload

    def read_digital_output_sync(self) -> DigitalOutputSyncPayload:
        """
        Reads the contents of the DigitalOutputSync register.

        Returns
        -------
        DigitalOutputSyncPayload
            Value read from the DigitalOutputSync register.
        """
        address = 36
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("DigitalOutputSync", reply.error_message)

        return reply.payload

    def write_digital_output_sync(self, value: DigitalOutputSyncPayload):
        """
        Writes a value to the DigitalOutputSync register.

        Parameters
        ----------
        value : DigitalOutputSyncPayload
            Value to write to the DigitalOutputSync register.
        """
        address = 36
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("DigitalOutputSync", reply.error_message)
    def read_digital_input_trigger(self) -> DigitalInputTriggerPayload:
        """
        Reads the contents of the DigitalInputTrigger register.

        Returns
        -------
        DigitalInputTriggerPayload
            Value read from the DigitalInputTrigger register.
        """
        address = 37
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("DigitalInputTrigger", reply.error_message)

        return reply.payload

    def write_digital_input_trigger(self, value: DigitalInputTriggerPayload):
        """
        Writes a value to the DigitalInputTrigger register.

        Parameters
        ----------
        value : DigitalInputTriggerPayload
            Value to write to the DigitalInputTrigger register.
        """
        address = 37
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("DigitalInputTrigger", reply.error_message)
    def read_pulse_mode(self) -> PulseModePayload:
        """
        Reads the contents of the PulseMode register.

        Returns
        -------
        PulseModePayload
            Value read from the PulseMode register.
        """
        address = 38
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("PulseMode", reply.error_message)

        return reply.payload

    def write_pulse_mode(self, value: PulseModePayload):
        """
        Writes a value to the PulseMode register.

        Parameters
        ----------
        value : PulseModePayload
            Value to write to the PulseMode register.
        """
        address = 38
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("PulseMode", reply.error_message)
    def read_led0_power(self) -> int:
        """
        Reads the contents of the Led0Power register.

        Returns
        -------
        int
            Value read from the Led0Power register.
        """
        address = 39
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("Led0Power", reply.error_message)

        return reply.payload

    def write_led0_power(self, value: int):
        """
        Writes a value to the Led0Power register.

        Parameters
        ----------
        value : int
            Value to write to the Led0Power register.
        """
        address = 39
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("Led0Power", reply.error_message)
    def read_led1_power(self) -> int:
        """
        Reads the contents of the Led1Power register.

        Returns
        -------
        int
            Value read from the Led1Power register.
        """
        address = 40
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("Led1Power", reply.error_message)

        return reply.payload

    def write_led1_power(self, value: int):
        """
        Writes a value to the Led1Power register.

        Parameters
        ----------
        value : int
            Value to write to the Led1Power register.
        """
        address = 40
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("Led1Power", reply.error_message)
    def read_led0_pwm_frequency(self) -> float:
        """
        Reads the contents of the Led0PwmFrequency register.

        Returns
        -------
        float
            Value read from the Led0PwmFrequency register.
        """
        address = 41
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.Float))
        if reply.is_error:
            raise HarpReadException("Led0PwmFrequency", reply.error_message)

        return reply.payload

    def write_led0_pwm_frequency(self, value: float):
        """
        Writes a value to the Led0PwmFrequency register.

        Parameters
        ----------
        value : float
            Value to write to the Led0PwmFrequency register.
        """
        address = 41
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.Float, value))
        if reply.is_error:
            raise HarpWriteException("Led0PwmFrequency", reply.error_message)
    def read_led0_pwm_duty_cycle(self) -> float:
        """
        Reads the contents of the Led0PwmDutyCycle register.

        Returns
        -------
        float
            Value read from the Led0PwmDutyCycle register.
        """
        address = 42
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.Float))
        if reply.is_error:
            raise HarpReadException("Led0PwmDutyCycle", reply.error_message)

        return reply.payload

    def write_led0_pwm_duty_cycle(self, value: float):
        """
        Writes a value to the Led0PwmDutyCycle register.

        Parameters
        ----------
        value : float
            Value to write to the Led0PwmDutyCycle register.
        """
        address = 42
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.Float, value))
        if reply.is_error:
            raise HarpWriteException("Led0PwmDutyCycle", reply.error_message)
    def read_led0_pwm_pulse_counter(self) -> int:
        """
        Reads the contents of the Led0PwmPulseCounter register.

        Returns
        -------
        int
            Value read from the Led0PwmPulseCounter register.
        """
        address = 43
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("Led0PwmPulseCounter", reply.error_message)

        return reply.payload

    def write_led0_pwm_pulse_counter(self, value: int):
        """
        Writes a value to the Led0PwmPulseCounter register.

        Parameters
        ----------
        value : int
            Value to write to the Led0PwmPulseCounter register.
        """
        address = 43
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("Led0PwmPulseCounter", reply.error_message)
    def read_led0_pulse_time_on(self) -> int:
        """
        Reads the contents of the Led0PulseTimeOn register.

        Returns
        -------
        int
            Value read from the Led0PulseTimeOn register.
        """
        address = 44
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("Led0PulseTimeOn", reply.error_message)

        return reply.payload

    def write_led0_pulse_time_on(self, value: int):
        """
        Writes a value to the Led0PulseTimeOn register.

        Parameters
        ----------
        value : int
            Value to write to the Led0PulseTimeOn register.
        """
        address = 44
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("Led0PulseTimeOn", reply.error_message)
    def read_led0_pulse_time_off(self) -> int:
        """
        Reads the contents of the Led0PulseTimeOff register.

        Returns
        -------
        int
            Value read from the Led0PulseTimeOff register.
        """
        address = 45
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("Led0PulseTimeOff", reply.error_message)

        return reply.payload

    def write_led0_pulse_time_off(self, value: int):
        """
        Writes a value to the Led0PulseTimeOff register.

        Parameters
        ----------
        value : int
            Value to write to the Led0PulseTimeOff register.
        """
        address = 45
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("Led0PulseTimeOff", reply.error_message)
    def read_led0_pulse_time_pulse_counter(self) -> int:
        """
        Reads the contents of the Led0PulseTimePulseCounter register.

        Returns
        -------
        int
            Value read from the Led0PulseTimePulseCounter register.
        """
        address = 46
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("Led0PulseTimePulseCounter", reply.error_message)

        return reply.payload

    def write_led0_pulse_time_pulse_counter(self, value: int):
        """
        Writes a value to the Led0PulseTimePulseCounter register.

        Parameters
        ----------
        value : int
            Value to write to the Led0PulseTimePulseCounter register.
        """
        address = 46
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("Led0PulseTimePulseCounter", reply.error_message)
    def read_led0_pulse_time_tail(self) -> int:
        """
        Reads the contents of the Led0PulseTimeTail register.

        Returns
        -------
        int
            Value read from the Led0PulseTimeTail register.
        """
        address = 47
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("Led0PulseTimeTail", reply.error_message)

        return reply.payload

    def write_led0_pulse_time_tail(self, value: int):
        """
        Writes a value to the Led0PulseTimeTail register.

        Parameters
        ----------
        value : int
            Value to write to the Led0PulseTimeTail register.
        """
        address = 47
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("Led0PulseTimeTail", reply.error_message)
    def read_led0_pulse_repeat_counter(self) -> int:
        """
        Reads the contents of the Led0PulseRepeatCounter register.

        Returns
        -------
        int
            Value read from the Led0PulseRepeatCounter register.
        """
        address = 48
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("Led0PulseRepeatCounter", reply.error_message)

        return reply.payload

    def write_led0_pulse_repeat_counter(self, value: int):
        """
        Writes a value to the Led0PulseRepeatCounter register.

        Parameters
        ----------
        value : int
            Value to write to the Led0PulseRepeatCounter register.
        """
        address = 48
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("Led0PulseRepeatCounter", reply.error_message)
    def read_led1_pwm_frequency(self) -> float:
        """
        Reads the contents of the Led1PwmFrequency register.

        Returns
        -------
        float
            Value read from the Led1PwmFrequency register.
        """
        address = 49
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.Float))
        if reply.is_error:
            raise HarpReadException("Led1PwmFrequency", reply.error_message)

        return reply.payload

    def write_led1_pwm_frequency(self, value: float):
        """
        Writes a value to the Led1PwmFrequency register.

        Parameters
        ----------
        value : float
            Value to write to the Led1PwmFrequency register.
        """
        address = 49
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.Float, value))
        if reply.is_error:
            raise HarpWriteException("Led1PwmFrequency", reply.error_message)
    def read_led1_pwm_duty_cycle(self) -> float:
        """
        Reads the contents of the Led1PwmDutyCycle register.

        Returns
        -------
        float
            Value read from the Led1PwmDutyCycle register.
        """
        address = 50
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.Float))
        if reply.is_error:
            raise HarpReadException("Led1PwmDutyCycle", reply.error_message)

        return reply.payload

    def write_led1_pwm_duty_cycle(self, value: float):
        """
        Writes a value to the Led1PwmDutyCycle register.

        Parameters
        ----------
        value : float
            Value to write to the Led1PwmDutyCycle register.
        """
        address = 50
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.Float, value))
        if reply.is_error:
            raise HarpWriteException("Led1PwmDutyCycle", reply.error_message)
    def read_led1_pwm_pulse_counter(self) -> int:
        """
        Reads the contents of the Led1PwmPulseCounter register.

        Returns
        -------
        int
            Value read from the Led1PwmPulseCounter register.
        """
        address = 51
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("Led1PwmPulseCounter", reply.error_message)

        return reply.payload

    def write_led1_pwm_pulse_counter(self, value: int):
        """
        Writes a value to the Led1PwmPulseCounter register.

        Parameters
        ----------
        value : int
            Value to write to the Led1PwmPulseCounter register.
        """
        address = 51
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("Led1PwmPulseCounter", reply.error_message)
    def read_led1_pulse_time_on(self) -> int:
        """
        Reads the contents of the Led1PulseTimeOn register.

        Returns
        -------
        int
            Value read from the Led1PulseTimeOn register.
        """
        address = 52
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("Led1PulseTimeOn", reply.error_message)

        return reply.payload

    def write_led1_pulse_time_on(self, value: int):
        """
        Writes a value to the Led1PulseTimeOn register.

        Parameters
        ----------
        value : int
            Value to write to the Led1PulseTimeOn register.
        """
        address = 52
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("Led1PulseTimeOn", reply.error_message)
    def read_led1_pulse_time_off(self) -> int:
        """
        Reads the contents of the Led1PulseTimeOff register.

        Returns
        -------
        int
            Value read from the Led1PulseTimeOff register.
        """
        address = 53
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("Led1PulseTimeOff", reply.error_message)

        return reply.payload

    def write_led1_pulse_time_off(self, value: int):
        """
        Writes a value to the Led1PulseTimeOff register.

        Parameters
        ----------
        value : int
            Value to write to the Led1PulseTimeOff register.
        """
        address = 53
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("Led1PulseTimeOff", reply.error_message)
    def read_led1_pulse_time_pulse_counter(self) -> int:
        """
        Reads the contents of the Led1PulseTimePulseCounter register.

        Returns
        -------
        int
            Value read from the Led1PulseTimePulseCounter register.
        """
        address = 54
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("Led1PulseTimePulseCounter", reply.error_message)

        return reply.payload

    def write_led1_pulse_time_pulse_counter(self, value: int):
        """
        Writes a value to the Led1PulseTimePulseCounter register.

        Parameters
        ----------
        value : int
            Value to write to the Led1PulseTimePulseCounter register.
        """
        address = 54
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("Led1PulseTimePulseCounter", reply.error_message)
    def read_led1_pulse_time_tail(self) -> int:
        """
        Reads the contents of the Led1PulseTimeTail register.

        Returns
        -------
        int
            Value read from the Led1PulseTimeTail register.
        """
        address = 55
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("Led1PulseTimeTail", reply.error_message)

        return reply.payload

    def write_led1_pulse_time_tail(self, value: int):
        """
        Writes a value to the Led1PulseTimeTail register.

        Parameters
        ----------
        value : int
            Value to write to the Led1PulseTimeTail register.
        """
        address = 55
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("Led1PulseTimeTail", reply.error_message)
    def read_led1_pulse_repeat_counter(self) -> int:
        """
        Reads the contents of the Led1PulseRepeatCounter register.

        Returns
        -------
        int
            Value read from the Led1PulseRepeatCounter register.
        """
        address = 56
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("Led1PulseRepeatCounter", reply.error_message)

        return reply.payload

    def write_led1_pulse_repeat_counter(self, value: int):
        """
        Writes a value to the Led1PulseRepeatCounter register.

        Parameters
        ----------
        value : int
            Value to write to the Led1PulseRepeatCounter register.
        """
        address = 56
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("Led1PulseRepeatCounter", reply.error_message)
    def read_led0_pwm_real(self) -> float:
        """
        Reads the contents of the Led0PwmReal register.

        Returns
        -------
        float
            Value read from the Led0PwmReal register.
        """
        address = 57
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.Float))
        if reply.is_error:
            raise HarpReadException("Led0PwmReal", reply.error_message)

        return reply.payload

    def read_led0_pwm_duty_cycle_real(self) -> float:
        """
        Reads the contents of the Led0PwmDutyCycleReal register.

        Returns
        -------
        float
            Value read from the Led0PwmDutyCycleReal register.
        """
        address = 58
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.Float))
        if reply.is_error:
            raise HarpReadException("Led0PwmDutyCycleReal", reply.error_message)

        return reply.payload

    def read_led1_pwm_real(self) -> float:
        """
        Reads the contents of the Led1PwmReal register.

        Returns
        -------
        float
            Value read from the Led1PwmReal register.
        """
        address = 59
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.Float))
        if reply.is_error:
            raise HarpReadException("Led1PwmReal", reply.error_message)

        return reply.payload

    def read_led_d1_pwm_duty_cycle_real(self) -> float:
        """
        Reads the contents of the LedD1PwmDutyCycleReal register.

        Returns
        -------
        float
            Value read from the LedD1PwmDutyCycleReal register.
        """
        address = 60
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.Float))
        if reply.is_error:
            raise HarpReadException("LedD1PwmDutyCycleReal", reply.error_message)

        return reply.payload

    def read_aux_digital_output_state(self) -> AuxDigitalOutputs:
        """
        Reads the contents of the AuxDigitalOutputState register.

        Returns
        -------
        AuxDigitalOutputs
            Value read from the AuxDigitalOutputState register.
        """
        address = 61
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("AuxDigitalOutputState", reply.error_message)

        return reply.payload

    def write_aux_digital_output_state(self, value: AuxDigitalOutputs):
        """
        Writes a value to the AuxDigitalOutputState register.

        Parameters
        ----------
        value : AuxDigitalOutputs
            Value to write to the AuxDigitalOutputState register.
        """
        address = 61
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("AuxDigitalOutputState", reply.error_message)
    def read_aux_led_power(self) -> int:
        """
        Reads the contents of the AuxLedPower register.

        Returns
        -------
        int
            Value read from the AuxLedPower register.
        """
        address = 62
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("AuxLedPower", reply.error_message)

        return reply.payload

    def write_aux_led_power(self, value: int):
        """
        Writes a value to the AuxLedPower register.

        Parameters
        ----------
        value : int
            Value to write to the AuxLedPower register.
        """
        address = 62
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("AuxLedPower", reply.error_message)
    def read_digital_output_state(self) -> DigitalOutputs:
        """
        Reads the contents of the DigitalOutputState register.

        Returns
        -------
        DigitalOutputs
            Value read from the DigitalOutputState register.
        """
        address = 63
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("DigitalOutputState", reply.error_message)

        return reply.payload

    def write_digital_output_state(self, value: DigitalOutputs):
        """
        Writes a value to the DigitalOutputState register.

        Parameters
        ----------
        value : DigitalOutputs
            Value to write to the DigitalOutputState register.
        """
        address = 63
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("DigitalOutputState", reply.error_message)
    def read_enable_events(self) -> LedArrayEvents:
        """
        Reads the contents of the EnableEvents register.

        Returns
        -------
        LedArrayEvents
            Value read from the EnableEvents register.
        """
        address = 65
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("EnableEvents", reply.error_message)

        return reply.payload

    def write_enable_events(self, value: LedArrayEvents):
        """
        Writes a value to the EnableEvents register.

        Parameters
        ----------
        value : LedArrayEvents
            Value to write to the EnableEvents register.
        """
        address = 65
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("EnableEvents", reply.error_message)
