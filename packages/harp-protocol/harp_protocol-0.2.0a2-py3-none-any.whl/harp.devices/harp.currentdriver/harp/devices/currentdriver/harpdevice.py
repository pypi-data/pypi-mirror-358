from dataclasses import dataclass
from enum import Enum, IntFlag

from harp.communication import Device
from harp.protocol import MessageType, PayloadType
from harp.protocol.exceptions import HarpReadException, HarpWriteException
from harp.protocol.messages import HarpMessage



class DigitalInputs(IntFlag):
    """
    Specifies the state of port digital input lines

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


class DigitalOutputs(IntFlag):
    """
    Specifies the state of port digital output lines

    Attributes
    ----------
    DO0 : int
        TODO
    DO1 : int
        TODO
    """

    NONE = 0x0
    DO0 = 0x1
    DO1 = 0x2


class LedOutputs(IntFlag):
    """
    Specifies the state of LED driver's outputs

    Attributes
    ----------
    L_E_D0 : int
        TODO
    L_E_D1 : int
        TODO
    """

    NONE = 0x0
    L_E_D0 = 0x1
    L_E_D1 = 0x2


class LedRamps(IntFlag):
    """
    Specifies the configuration of LED driver's ramps

    Attributes
    ----------
    L_E_D0_U_P : int
        TODO
    L_E_D0_DO_W_N : int
        TODO
    L_E_D1_U_P : int
        TODO
    L_E_D1_DO_W_N : int
        TODO
    """

    NONE = 0x0
    L_E_D0_U_P = 0x1
    L_E_D0_DO_W_N = 0x2
    L_E_D1_U_P = 0x4
    L_E_D1_DO_W_N = 0x8


class CurrentDriverEvents(IntFlag):
    """
    Specifies the active events in the device.

    Attributes
    ----------
    DIS : int
        TODO
    """

    NONE = 0x0
    DIS = 0x1


# All available registers for the device as a Enum
class CurrentDriverRegisters(Enum):
    """Enum for all available registers in the CurrentDriver device.

    Attributes
    ----------
    DIGITAL_INPUT_STATE : int
        Reflects the state of DI digital lines
    OUTPUT_SET : int
        Set the specified digital output lines
    OUTPUT_CLEAR : int
        Clear the specified digital output lines
    OUTPUT_TOGGLE : int
        Toggle the specified digital output lines
    OUTPUT_STATE : int
        Write the state of all digital output lines
    LED0_CURRENT : int
        Configuration of current to drive LED 0 [0:1000] mA
    LED1_CURRENT : int
        Configuration of current to drive LED 1 [0:1000] mA
    DAC0_VOLTAGE : int
        Configuration of DAC 0 voltage [0:5000] mV
    DAC1_VOLTAGE : int
        Configuration of DAC 1 voltage [0:5000] mV
    LED_ENABLE : int
        Enable driver on the selected output
    LED_DISABLE : int
        Disable driver on the selected output
    LED_STATE : int
        Control the correspondent LED output
    LED0_MAX_CURRENT : int
        Configuration of current to drive LED 0 [0:1000] mA
    LED1_MAX_CURRENT : int
        Configuration of current to drive LED 1 [0:1000] mA
    PULSE_ENABLE : int
        Enables the pulse function for the specified output DACs/LEDs
    PULSE_DUTY_CYCLE_LED0 : int
        Specifies the duty cycle of the output pulse from 1 to 100
    PULSE_DUTY_CYCLE_LED1 : int
        Specifies the duty cycle of the output pulse from 1 to 100
    PULSE_FREQUENCY_LED0 : int
        Specifies the frequency of the output pulse in Hz
    PULSE_FREQUENCY_LED1 : int
        Specifies the frequency of the output pulse in Hz
    RAMP_LED0 : int
        Specifies the ramp time of the transitions between different current/voltage values in milliseconds. The ramp will only work if the pulse function is off
    RAMP_LED1 : int
        Specifies the ramp time of the transitions between different current/voltage values in milliseconds. The ramp will only work if the pulse function is off
    RAMP_CONFIG : int
        Specifies when the ramps are applied for each DAC/LED
    RESERVED0 : int
        Reserved
    RESERVED1 : int
        Reserved
    RESERVED2 : int
        Reserved
    RESERVED3 : int
        Reserved
    ENABLE_EVENTS : int
        Specifies the active events in the device
    """
    DIGITAL_INPUT_STATE = 32
    OUTPUT_SET = 33
    OUTPUT_CLEAR = 34
    OUTPUT_TOGGLE = 35
    OUTPUT_STATE = 36
    LED0_CURRENT = 37
    LED1_CURRENT = 38
    DAC0_VOLTAGE = 39
    DAC1_VOLTAGE = 40
    LED_ENABLE = 41
    LED_DISABLE = 42
    LED_STATE = 43
    LED0_MAX_CURRENT = 44
    LED1_MAX_CURRENT = 45
    PULSE_ENABLE = 46
    PULSE_DUTY_CYCLE_LED0 = 47
    PULSE_DUTY_CYCLE_LED1 = 48
    PULSE_FREQUENCY_LED0 = 49
    PULSE_FREQUENCY_LED1 = 50
    RAMP_LED0 = 51
    RAMP_LED1 = 52
    RAMP_CONFIG = 53
    RESERVED0 = 54
    RESERVED1 = 55
    RESERVED2 = 56
    RESERVED3 = 57
    ENABLE_EVENTS = 58


class CurrentDriver(Device):
    """
    CurrentDriver class for controlling the device.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # connect and load already happened in the base class
        # verify that WHO_AM_I matches the expected value
        if self.WHO_AM_I != 1282:
            self.disconnect()
            raise Exception(f"WHO_AM_I mismatch: expected {1282}, got {self.WHO_AM_I}")

    def read_digital_input_state(self) -> DigitalInputs:
        """
        Reads the contents of the DigitalInputState register.

        Returns
        -------
        DigitalInputs
            Value read from the DigitalInputState register.
        """
        address = 32
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("DigitalInputState", reply.error_message)

        return reply.payload

    def read_output_set(self) -> DigitalOutputs:
        """
        Reads the contents of the OutputSet register.

        Returns
        -------
        DigitalOutputs
            Value read from the OutputSet register.
        """
        address = 33
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("OutputSet", reply.error_message)

        return reply.payload

    def write_output_set(self, value: DigitalOutputs):
        """
        Writes a value to the OutputSet register.

        Parameters
        ----------
        value : DigitalOutputs
            Value to write to the OutputSet register.
        """
        address = 33
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("OutputSet", reply.error_message)
    def read_output_clear(self) -> DigitalOutputs:
        """
        Reads the contents of the OutputClear register.

        Returns
        -------
        DigitalOutputs
            Value read from the OutputClear register.
        """
        address = 34
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("OutputClear", reply.error_message)

        return reply.payload

    def write_output_clear(self, value: DigitalOutputs):
        """
        Writes a value to the OutputClear register.

        Parameters
        ----------
        value : DigitalOutputs
            Value to write to the OutputClear register.
        """
        address = 34
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("OutputClear", reply.error_message)
    def read_output_toggle(self) -> DigitalOutputs:
        """
        Reads the contents of the OutputToggle register.

        Returns
        -------
        DigitalOutputs
            Value read from the OutputToggle register.
        """
        address = 35
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("OutputToggle", reply.error_message)

        return reply.payload

    def write_output_toggle(self, value: DigitalOutputs):
        """
        Writes a value to the OutputToggle register.

        Parameters
        ----------
        value : DigitalOutputs
            Value to write to the OutputToggle register.
        """
        address = 35
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("OutputToggle", reply.error_message)
    def read_output_state(self) -> DigitalOutputs:
        """
        Reads the contents of the OutputState register.

        Returns
        -------
        DigitalOutputs
            Value read from the OutputState register.
        """
        address = 36
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("OutputState", reply.error_message)

        return reply.payload

    def write_output_state(self, value: DigitalOutputs):
        """
        Writes a value to the OutputState register.

        Parameters
        ----------
        value : DigitalOutputs
            Value to write to the OutputState register.
        """
        address = 36
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("OutputState", reply.error_message)
    def read_led0_current(self) -> float:
        """
        Reads the contents of the Led0Current register.

        Returns
        -------
        float
            Value read from the Led0Current register.
        """
        address = 37
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.Float))
        if reply.is_error:
            raise HarpReadException("Led0Current", reply.error_message)

        return reply.payload

    def write_led0_current(self, value: float):
        """
        Writes a value to the Led0Current register.

        Parameters
        ----------
        value : float
            Value to write to the Led0Current register.
        """
        address = 37
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.Float, value))
        if reply.is_error:
            raise HarpWriteException("Led0Current", reply.error_message)
    def read_led1_current(self) -> float:
        """
        Reads the contents of the Led1Current register.

        Returns
        -------
        float
            Value read from the Led1Current register.
        """
        address = 38
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.Float))
        if reply.is_error:
            raise HarpReadException("Led1Current", reply.error_message)

        return reply.payload

    def write_led1_current(self, value: float):
        """
        Writes a value to the Led1Current register.

        Parameters
        ----------
        value : float
            Value to write to the Led1Current register.
        """
        address = 38
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.Float, value))
        if reply.is_error:
            raise HarpWriteException("Led1Current", reply.error_message)
    def read_dac0_voltage(self) -> float:
        """
        Reads the contents of the Dac0Voltage register.

        Returns
        -------
        float
            Value read from the Dac0Voltage register.
        """
        address = 39
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.Float))
        if reply.is_error:
            raise HarpReadException("Dac0Voltage", reply.error_message)

        return reply.payload

    def write_dac0_voltage(self, value: float):
        """
        Writes a value to the Dac0Voltage register.

        Parameters
        ----------
        value : float
            Value to write to the Dac0Voltage register.
        """
        address = 39
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.Float, value))
        if reply.is_error:
            raise HarpWriteException("Dac0Voltage", reply.error_message)
    def read_dac1_voltage(self) -> float:
        """
        Reads the contents of the Dac1Voltage register.

        Returns
        -------
        float
            Value read from the Dac1Voltage register.
        """
        address = 40
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.Float))
        if reply.is_error:
            raise HarpReadException("Dac1Voltage", reply.error_message)

        return reply.payload

    def write_dac1_voltage(self, value: float):
        """
        Writes a value to the Dac1Voltage register.

        Parameters
        ----------
        value : float
            Value to write to the Dac1Voltage register.
        """
        address = 40
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.Float, value))
        if reply.is_error:
            raise HarpWriteException("Dac1Voltage", reply.error_message)
    def read_led_enable(self) -> LedOutputs:
        """
        Reads the contents of the LedEnable register.

        Returns
        -------
        LedOutputs
            Value read from the LedEnable register.
        """
        address = 41
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("LedEnable", reply.error_message)

        return reply.payload

    def write_led_enable(self, value: LedOutputs):
        """
        Writes a value to the LedEnable register.

        Parameters
        ----------
        value : LedOutputs
            Value to write to the LedEnable register.
        """
        address = 41
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("LedEnable", reply.error_message)
    def read_led_disable(self) -> LedOutputs:
        """
        Reads the contents of the LedDisable register.

        Returns
        -------
        LedOutputs
            Value read from the LedDisable register.
        """
        address = 42
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("LedDisable", reply.error_message)

        return reply.payload

    def write_led_disable(self, value: LedOutputs):
        """
        Writes a value to the LedDisable register.

        Parameters
        ----------
        value : LedOutputs
            Value to write to the LedDisable register.
        """
        address = 42
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("LedDisable", reply.error_message)
    def read_led_state(self) -> LedOutputs:
        """
        Reads the contents of the LedState register.

        Returns
        -------
        LedOutputs
            Value read from the LedState register.
        """
        address = 43
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("LedState", reply.error_message)

        return reply.payload

    def write_led_state(self, value: LedOutputs):
        """
        Writes a value to the LedState register.

        Parameters
        ----------
        value : LedOutputs
            Value to write to the LedState register.
        """
        address = 43
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("LedState", reply.error_message)
    def read_led0_max_current(self) -> float:
        """
        Reads the contents of the Led0MaxCurrent register.

        Returns
        -------
        float
            Value read from the Led0MaxCurrent register.
        """
        address = 44
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.Float))
        if reply.is_error:
            raise HarpReadException("Led0MaxCurrent", reply.error_message)

        return reply.payload

    def write_led0_max_current(self, value: float):
        """
        Writes a value to the Led0MaxCurrent register.

        Parameters
        ----------
        value : float
            Value to write to the Led0MaxCurrent register.
        """
        address = 44
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.Float, value))
        if reply.is_error:
            raise HarpWriteException("Led0MaxCurrent", reply.error_message)
    def read_led1_max_current(self) -> float:
        """
        Reads the contents of the Led1MaxCurrent register.

        Returns
        -------
        float
            Value read from the Led1MaxCurrent register.
        """
        address = 45
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.Float))
        if reply.is_error:
            raise HarpReadException("Led1MaxCurrent", reply.error_message)

        return reply.payload

    def write_led1_max_current(self, value: float):
        """
        Writes a value to the Led1MaxCurrent register.

        Parameters
        ----------
        value : float
            Value to write to the Led1MaxCurrent register.
        """
        address = 45
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.Float, value))
        if reply.is_error:
            raise HarpWriteException("Led1MaxCurrent", reply.error_message)
    def read_pulse_enable(self) -> LedOutputs:
        """
        Reads the contents of the PulseEnable register.

        Returns
        -------
        LedOutputs
            Value read from the PulseEnable register.
        """
        address = 46
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("PulseEnable", reply.error_message)

        return reply.payload

    def write_pulse_enable(self, value: LedOutputs):
        """
        Writes a value to the PulseEnable register.

        Parameters
        ----------
        value : LedOutputs
            Value to write to the PulseEnable register.
        """
        address = 46
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("PulseEnable", reply.error_message)
    def read_pulse_duty_cycle_led0(self) -> int:
        """
        Reads the contents of the PulseDutyCycleLed0 register.

        Returns
        -------
        int
            Value read from the PulseDutyCycleLed0 register.
        """
        address = 47
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("PulseDutyCycleLed0", reply.error_message)

        return reply.payload

    def write_pulse_duty_cycle_led0(self, value: int):
        """
        Writes a value to the PulseDutyCycleLed0 register.

        Parameters
        ----------
        value : int
            Value to write to the PulseDutyCycleLed0 register.
        """
        address = 47
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("PulseDutyCycleLed0", reply.error_message)
    def read_pulse_duty_cycle_led1(self) -> int:
        """
        Reads the contents of the PulseDutyCycleLed1 register.

        Returns
        -------
        int
            Value read from the PulseDutyCycleLed1 register.
        """
        address = 48
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("PulseDutyCycleLed1", reply.error_message)

        return reply.payload

    def write_pulse_duty_cycle_led1(self, value: int):
        """
        Writes a value to the PulseDutyCycleLed1 register.

        Parameters
        ----------
        value : int
            Value to write to the PulseDutyCycleLed1 register.
        """
        address = 48
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("PulseDutyCycleLed1", reply.error_message)
    def read_pulse_frequency_led0(self) -> int:
        """
        Reads the contents of the PulseFrequencyLed0 register.

        Returns
        -------
        int
            Value read from the PulseFrequencyLed0 register.
        """
        address = 49
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("PulseFrequencyLed0", reply.error_message)

        return reply.payload

    def write_pulse_frequency_led0(self, value: int):
        """
        Writes a value to the PulseFrequencyLed0 register.

        Parameters
        ----------
        value : int
            Value to write to the PulseFrequencyLed0 register.
        """
        address = 49
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("PulseFrequencyLed0", reply.error_message)
    def read_pulse_frequency_led1(self) -> int:
        """
        Reads the contents of the PulseFrequencyLed1 register.

        Returns
        -------
        int
            Value read from the PulseFrequencyLed1 register.
        """
        address = 50
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("PulseFrequencyLed1", reply.error_message)

        return reply.payload

    def write_pulse_frequency_led1(self, value: int):
        """
        Writes a value to the PulseFrequencyLed1 register.

        Parameters
        ----------
        value : int
            Value to write to the PulseFrequencyLed1 register.
        """
        address = 50
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("PulseFrequencyLed1", reply.error_message)
    def read_ramp_led0(self) -> int:
        """
        Reads the contents of the RampLed0 register.

        Returns
        -------
        int
            Value read from the RampLed0 register.
        """
        address = 51
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("RampLed0", reply.error_message)

        return reply.payload

    def write_ramp_led0(self, value: int):
        """
        Writes a value to the RampLed0 register.

        Parameters
        ----------
        value : int
            Value to write to the RampLed0 register.
        """
        address = 51
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("RampLed0", reply.error_message)
    def read_ramp_led1(self) -> int:
        """
        Reads the contents of the RampLed1 register.

        Returns
        -------
        int
            Value read from the RampLed1 register.
        """
        address = 52
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("RampLed1", reply.error_message)

        return reply.payload

    def write_ramp_led1(self, value: int):
        """
        Writes a value to the RampLed1 register.

        Parameters
        ----------
        value : int
            Value to write to the RampLed1 register.
        """
        address = 52
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("RampLed1", reply.error_message)
    def read_ramp_config(self) -> LedRamps:
        """
        Reads the contents of the RampConfig register.

        Returns
        -------
        LedRamps
            Value read from the RampConfig register.
        """
        address = 53
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("RampConfig", reply.error_message)

        return reply.payload

    def write_ramp_config(self, value: LedRamps):
        """
        Writes a value to the RampConfig register.

        Parameters
        ----------
        value : LedRamps
            Value to write to the RampConfig register.
        """
        address = 53
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("RampConfig", reply.error_message)
    def read_enable_events(self) -> CurrentDriverEvents:
        """
        Reads the contents of the EnableEvents register.

        Returns
        -------
        CurrentDriverEvents
            Value read from the EnableEvents register.
        """
        address = 58
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("EnableEvents", reply.error_message)

        return reply.payload

    def write_enable_events(self, value: CurrentDriverEvents):
        """
        Writes a value to the EnableEvents register.

        Parameters
        ----------
        value : CurrentDriverEvents
            Value to write to the EnableEvents register.
        """
        address = 58
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("EnableEvents", reply.error_message)
