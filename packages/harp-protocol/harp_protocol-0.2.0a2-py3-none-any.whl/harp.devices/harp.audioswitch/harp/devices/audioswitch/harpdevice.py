from dataclasses import dataclass
from enum import Enum, IntFlag

from harp.communication import Device
from harp.protocol import MessageType, PayloadType
from harp.protocol.exceptions import HarpReadException, HarpWriteException
from harp.protocol.messages import HarpMessage



class AudioChannels(IntFlag):
    """
    Specifies the available audio output channels.

    Attributes
    ----------
    CHANNEL0 : int
        TODO
    CHANNEL1 : int
        TODO
    CHANNEL2 : int
        TODO
    CHANNEL3 : int
        TODO
    CHANNEL4 : int
        TODO
    CHANNEL5 : int
        TODO
    CHANNEL6 : int
        TODO
    CHANNEL7 : int
        TODO
    CHANNEL8 : int
        TODO
    CHANNEL9 : int
        TODO
    CHANNEL10 : int
        TODO
    CHANNEL11 : int
        TODO
    CHANNEL12 : int
        TODO
    CHANNEL13 : int
        TODO
    CHANNEL14 : int
        TODO
    CHANNEL15 : int
        TODO
    """

    NONE = 0x0
    CHANNEL0 = 0x1
    CHANNEL1 = 0x2
    CHANNEL2 = 0x4
    CHANNEL3 = 0x8
    CHANNEL4 = 0x10
    CHANNEL5 = 0x20
    CHANNEL6 = 0x40
    CHANNEL7 = 0x80
    CHANNEL8 = 0x100
    CHANNEL9 = 0x200
    CHANNEL10 = 0x400
    CHANNEL11 = 0x800
    CHANNEL12 = 0x1000
    CHANNEL13 = 0x2000
    CHANNEL14 = 0x4000
    CHANNEL15 = 0x8000


class DigitalInputs(IntFlag):
    """
    Specifies the state of the digital input pins.

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
    """

    NONE = 0x0
    DI0 = 0x1
    DI1 = 0x2
    DI2 = 0x4
    DI3 = 0x8
    DI4 = 0x10


class AudioSwitchEvents(IntFlag):
    """
    The events that can be enabled/disabled.

    Attributes
    ----------
    ENABLE_CHANNELS : int
        TODO
    DIGITAL_INPUTS_STATE : int
        TODO
    """

    NONE = 0x0
    ENABLE_CHANNELS = 0x1
    DIGITAL_INPUTS_STATE = 0x2


class ControlSource(Enum):
    """
    Available configurations to control the board channels (host computer or digital inputs).

    Attributes
    ----------
    U_S_B : int
        TODO
    DIGITAL_INPUTS : int
        TODO
    """

    U_S_B = 0
    DIGITAL_INPUTS = 1


class DI4TriggerConfig(Enum):
    """
    Available configurations for DI4. Can be used as digital input or as the MSB of the switches address when the SourceControl is configured as DigitalInputs.

    Attributes
    ----------
    INPUT : int
        TODO
    ADDRESS : int
        TODO
    """

    INPUT = 0
    ADDRESS = 1


class DO0SyncConfig(Enum):
    """
    Available configurations when using DO0 pin to report firmware events.

    Attributes
    ----------
    OUTPUT : int
        TODO
    TOGGLE_ON_CHANNEL_CHANGE : int
        TODO
    """

    OUTPUT = 0
    TOGGLE_ON_CHANNEL_CHANGE = 1


# All available registers for the device as a Enum
class AudioSwitchRegisters(Enum):
    """Enum for all available registers in the AudioSwitch device.

    Attributes
    ----------
    CONTROL_MODE : int
        Configures the source to enable the board channels.
    ENABLE_CHANNELS : int
        Enables the audio output channels using a bitmask format. An event will be emitted when any of the channels are enabled.
    DIGITAL_INPUT_STATE : int
        State of the digital input pins. An event will be emitted when the value of any digital input pin changes.
    DO0_STATE : int
        Status of the digital output pin 0.
    RESERVED0 : int
        Reserved for future use.
    DI4_TRIGGER : int
        Configuration of the digital input pin 4 functionality.
    DO0_SYNC : int
        Configuration of the digital output pin 0 functionality.
    ENABLE_EVENTS : int
        Specifies the active events in the device.
    """
    CONTROL_MODE = 32
    ENABLE_CHANNELS = 33
    DIGITAL_INPUT_STATE = 34
    DO0_STATE = 35
    RESERVED0 = 36
    DI4_TRIGGER = 37
    DO0_SYNC = 38
    ENABLE_EVENTS = 39


class AudioSwitch(Device):
    """
    AudioSwitch class for controlling the device.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # connect and load already happened in the base class
        # verify that WHO_AM_I matches the expected value
        if self.WHO_AM_I != 1248:
            self.disconnect()
            raise Exception(f"WHO_AM_I mismatch: expected {1248}, got {self.WHO_AM_I}")

    def read_control_mode(self) -> ControlSource:
        """
        Reads the contents of the ControlMode register.

        Returns
        -------
        ControlSource
            Value read from the ControlMode register.
        """
        address = 32
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("ControlMode", reply.error_message)

        return reply.payload

    def write_control_mode(self, value: ControlSource):
        """
        Writes a value to the ControlMode register.

        Parameters
        ----------
        value : ControlSource
            Value to write to the ControlMode register.
        """
        address = 32
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("ControlMode", reply.error_message)
    def read_enable_channels(self) -> AudioChannels:
        """
        Reads the contents of the EnableChannels register.

        Returns
        -------
        AudioChannels
            Value read from the EnableChannels register.
        """
        address = 33
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("EnableChannels", reply.error_message)

        return reply.payload

    def write_enable_channels(self, value: AudioChannels):
        """
        Writes a value to the EnableChannels register.

        Parameters
        ----------
        value : AudioChannels
            Value to write to the EnableChannels register.
        """
        address = 33
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("EnableChannels", reply.error_message)
    def read_digital_input_state(self) -> DigitalInputs:
        """
        Reads the contents of the DigitalInputState register.

        Returns
        -------
        DigitalInputs
            Value read from the DigitalInputState register.
        """
        address = 34
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("DigitalInputState", reply.error_message)

        return reply.payload

    def read_do0_state(self) -> bool:
        """
        Reads the contents of the DO0State register.

        Returns
        -------
        bool
            Value read from the DO0State register.
        """
        address = 35
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("DO0State", reply.error_message)

        return reply.payload

    def write_do0_state(self, value: bool):
        """
        Writes a value to the DO0State register.

        Parameters
        ----------
        value : bool
            Value to write to the DO0State register.
        """
        address = 35
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("DO0State", reply.error_message)
    def read_di4_trigger(self) -> DI4TriggerConfig:
        """
        Reads the contents of the DI4Trigger register.

        Returns
        -------
        DI4TriggerConfig
            Value read from the DI4Trigger register.
        """
        address = 37
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("DI4Trigger", reply.error_message)

        return reply.payload

    def write_di4_trigger(self, value: DI4TriggerConfig):
        """
        Writes a value to the DI4Trigger register.

        Parameters
        ----------
        value : DI4TriggerConfig
            Value to write to the DI4Trigger register.
        """
        address = 37
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("DI4Trigger", reply.error_message)
    def read_do0_sync(self) -> DO0SyncConfig:
        """
        Reads the contents of the DO0Sync register.

        Returns
        -------
        DO0SyncConfig
            Value read from the DO0Sync register.
        """
        address = 38
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("DO0Sync", reply.error_message)

        return reply.payload

    def write_do0_sync(self, value: DO0SyncConfig):
        """
        Writes a value to the DO0Sync register.

        Parameters
        ----------
        value : DO0SyncConfig
            Value to write to the DO0Sync register.
        """
        address = 38
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("DO0Sync", reply.error_message)
    def read_enable_events(self) -> AudioSwitchEvents:
        """
        Reads the contents of the EnableEvents register.

        Returns
        -------
        AudioSwitchEvents
            Value read from the EnableEvents register.
        """
        address = 39
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("EnableEvents", reply.error_message)

        return reply.payload

    def write_enable_events(self, value: AudioSwitchEvents):
        """
        Writes a value to the EnableEvents register.

        Parameters
        ----------
        value : AudioSwitchEvents
            Value to write to the EnableEvents register.
        """
        address = 39
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("EnableEvents", reply.error_message)
