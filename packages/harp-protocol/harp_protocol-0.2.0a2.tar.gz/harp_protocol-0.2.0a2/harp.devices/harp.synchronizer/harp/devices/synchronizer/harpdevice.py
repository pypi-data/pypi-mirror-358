from dataclasses import dataclass
from enum import Enum, IntFlag

from harp.communication import Device
from harp.protocol import MessageType, PayloadType
from harp.protocol.exceptions import HarpReadException, HarpWriteException
from harp.protocol.messages import HarpMessage



class DigitalInputs(IntFlag):
    """
    Specifies the state of digital input port lines.

    Attributes
    ----------
    DI0 : int
        TODO
    DI1 : int
        TODO
    DI2 : int
        TODO
    DI3 : int
        TODO
    DI4 : int
        TODO
    DI5 : int
        TODO
    DI6 : int
        TODO
    DI7 : int
        TODO
    DI8 : int
        TODO
    """

    NONE = 0x0
    DI0 = 0x1
    DI1 = 0x2
    DI2 = 0x3
    DI3 = 0x4
    DI4 = 0x8
    DI5 = 0x10
    DI6 = 0x20
    DI7 = 0x40
    DI8 = 0x80


class DigitalOutputs(IntFlag):
    """
    Specifies the state of digital output port lines.

    Attributes
    ----------
    DO0 : int
        TODO
    """

    NONE = 0x0
    DO0 = 0x1


class SynchronizerEvents(IntFlag):
    """
    The events that can be enabled/disabled.

    Attributes
    ----------
    DIGITAL_INPUT_STATE : int
        TODO
    """

    NONE = 0x0
    DIGITAL_INPUT_STATE = 0x1


class DigitalInputsSamplingConfig(Enum):
    """
    Available modes for catching/sampling the digital inputs.

    Attributes
    ----------
    NONE : int
        TODO
    INPUTS_CHANGE : int
        TODO
    DI0_RISING_EDGE : int
        TODO
    DI0_FALLING_EDGE : int
        TODO
    SAMPLING100_HZ : int
        TODO
    SAMPLING250_HZ : int
        TODO
    SAMPLING500_HZ : int
        TODO
    SAMPLING1000_HZ : int
        TODO
    SAMPLING2000_HZ : int
        TODO
    """

    NONE = 0
    INPUTS_CHANGE = 1
    DI0_RISING_EDGE = 2
    DI0_FALLING_EDGE = 3
    SAMPLING100_HZ = 4
    SAMPLING250_HZ = 5
    SAMPLING500_HZ = 6
    SAMPLING1000_HZ = 7
    SAMPLING2000_HZ = 8


class DO0ConfigMode(Enum):
    """
    Available configuration for the DO0.

    Attributes
    ----------
    NONE : int
        TODO
    TOGGLE_ON_INPUTS_CHANGE : int
        TODO
    MIMIC_DI0 : int
        TODO
    PULSE5MS_ON_INPUTS_CHANGE : int
        TODO
    PULSE2MS_ON_INPUTS_CHANGE : int
        TODO
    PULSE1MS_ON_INPUTS_CHANGE : int
        TODO
    PULSE500US_ON_INPUTS_CHANGE : int
        TODO
    PULSE250US_ON_INPUTS_CHANGE : int
        TODO
    ANY_INPUTS : int
        TODO
    """

    NONE = 0
    TOGGLE_ON_INPUTS_CHANGE = 1
    MIMIC_DI0 = 2
    PULSE5MS_ON_INPUTS_CHANGE = 3
    PULSE2MS_ON_INPUTS_CHANGE = 4
    PULSE1MS_ON_INPUTS_CHANGE = 5
    PULSE500US_ON_INPUTS_CHANGE = 6
    PULSE250US_ON_INPUTS_CHANGE = 7
    ANY_INPUTS = 8


# All available registers for the device as a Enum
class SynchronizerRegisters(Enum):
    """Enum for all available registers in the Synchronizer device.

    Attributes
    ----------
    DIGITAL_INPUT_STATE : int
        State of the digital input pins. An event will be emitted when the value of any digital input pin changes.
    DIGITAL_OUTPUT_STATE : int
        Status of the digital output pin 0.
    DIGITAL_INPUTS_SAMPLING_MODE : int
        Sets the sampling mode for digital input pins.
    DO0_CONFIG : int
        Configures how the DO0 pin behaves.
    RESERVED0 : int
        Reserved for future use.
    RESERVED1 : int
        Reserved for future use.
    RESERVED2 : int
        Reserved for future use.
    RESERVED3 : int
        Reserved for future use.
    ENABLE_EVENTS : int
        Specifies all the active events in the device.
    """
    DIGITAL_INPUT_STATE = 32
    DIGITAL_OUTPUT_STATE = 33
    DIGITAL_INPUTS_SAMPLING_MODE = 34
    DO0_CONFIG = 35
    RESERVED0 = 36
    RESERVED1 = 37
    RESERVED2 = 38
    RESERVED3 = 39
    ENABLE_EVENTS = 40


class Synchronizer(Device):
    """
    Synchronizer class for controlling the device.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # connect and load already happened in the base class
        # verify that WHO_AM_I matches the expected value
        if self.WHO_AM_I != 1104:
            self.disconnect()
            raise Exception(f"WHO_AM_I mismatch: expected {1104}, got {self.WHO_AM_I}")

    def read_digital_input_state(self) -> DigitalInputs:
        """
        Reads the contents of the DigitalInputState register.

        Returns
        -------
        DigitalInputs
            Value read from the DigitalInputState register.
        """
        address = 32
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("DigitalInputState", reply.error_message)

        return reply.payload

    def read_digital_output_state(self) -> DigitalOutputs:
        """
        Reads the contents of the DigitalOutputState register.

        Returns
        -------
        DigitalOutputs
            Value read from the DigitalOutputState register.
        """
        address = 33
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
        address = 33
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("DigitalOutputState", reply.error_message)
    def read_digital_inputs_sampling_mode(self) -> DigitalInputsSamplingConfig:
        """
        Reads the contents of the DigitalInputsSamplingMode register.

        Returns
        -------
        DigitalInputsSamplingConfig
            Value read from the DigitalInputsSamplingMode register.
        """
        address = 34
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("DigitalInputsSamplingMode", reply.error_message)

        return reply.payload

    def write_digital_inputs_sampling_mode(self, value: DigitalInputsSamplingConfig):
        """
        Writes a value to the DigitalInputsSamplingMode register.

        Parameters
        ----------
        value : DigitalInputsSamplingConfig
            Value to write to the DigitalInputsSamplingMode register.
        """
        address = 34
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("DigitalInputsSamplingMode", reply.error_message)
    def read_do0_config(self) -> DO0ConfigMode:
        """
        Reads the contents of the DO0Config register.

        Returns
        -------
        DO0ConfigMode
            Value read from the DO0Config register.
        """
        address = 35
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("DO0Config", reply.error_message)

        return reply.payload

    def write_do0_config(self, value: DO0ConfigMode):
        """
        Writes a value to the DO0Config register.

        Parameters
        ----------
        value : DO0ConfigMode
            Value to write to the DO0Config register.
        """
        address = 35
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("DO0Config", reply.error_message)
    def read_enable_events(self) -> SynchronizerEvents:
        """
        Reads the contents of the EnableEvents register.

        Returns
        -------
        SynchronizerEvents
            Value read from the EnableEvents register.
        """
        address = 40
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("EnableEvents", reply.error_message)

        return reply.payload

    def write_enable_events(self, value: SynchronizerEvents):
        """
        Writes a value to the EnableEvents register.

        Parameters
        ----------
        value : SynchronizerEvents
            Value to write to the EnableEvents register.
        """
        address = 40
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("EnableEvents", reply.error_message)
